import csv
import json
import os
import math

round_to_n = lambda x, n: x if x == 0 else round(x, -int(math.floor(math.log10(abs(x)))) + (n - 1))

def parse_value(ciqual_nutrient):
    if not ciqual_nutrient or ciqual_nutrient == '-':
        return 0
    return float(ciqual_nutrient.replace(',','.').replace('<','').replace('traces','0'))

# Load Ciqual data
max_values = {}
ciqual_ingredients = {}
filename = os.path.join(os.path.dirname(__file__), "Ciqual.csv.0")
with open(filename, newline="", encoding="utf8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        values = list(row.values())
        keys = list(row.keys())
        for i in range(9,len(values)):
            value = parse_value(values[i])
            row[keys[i]] = value
            max_values[keys[i]] = max(max_values.get(keys[i], 0), value)
        ciqual_ingredients[row["alim_code"]] = row

# print(ciqual_ingredients['42501'])

# Load OFF Ciqual Nutrient mapping
off_to_ciqual = {}
ciqual_to_off = {}
filename = os.path.join(os.path.dirname(__file__), "nutrient_map.csv")
with open(filename, newline="", encoding="utf8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if row["ciqual_id"]:
            # Normalise units. OFF units are generally g so need to convert to the
            # Ciqual unit for comparison
            factor = 1.0
            ciqual_unit = row['ciqual_unit']
            if ciqual_unit == 'mg':
                factor = 1000.0
            elif ciqual_unit == 'µg':
                factor = 1000000.0
            row['factor'] = factor
            off_to_ciqual[row["off_id"]] = row
            ciqual_to_off[row["ciqual_id"]] = row

# Load ingredients
filename = os.path.join(os.path.dirname(__file__), "ingredients.json")
with open(filename, "r", encoding="utf-8") as ingredients_file:
    ingredients_taxonomy = json.load(ingredients_file)


def get_ciqual_code(ingredient_id):
    ingredient = ingredients_taxonomy.get(ingredient_id, None)
    if ingredient is None:
        print(ingredient_id + ' not found')
        return None

    ciqual_code = ingredient.get('ciqual_food_code', None)
    if ciqual_code:
        return ciqual_code['en']

    parents = ingredient.get('parents', None)
    if parents:
        for parent_id in parents:
            ciqual_code = get_ciqual_code(parent_id)
            if ciqual_code:
                print('Obtained ciqual_code from ' + parent_id)
                return ciqual_code

    return None


def setup_ingredients(ingredients):
    for ingredient in ingredients:
        if ('ingredients' in ingredient):
            # Child ingredients
            setup_ingredients(ingredient['ingredients'])

        else:
            ciqual_code = ingredient.get('ciqual_food_code')
            if (ciqual_code is None):
                ciqual_code = get_ciqual_code(ingredient['id'])

            # Convert CIQUAL nutrient codes back to OFF
            ingredient_nutrients = {}
            ciqual_ingredient = ciqual_ingredients.get(ciqual_code, None)
            if (ciqual_ingredient is None):
                # Invent a dummy set of nutrients with maximum ranges
                # Use max values that occur in acual data
                for off_id in off_to_ciqual:
                    max_value = max_values[off_to_ciqual[off_id]['ciqual_id']]
                    ingredient_nutrients[off_id] = {'percent_min': 0, 'percent_max': max_value}
            else:
                for ciqual_key in ciqual_ingredient:
                    nutrient = ciqual_to_off.get(ciqual_key)
                    if (nutrient is not None):
                        value = ciqual_ingredient[ciqual_key] / nutrient['factor']
                        # TODO Get range data from CIQUAL values
                        ingredient_nutrients[nutrient['off_id']] = {'percent_min': value, 'percent_max': value}

            ingredient['nutrients'] = ingredient_nutrients


def prepare_product(product):
    setup_ingredients(product['ingredients'])



# Dump ingredients
#with open(filename, "w", encoding="utf-8") as ingredients_file:
#    json.dump(
#        ingredients, ingredients_file, sort_keys=True, indent=4, ensure_ascii=False
#    )
