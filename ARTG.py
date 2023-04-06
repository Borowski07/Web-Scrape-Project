import pandas as pd

# Read product information CSV file into a pandas DataFrame
product_info = pd.read_csv('artg/product_info.csv')

# Read ARTG list CSV file into a pandas DataFrame
artg_list = pd.read_csv('artg/artg_list.csv')

# Extract the set of unique manufacturers from the ARTG list DataFrame
artg_manufacturers = set(artg_list['Sponsor Name'].str.strip().str.lower())

# Normalize manufacturer names in product_info dataframe
product_info['Manufacturer'] = product_info['Manufacturer'].str.strip().str.lower()

# Loop through product info and check if manufacturer is in ARTG list
for index, product in product_info.iterrows():
    product_artg = product['ARTG Number']
    product_manufacturer = product['Manufacturer']
    
    if pd.isna(product_manufacturer) or not product_manufacturer.strip():
        print(f"{product['Name']}\nWarning!! does not have a manufacturer")
    else:
        if pd.isna(product_artg) or not product_artg.strip():
            #print(f"{product['Name']}\nWarning!! does not have an ARTG number")
            print("")
        else:
            product_artg_numbers = set()
            for artg_num in product_artg.split():
                artg_num = artg_num.strip()  # Remove leading/trailing white spaces
                if '-' in artg_num:
                    start, end = map(int, artg_num.split('-'))
                    if end == 0:
                        # ARTG number in the product list has a suffix of "-0"
                        # Check if corresponding number without the suffix is in ARTG list
                        if str(start) in artg_numbers:
                            product_artg_numbers.add(str(start))
                    else:
                        product_artg_numbers.update(str(x) for x in range(start, end+1))
                else:
                    product_artg_numbers.add(artg_num)
            if product_manufacturer in artg_manufacturers:
                print(f"{product['Name']}\nComplies with ARTG regulations")
            else:
                #print(f"{product['Name']}\nDoes not comply with ARTG regulations")
                print("")
