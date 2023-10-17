#!/usr/bin/python3
"""
compute_metrics_for_model_on_test_sets [path of model results] [paths of one or more input test sets]

This scriptwill go through each product JSON file of the specified input test sets to:
- Compute accuracy metrics comparing the estimated "percent_estimate" field in the resulting product
to the "percent" field in the input product
- Store product level metrics in the resulting product
- Aggregate metrics by test set
"""

import json
import sys
import os

def compare_input_ingredients_to_resulting_ingredients(input_ingredients, resulting_ingredients):
    # Compute difference metrics for each ingredient and nested sub ingredient comparing the input percent to the resulting percent_estimate

    total_difference = 0

    for i, input_ingredient in enumerate(input_ingredients):
        resulting_ingredient = resulting_ingredients[i]
        # We compute metrics for known percent in the input product
        if "percent" in input_ingredient:
            input_percent = input_ingredient["percent"]
            # If the resulting ingredient does not have a percent_estimate, we set it to 0 for metrics computation
            if "percent_estimate" in resulting_ingredient:
                resulting_percent_estimate = resulting_ingredient["percent_estimate"]
            else
                resulting_percent_estimate = 0
                
            difference = abs(resulting_percent_estimate - input_percent)
            # Store the difference at the ingredient level
            resulting_ingredient["difference"] = difference
            total_difference += difference
        
        # Compare sub ingredients if any
        if "ingredients" in input_ingredients:
            input_sub_ingredients = input_ingredient["ingredients"]
            resulting_sub_ingredients = resulting_ingredient["ingredients"]
            total_difference += compare_input_ingredients_to_resulting_ingredients(input_sub_ingredients, resulting_sub_ingredients)

    return total_difference

def compare_input_product_to_resulting_product(input_product, resulting_product):
    
    compare_input_ingredients_to_resulting_ingredients(input_ingredients, resulting_ingredients)

    resulting_product["ingredients_metrics"] = ["total_difference": total_difference]

    pass

# Go through each input test set directory
for test_set_path in sys.argv[3:]:

    # Test set name is the last component of the test set path
    test_set_name = test_set_path.split("/")[-1]

    # Go through each JSON file in the input test set directory
    for path in [test_set_path + "/" + f for f in os.listdir(test_set_path) if f.endswith(".json")]:

        # Read the input product
        with open(path, "r") as f:
            input_product = json.load(f)

        # Read the corresponding resulting product

        # test name is the last component of the path
        test_name = path.split("/")[-1]

        # Pretty save the resulting JSON structure over the input file for easy inspection of diffs
        result_path = results_path + "/" + test_set_name + "/" + test_name
        with open(result_path, "r") as f:
            resulting_product = json.load(f)

        # Compute accuracy metrics comparing the estimated "percent_estimate" field in the resulting product
        # to the "percent" field in the input product
        compare_input_product_to_resulting_product(input_product, resulting_product)

        # Store product level metrics in the resulting product
        with open(result_path, "w") as f:
            print("Saving metrics in result: " + result_path)
            json.dump(resulting_product, f, indent=4)
