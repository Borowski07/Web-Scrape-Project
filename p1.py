#%%
import pandas as pd
import re

# Read product information from CSV file
product_df = pd.read_csv('web-scrape-export_2023-04-03.csv')
if 'Ingredients' not in product_df.columns:
    print("Warning: No 'Ingredients' column found in the product information CSV file.")
    exit()

# Read poison ingredients from CSV files
poison_df = pd.read_csv('poison_list.csv', encoding='iso-8859-1')
# Create a set of poisonous substances for faster lookup
poison_set = set(poison_df['poison'].str.lower())

# Compile regular expressions for checking ingredient names against poisons
poison_regexes = [re.compile(rf"\b{re.escape(p)}\b") for p in poison_set]

# Define a function to check if a product is safe
def is_safe(ingredients):
    if pd.isna(ingredients):
        # If ingredients is NaN, convert it to an empty string
        ingredients = ""
    elif not isinstance(ingredients, str):
        # If ingredients is not a string, convert it to a string
        ingredients = str(ingredients)
    for ingredient in ingredients.split(","):
        ingredient = ingredient.strip()  # Remove leading/trailing spaces
        # Check if the ingredient name exactly matches a poison in the poison set
        if ingredient.lower() in poison_set:
            return False
        # Check if any variation of the ingredient name is a match to a poison in the poison set
        if any(regex.search(ingredient.lower()) for regex in poison_regexes):
            return False
    return True

# Create a new column 'is_safe' based on whether the product is safe or not
product_df['is_safe'] = product_df['Ingredients'].apply(is_safe)

# Output the decision of whether a product is safe or not
for index, row in product_df.iterrows():
    if pd.isna(row['Ingredients']):
        print(f"{row['Name']}\n  Warning!! No ingredients so wait for the verification.")
    elif row['is_safe']:
        print(f"Product {row['Name']}\n This product does not contain poison and is safe for use.")
    else:
        print(f"Product {row['Name']}\n Warning!! This product contains poison and is not safe for use.")

# %%
