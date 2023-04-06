#%%
import csv
import pandas as pd

description=pd.read_csv("test.csv", usecols=["Id","Name","Description"]) #reads the csv with all products, with only ID, NAME, and DESCRIPTION
dictionary=pd.read_csv("dictionary.csv", usecols=["Keyword"], squeeze=True) #reads the Dictionary csv file which contains all keywords/phrases

desc = description['Description'].to_list() #converts decription to list
diction = dictionary.to_list() #converts description to list

#%%
number_claims = []
for descript in desc: #goes through each description
    #print(descript)
    descript= descript.lower()
    #print(descript)
    bad_claims = 0
    for keyword in diction: #goes through each keyword for each description 
        keyword = keyword.lower() # converts dictionary to lowercase
        if keyword in descript: # if keyword is in a description adds 1 to number of claims in number_claim variable
            bad_claims += 1 
    number_claims.append(bad_claims)

#for n in claim_:
    #print(n)
    
#%%
#determine if the product is compliant or not 
compliance = []
for n in number_claims:
    if n >= 1:
        compliance.append("non-compliant")
    elif n == 0:
        compliance.append("compliant")

print(compliance)

#%%








#%% 

# loop through desc column
    #i=0
    # for loop through claim table
        #if yes
        #i +=1
# claim numbers.append(i)    

# pattern = '|'.join(dictionary) #Joins the dictionary csv files

#exist=description['Description'].str.contains(pattern, na=False) #Grabs out products that contain the keywords and phrases based on description
#for CHECK in exist: #creates a new column that shows that the product is not compliant (All the descriptions that contain the keywords/phrases)
   # if not CHECK:
       # description['Compliant']='NO'
   # else:
      #  description['Compliant']='NO'

#description[exist].to_csv('nonCompliant.csv') #creates new csv with the list of all non-compliant products

#for CHECK in exist: #creates a new column that shows that the product is compliant (All the descriptions that dont contain the keywords/phrases)
   # if not CHECK:
      #  description['Compliant']='YES'
    #else:
       # description['Compliant']='YES'

#description[~exist].to_csv('compliant.csv') #creates new csv with the list of all compliant products

#compliant = pd.read_csv ("compliant.csv")
#nonCompliant= pd.read_csv("nonCompliant.csv")

#finalCompliance= pd.concat([compliant,nonCompliant]) #Joins the compliant and non-compliant csv files

#finalCompliance.to_csv("finalCompliance.csv") 

#print(finalCompliance)












# %%
