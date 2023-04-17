# Author:  Matthew Borowski
# Date Created: Monday 20/02/2023 16:10 
# Project Name: Detecting non-compliance therapeutic goods selling on e-commerce websites.
# Project Group ID: 9785-23-06


#%% Initialise packages etc.
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime
import random

#%% User selects file path location for files to be saved to.

from tkinter import filedialog
from tkinter import *
root = Tk()
root.withdraw()
SaveLocation = filedialog.askdirectory()
#print(SaveLocation)

#%%

#%% Selenium Driver Setup (chrome window)

#url variable, used to call what webpage to visit
URL= ""

#read setting file for setup
#opens file in read mode
settingsFile = open("settings.txt", mode = "r")
lines = []
for line in settingsFile:
    lines.append(line)
    #print(line)

keywordFile = open("keyword-searches.txt", mode = "r")
searchTerms = []
for keyword in keywordFile:
    c = keyword[0]
    if c != "#":
        searchTerms.append(keyword)
        #print(keyword)

#setting up where to save images etc.
prefs = {"downlaod.default_directory": lines[2]}
options = Options()
options.add_experimental_option("prefs", prefs)

#compile webdriver / browser for selenium to run
#driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()))
driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()), options = options)

# %% Open webpage and run start scraping

#starting with amazon webpage for scraping.
#URL= "https://www.amazon.com.au/"

#navigates the empty chrome window to the url specified
#driver.get(URL)

# find search bar to start searches
#searchBar = driver.find_element(By.ID, "twotabsearchtextbox")

# we can update this section to take a list of search terms to check 
# from a txt file or something that can be editted externally.
#searchTerm = "Vitamins & Supplements"

#input the current search term into the search box and send the enter key command
#searchBar.send_keys(searchTerm)
#searchBar.send_keys(Keys.ENTER)

#%% 







#%% list creation

# set up waits to add some variability as to fool automated systems
waitShort = [2, 3]
waitMedium = [3, 4, 5, 6]
waitLong = [5, 6, 7, 8]

# this list will contain all the hyperlink references (hrefs) we find on the pages
hrefs = []

# collected information lists
productName = [] #comes from Name function
hyperlinks = [] #comes from 'core" function
manufacturers = [] #comes from CollectAsinManufacturer function
sellers = [] #comes from ProductSeller function
asins = [] #comes from CollectAsinManufacturer function
keywordUsed = [] #comes from 'core" function
artgs = [] #comes from OCR_Image function
descriptions = [] #comes from DescriptionText function
productIngredients = [] #comes from FindIngredients function
datesCollected = [] #comes from CollectDate fucntion
imageProofName = [] #comes from ProductScreenshot function
OcrResults = [] #comes from OCR_Image function

# results lists
compliancePoison = [] #comes from PoisonCheck fucntion
complianceARTG = [] #comes from CheckARTG function
therapueticClaims = [] #comes from CheckTherpeuticClaims function

#%% import poison list and set up checking dependacies

import pandas as pd
import re

# ------ Poison Check ------ 
# Read poison ingredients from CSV files
poison_df = pd.read_csv('poison_list.csv', encoding='iso-8859-1')
# Create a set of poisonous substances for faster lookup
poison_set = set(poison_df['poison'].str.lower())
# Compile regular expressions for checking ingredient names against poisons
poison_regexes = [re.compile(rf"\b{re.escape(p)}\b") for p in poison_set]


# ------ Therapuetic Claim Check ------ 
#imports claim words/phrases from csv file
claimTermsTable = pd.read_csv("claim-terms.csv", usecols=["Keyword"], squeeze=True) 
#converts description to list
claimTerms = claimTermsTable.to_list() 


# ------ ARTG Number Check ------ 
# Read ARTG list CSV file into a pandas DataFrame
artg_list = pd.read_csv('artg_list.csv')
# Extract the set of unique manufacturers from the ARTG list DataFrame
artg_manufacturers = set(artg_list['Sponsor Name'].str.strip().str.lower())


#%% Load all function for checking compliance of products

#ARTG Check artg number and manufacturer.
def CheckARTG():
    for i in range(len(artgs)):
        #sets up variables for comparisons
        product_artg = artgs[i]
        product_manufacturer = manufacturers[i]
        
        if pd.isna(product_manufacturer) or not product_manufacturer.strip():
            if pd.isna(product_artg) or not product_artg.strip():
                #print(f"{product['Name']}\nWarning!! does not have a manufacturer")
                complianceARTG.append("non-compliant")
                # pass #no manufacturer so we make it non-compliant?
            else: #manufacturer is not na
                if pd.isna(product_artg) or not product_artg.strip():
                    #print(f"{product['Name']}\nWarning!! does not have an ARTG number")
                    complianceARTG.append("non-compliant")
                    # pass #no artg  number so its non-compliant
                else:
                    product_artg_numbers = set()
                    for artg_num in product_artg.split():
                        artg_num = artg_num.strip()  # Remove leading/trailing white spaces
                        #if '-' in artg_num:
                        #    start, end = map(int, artg_num.split('-'))
                        #    if end == 0:
                        #        # ARTG number in the product list has a suffix of "-0"
                        #        # Check if corresponding number without the suffix is in ARTG list
                        #        if str(start) in artg_num:
                        #            product_artg_numbers.add(str(start))
                        #    else:
                        #        product_artg_numbers.update(str(x) for x in range(start, end+1))
                        #else:
                        #    product_artg_numbers.add(artg_num)
                        product_artg_numbers.add(artg_num)
                    if product_manufacturer in artg_manufacturers:
                        #pass
                        #print(f"{product['Name']}\nComplies with ARTG regulations")
                        complianceARTG.append("compliant")
                    else:
                        #print(f"{product['Name']}\nDoes not comply with ARTG regulations")
                        complianceARTG.append("non-compliant")
                        #pass

# Checks ingredients and returns a bool of true or false based on if ingredeients are poisonous
def CheckIngredients(ingredients):
    # checks if the ingredfentis are blank or NaN and sets it to blank
    if pd.isna(ingredients):
        # If ingredients is NaN, convert it to an empty string
        ingredients = ""
    #checks to see if poison list is anythign but a string
    elif not isinstance(ingredients, str):
        # If ingredients is not a string, convert it to a string
        ingredients = str(ingredients)
    for ingredient in ingredients.split(","):
        ingredient = ingredient.strip()  # Remove leading/trailing spaces
        # Check if the ingredient name exactly matches a poison in the poison set
        if ingredient.lower() in poison_set:
            #contains poison
            return False 
        # Check if any variation of the ingredient name is a match to a poison in the poison set
        if any(regex.search(ingredient.lower()) for regex in poison_regexes):
            #contains poison
            return False 
    #no poison detected
    return True 

# creates a list of compliant or non-compliant results
def PoisonCheck():
    for ingred in productIngredients:
        safe = CheckIngredients(ingred)
        if safe == True:
            compliancePoison.append("compliant")
        else:
            compliancePoison.append("non-compliant")

# checks descriptions against claim keywords
def CheckTherpeuticClaims():
    #number_claims = []
    for descript in descriptions: #goes through each description
        #print(descript)
        descript = descript.lower()
        #print(descript)
        bad_claims = 0
        for keyword in claimTerms: #goes through each keyword for each description 
            keyword = keyword.lower() # converts dictionary to lowercase
            if keyword in descript: # if keyword is in a description adds 1 to number of claims in number_claim variable
                bad_claims += 1 
        #number_claims.append(bad_claims)
        if bad_claims >= 1:
            therapueticClaims.append("non-compliant")
        else:
            therapueticClaims.append("compliant")






#%% Load all functions for collecting product information

# Opens the main landing page for amazon
def OpenAmazon(): 
    #starting with amazon webpage for scraping.
    URL= "https://www.amazon.com.au/"
    #navigates the empty chrome window to the url specified
    driver.get(URL)
    #wait so the website can load (possible problem with slower connections.)
    time.sleep(random.choice(waitMedium))

# This inputs the search term into the search bar on amazon
def SearchAmazon(searchTerm):
    from selenium.common.exceptions import TimeoutException
    # from selenium.webdriver.common.keys import Keys
    # find search bar to start searches
    while(True):
        try:
            searchBar = driver.find_element(By.ID, "twotabsearchtextbox")
            searchBar.send_keys(searchTerm)
        except TimeoutException:
            try:
                searchBar = driver.find_element(By.ID, "nav-bb-search")
                searchBar.send_keys(searchTerm)
            except TimeoutException:
                driver.refresh()
            else:
                break
        else:
            break

    #input the current search term into the search box and send the enter key command
    #searchBar.send_keys(searchTerm)
    #searchBar.send_keys(Keys.ENTER)

# Collects the hyperlink references from the product results page
def PageHrefs():
    import time
    #wait so the website can load (possible problem with slower connections.)
    time.sleep(random.choice(waitMedium))
    # find all the products on the page by using an XPATH search to find all 
    products = driver.find_elements(By.XPATH, "//*[@class='a-link-normal s-no-outline']")
    # loop through all the product elements and collect their href links.
    for prod in products:
        #print(prod.get_attribute("href"))
        #adds href link to end of list of links
        hrefs.append(prod.get_attribute("href"))

# Attempts to go to the next page of search results
def NextPage():
    # go to next page of search
    from selenium.webdriver.common.action_chains import ActionChains

    try:        
        nextButton = driver.find_element(By.XPATH, "//*[@class = 's-pagination-item s-pagination-next s-pagination-button s-pagination-separator']")
        ac = ActionChains(driver)
        #clicks on cross button so other parts of code an function properly
        ac.move_to_element(nextButton).click().perform()
        return True
    except:
        return False

# Manages changing pages and collecting results functions
def CollectHrefs():
    #stillPages indicates that information needs to be collected from the currently active screen
    stillPages = True
    while stillPages == True:
        #collectedPage helps loop and collect the current displayed page, not sure if its needed reeally.
        collectedPage = False
        if collectedPage == False:
            #pageHrefs coollects and appends the Hyperlinks of products into a list.
            PageHrefs()
            collectedPage = True
            #nextPage returns true if it changes page and false if its fails and cannot
            stillPages = NextPage()
            if stillPages == True:
                collectedPage = False

# Image collection
def ImageCollection():
    from selenium.webdriver.common.action_chains import ActionChains

    thumbnails = []
    #setup action driver
    ac = ActionChains(driver)
    #for image thumbnail locations
    #//*[@class='a-spacing-small item imageThumbnail a-declarative']
    thumbnails = driver.find_elements(By.XPATH, "//*[@class='a-spacing-small item imageThumbnail a-declarative']")
    #hover over thumbnails to load high-res images into html code
    for thumbnail in thumbnails:
        #moves a 'mouse' over the thumbnail elements
        ac.move_to_element(thumbnail).perform()

    highResImgHrefs = []
    #search for full size images
    highResImgs = driver.find_elements(By.XPATH, "//*[@id='main-image-container']/ul/li/span/span/div/img")
    for img in highResImgs:
        highResImgHrefs.append(img.get_attribute("src"))
        #print(img.get_attribute("src"))

    x = 0
    for imgRef in highResImgHrefs:   
        #going to image webpage 
        driver.get(imgRef)

        #testing out a wait here so the searches last longer and hopefully we get less hits per minute on the amazon server
        #time.sleep(random.choice(waitShort))

        x += 1
        #formats the number to be a 6 digit number eg 1 will be 000001
        number = "{0:0=2d}".format(x)
        #create the output name
        proofName = "image"+ number + ".png"
        outputLocation = "Product Images/"+ proofName
        
        #saving image thats found on image webpage
        with open (outputLocation, 'wb') as file:
            file.write(driver.find_element(By.XPATH, "//body/img").screenshot_as_png)    

# Delete images
def Delete_Image(file):
    import os
    #print(file + " deleting")
    os.remove(file)

# Collect name of product
def Name():
    name = driver.find_element(By.ID, "productTitle").text
    productName.append(name)
    #print(name)

# Date collected
def CollectDate():
    date = str(datetime.today().strftime('%Y-%m-%d'))
    datesCollected.append(date)
    #print(date)

# Collect ingredients
def FindIngredients():
    ingredients = ""
    ingredName = "Ingredients:"
    try:
        #section = driver.find_element(By.ID, "important-information")
        #ingredients = driver.find_element()
        #find what section has the ingredients, its nmot always in the same position
        infoSections = driver.find_elements(By.XPATH, "//*[@id='important-information']/div/h4")
        
        #for infoSec in infoSections:
        #    print(infoSec.text)
        i = 0
        
        for infoSec in infoSections:
            i += 1
            if infoSec.text == ingredName:
                # the [2] on the end was added because it originally didnt need it but it it wouldnt pick anything up
                # if this continues, I will need ot do a if null check and continue onto the next one to collect info.
                if i == "1":
                    ingredients = driver.find_element(By.XPATH, "//*[@id='important-information']/div[1]/p[2]").text
                elif i == "2":
                    ingredients = driver.find_element(By.XPATH, "//*[@id='important-information']/div[2]/p[2]").text
                else:
                    ingredients = driver.find_element(By.XPATH, "//*[@id='important-information']/div[3]/p[2]").text
                #position of ingredients in list at i index
                #//*[@id='important-information']/div[i]/p[2]
                #dynamicXPath = "//*[@id='important-information']/div[" + i + "]/p"
                #print(dynamicXPath)
                #ingredients = driver.find_elements(By.XPATH, dynamicXPath).text
                #print(ingredients)
    except:
        #print("---- no ingredients listed ----")
        ingredients = ""
    productIngredients.append(ingredients)

# Find seller
def ProductSeller():
    try:
        # //*[@class="tabular-buybox-container"] top box
        # //*[@class="tabular-buybox-text"][2] more specific
        seller = driver.find_element(By.XPATH, "//*[@class='tabular-buybox-text'][2]").text
        if seller == "":
            #get seller a different way becuase amazon offers recurring purchase options and thus has a different layout.
            seller = driver.find_element(By.XPATH, "//*[@id='sfsb_accordion_head']//div[2]//div//span[2]").text
        #print(seller)
        sellers.append(seller)
    except:
        try:
            from selenium.webdriver.common.action_chains import ActionChains
            buyingOptions = driver.find_element(By.ID, "buybox-see-all-buying-choices")
        
            #setup action driver
            ac = ActionChains(driver)
            #clicks on buying options button
            ac.move_to_element(buyingOptions).click().perform()

            time.sleep(random.choice(waitMedium))
            #find the multiple sellers.
            sellerNames = []
            sellerOptions = driver.find_elements(By.XPATH, "//*[@Class='a-size-small a-link-normal']")
            for seller in sellerOptions:
                if(seller.text != ""):
                    #print(seller.text)
                    sellerNames.append(seller.text)
            #create output of all names for database
            outputName = ""
            for sellerName in sellerNames:
                outputName = outputName + sellerName + ", "
            sellers.append(outputName)
            #print(outputName)
            crossButton = driver.find_element(By.XPATH, "//*[@id='all-offers-display']/span/div")
            ac = ActionChains(driver)
            #clicks on cross button so other parts of code an function properly
            ac.move_to_element(crossButton).click().perform()
        except:
            sellers.append("Item Currently Unavailable")

# Manufacturer and ASIN
def CollectAsinManufacturer():
    #old way of finding ASIN
    #asin = driver.find_element(By.XPATH, "//*[@id='detailBullets_feature_div']/ul/li[4]/span/span[2]").text
    #print(asin)
    details = driver.find_elements(By.XPATH, "//*[@id='detailBulletsWrapper_feature_div']/div/ul[1]/li/span/span")
    i = 0
    asin = ""
    manufacturer = ""
    for dets in details:
        #print(dets.text)
        i += 1
        editDets = dets.text.rstrip(" :")
        #print(editDets)
        #if "Manufacturer" in dets.text :
        if "Manufacturer" == editDets :
            #print ("---MANUFACTURER SOMEWHAT FOUND")
            #print(i)
            if i == 5:
                #print("--- found manu @ pos 3")
                manufacturer = driver.find_element(By.XPATH, "//*[@id='detailBullets_feature_div']/ul/li[3]/span/span[2]").text
                #manufacturer = driver.find_element(By.XPATH, "//*[@id='detailBulletsWrapper_feature_div']/div/ul[1]/li[3]/span/span[2]").text
            if i == 7:
                #print("--- found manu @ pos 4")
                manufacturer = driver.find_element(By.XPATH, "//*[@id='detailBullets_feature_div']/ul/li[4]/span/span[2]").text
                #manufacturer = driver.find_element(By.XPATH, "//*[@id='detailBulletsWrapper_feature_div']/div/ul[1]/li[4]/span/span[2]").text
        #if "ASIN" in dets.text :
        if "ASIN" == editDets :
            #print ("---ASIN SOMEWHAT FOUND")
            #print(i)
            if i == 7:
                #print("--- found ASIN @ pos 4")
                asin = driver.find_element(By.XPATH, "//*[@id='detailBullets_feature_div']/ul/li[4]/span/span[2]").text
                #asin = driver.find_element(By.XPATH, "//*[@id='detailBulletsWrapper_feature_div']/div/ul[1]/li[4]/span/span[2]").text
            if i == 9:
                #print("--- found ASIN @ pos 5")
                asin = driver.find_element(By.XPATH, "//*[@id='detailBullets_feature_div']/ul/li[5]/span/span[2]").text
                #asin = driver.find_element(By.XPATH, "//*[@id='detailBulletsWrapper_feature_div']/div/ul[1]/li[5]/span/span[2]").text
    #print(manufacturer)
    manufacturers.append(manufacturer)
    #print(asin)
    asins.append(asin)

# Collect screenshot of product screen
def ProductScreenshot(tally):
    #formats the number to be a 6 digit number eg 1 will be 000001
    number = "{0:0=6d}".format(tally)
    #create the output name
    screenshotName = "proof"+ number + ".png"
    outputLocation = "Product Screenshots/"+ screenshotName
    #print(outputLocation)
    driver.save_screenshot(outputLocation)
    imageProofName.append(screenshotName)

# OCR of images to find ARTG number using pytesseract
def OCR_Image():
    #import useful packages
    import pytesseract
    from PIL import Image
    import os

    #collects all the results of each image in one place.
    OCR_Results = []
    ArtgResults = []

    # Get the list of all files and directories
    path = "Product Images/"
    dir_list = os.listdir(path)

    for file in dir_list:
        file = "Product Images/" + file

        #original image, no preprocessing
        #im_file = "Product Images/image01.png"
        #loads image into memory
        img = Image.open(file)
        #saves the text found by OCR
        ocr_result = pytesseract.image_to_string(img)
        #prints all the text found
        #print(ocr_result)
        #format text better
        ocr_result = ocr_result.replace("\n", " ")
        
        OCR_Results.append(ocr_result)
        ARTG_L = ""
        ARTG_R = ""
        try:
            startIndex = ocr_result.find("AUST L")
            endIndex = startIndex + 13
            ARTG_L = ocr_result[startIndex:endIndex].strip()
        except:
            ARTG_L = ""
        
        try:
            startIndex = ocr_result.find("AUSTL ")
            endIndex = startIndex + 12
            ARTG_L = ocr_result[startIndex:endIndex].strip()
        except:
            ARTG_L = ""
        try:
            startIndex = ocr_result.find("AUSTL")
            endIndex = startIndex + 11
            ARTG_L = ocr_result[startIndex:endIndex].strip()
        except:
            ARTG_L = ""
        try:
            startIndex = ocr_result.find("AUST R")
            endIndex = startIndex + 13
            ARTG_R = ocr_result[startIndex:endIndex].strip()
        except:
            ARTG_R = ""
        try:
            startIndex = ocr_result.find("AUSTR ")
            endIndex = startIndex + 12
            ARTG_L = ocr_result[startIndex:endIndex].strip()
        except:
            ARTG_L = ""
        try:
            startIndex = ocr_result.find("AUSTR")
            #this test is because the word 'AUSTRALIA' would be picked up mistakenly
            #this isnt an issue for the other tests.
            testIndex = startIndex + 5
            testLetter = ocr_result[testIndex]
            if testLetter != "A": 
                endIndex = startIndex + 12
                ARTG_L = ocr_result[startIndex:endIndex].strip()
        except:
            ARTG_L = ""

        artgFinal = ARTG_L + " " +ARTG_R
        #print(artgFinal)
        ArtgResults.append(artgFinal)

        Delete_Image(file)

    #put all results into a single line and append product information
    ocrOutput = ""
    for result in OCR_Results:
        ocrOutput = ocrOutput + result
    OcrResults.append(ocrOutput)
    artgOutput = ""
    for result in ArtgResults:
        artgOutput = artgOutput + result
    artgs.append(artgOutput)

# Collect product infromation under the "about this item" section
def DescriptionText():
    writtentext = []
    featuresList = driver.find_elements(By.XPATH, "//*[@id='feature-bullets']//li/span")
    for ft in featuresList:
        writtentext.append(ft.text)
    #if a description is available
    try:    
        description = driver.find_element(By.XPATH, "//*[@id='productDescription']/p/span")
        writtentext.append(description.text)
    except:
        #print("---- no description section ----")
        pass

    #for text in writtentext:
        #print(text)
    textOutput = ""
    for txt in writtentext:
        textOutput = textOutput + txt
    descriptions.append(textOutput)
    
#%% New chrome window

def createChromeWindow():
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager

    #setting up where to save images etc.
    #prefs = {"downlaod.default_directory": lines[2]}
    #options = Options()
    #options.add_experimental_option("prefs", prefs)

    #compile webdriver / browser for selenium to run
    #driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()))
    driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()), options = options)

    return driver



#%% go to product page


def StartSearch():
    
    try:
        for term in searchTerms: #loops through search terms
            OpenAmazon() #open amazon
            SearchAmazon(term) #sends search term to driver
            CollectHrefs()
            #Counting the number of products for the proof image naming
            n = 0

            #loop through all the products
            for link in hrefs:
                #Loads the product page using hyperlink from the resulkts page
                driver.get(link)
                time.sleep(random.choice(waitMedium)) #wait for page to load
                #sometimes Amazon will redirect you elsewhere
                current = driver.current_url
                if "www.primevideo.com" in current:
                    #time.sleep(300)
                    #driver.refresh()
                    pass
                hyperlinks.append(link)
                CollectDate() #date collected
                    #keyword search
                    #print(searchTerm)
                keywordUsed.append(term)
                Name() #collect name of product
                FindIngredients() #collect ingredients
                DescriptionText() #collect product infromation under the "about this item" section
                CollectAsinManufacturer() #manufacturer and ASIN
                ProductSeller() #find seller
                ProductScreenshot(n) #proof screenshot
                ImageCollection() #images from product thumbnails 
                OCR_Image() #run OCR on images to extract text
                time.sleep(random.choice(waitShort))
                n = n + 1
            #reset the href list as to not take up too much memory
            hrefs.clear()
        #just a timer, you could add whatever further functionality 
        #after this point
        time.sleep(30)
    except:
        print(datetime.today())
        print(n)
        #closes the window
        #driver.quit()
        




#%% starts the program
print(datetime.today())
#driver = createChromeWindow()
StartSearch()



#%%

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime
import random

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException

#setting up where to save images etc.
#prefs = {"downlaod.default_directory": lines[2]}
#options = Options()
#options.add_experimental_option("prefs", prefs)

#compile webdriver / browser for selenium to run
#driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()))
#driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()), options = options)

keywordFile = open("keyword-searches.txt", mode = "r")
searchTerms = []
for keyword in keywordFile:
    c = keyword[0]
    if c != "#":
        searchTerms.append(keyword)
        #print(keyword)

#driver 
# create window
driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()))
# collects all the hyperlinks
for term in searchTerms: #loops through search terms
    OpenAmazon() #open amazon
    SearchAmazon(term) #sends search term to driver
    CollectHrefs()


#%%

# #Counting the number of products for the proof image naming
n = 0
#
stillCollecting = True

while(stillCollecting):
    try:
        #loop through all the products
        #for n in range(len(hrefs)):
        while n <= len(hrefs):
            #Loads the product page using hyperlink from the resulkts page
            driver.get(hrefs[n])
            time.sleep(random.choice(waitMedium)) #wait for page to load
            #sometimes Amazon will redirect you elsewhere
            current = driver.current_url
            if "www.primevideo.com" in current:
                #time.sleep(300)
                driver.quit()
                pass
            
            CollectDate() #date collected
            hyperlinks.append(hrefs[n])
                #keyword search
                #print(searchTerm)
            #keywordUsed.append(term)
            Name() #collect name of product
            FindIngredients() #collect ingredients
            DescriptionText() #collect product infromation under the "about this item" section
            CollectAsinManufacturer() #manufacturer and ASIN
            ProductSeller() #find seller
            ProductScreenshot(n) #proof screenshot
            ImageCollection() #images from product thumbnails 
            OCR_Image() #run OCR on images to extract text
            time.sleep(random.choice(waitShort))
            n = n + 1
        #reset the href list as to not take up too much memory
        #hrefs.clear()
        #just a timer, you could add whatever further functionality 
        #after this point
        time.sleep(10)
        print("-----Finished collecting all products-----")
        stillCollecting = False
        break
    except:
        print(n)
        driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()))
        #print(datetime.today())
        #closes the window
        #driver.quit()






#%%

driver.refresh()


#%% trying to save only the page results hyperlinks and keyword used for search

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime
import random

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException

# set up waits to add some variability as to fool automated systems
waitShort = [2, 3]
waitMedium = [3, 4, 5, 6]
waitLong = [5, 6, 7, 8]


# Opens the main landing page for amazon
def OpenAmazonE(): 
    #starting with amazon webpage for scraping.
    URL= "https://www.amazon.com.au/"
    #navigates the empty chrome window to the url specified
    driver.get(URL)
    #wait so the website can load (possible problem with slower connections.)
    time.sleep(random.choice(waitMedium))

# This inputs the search term into the search bar on amazon
def SearchAmazonE(searchTerm):
    from selenium.common.exceptions import TimeoutException
    # from selenium.webdriver.common.keys import Keys
    # find search bar to start searches
    while(True):
        try:
            searchBar = driver.find_element(By.ID, "twotabsearchtextbox")
            searchBar.send_keys(searchTerm)
        except TimeoutException:
            try:
                searchBar = driver.find_element(By.ID, "nav-bb-search")
                searchBar.send_keys(searchTerm)
            except TimeoutException:
                driver.refresh()
            else:
                break
        else:
            break

    #input the current search term into the search box and send the enter key command
    #searchBar.send_keys(searchTerm)
    #searchBar.send_keys(Keys.ENTER)



# Attempts to go to the next page of search results
def NextPageE():
    # go to next page of search
    from selenium.webdriver.common.action_chains import ActionChains

    try:        
        nextButton = driver.find_element(By.XPATH, "//*[@class = 's-pagination-item s-pagination-next s-pagination-button s-pagination-separator']")
        ac = ActionChains(driver)
        #clicks on cross button so other parts of code an function properly
        ac.move_to_element(nextButton).click().perform()
        return True
    except:
        return False

# Date collected
def CollectDateE():
    date = str(datetime.today().strftime('%Y-%m-%d'))
    datesCollected.append(date)
    #print(date)

# Collects the hyperlink references from the product results page
def PageHrefsE(n, keyword):
    import time
    #wait so the website can load (possible problem with slower connections.)
    time.sleep(random.choice(waitMedium))
    # find all the products on the page by using an XPATH search to find all 
    products = driver.find_elements(By.XPATH, "//*[@class='a-link-normal s-no-outline']")
    # lists of info for collected products for this page
    pageHrefs = []
    pageKeyword = []
    pageDateCollected = []
    # loop through all the product elements and collect their href links.
    for prod in products:
        #print(prod.get_attribute("href"))
        #adds href link to end of list of links
        pageHrefs.append(prod.get_attribute("href"))
        pageKeyword.append(keyword)
        date = str(datetime.today().strftime('%Y-%m-%d'))
        pageDateCollected.append(date)
    # export page of things with 
    import pandas as pd
    data = {
        'Hyperlink' : pageHrefs,
        'SearchKeywords' : pageKeyword,
        'DateCollected' : pageDateCollected
    }
    df = pd.DataFrame(data)
    keyword = keyword.strip()
    keyword = keyword.replace("&" , "")
    keyword = keyword.replace("'" , "")
    df.to_csv(keyword + '-page-' + str(n) + '.csv')

# Manages changing pages and collecting results functions
def CollectHrefsE(word):
    n = 1
    #stillPages indicates that information needs to be collected from the currently active screen
    stillPages = True
    while stillPages == True:
        #collectedPage helps loop and collect the current displayed page, not sure if its needed reeally.
        collectedPage = False
        if collectedPage == False:
            #pageHrefs coollects and appends the Hyperlinks of products into a list.
            PageHrefsE(n, word)
            collectedPage = True
            #nextPage returns true if it changes page and false if its fails and cannot
            stillPages = NextPageE()
            if stillPages == True:
                n += 1
                collectedPage = False
            
keywordFile = open("keyword-searches.txt", mode = "r")
searchTerms = []
for keyword in keywordFile:
    c = keyword[0]
    if c != "#":
        searchTerms.append(keyword)
        #print(keyword)

# create window
driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()))
# collects all the hyperlinks
for term in searchTerms: #loops through search terms
    OpenAmazonE() #open amazon
    SearchAmazonE(term) #sends search term to driver
    CollectHrefsE(term)

#%% read page results and collect specific product results

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime
import random
import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException

# set up waits to add some variability as to fool automated systems
waitShort = [2, 3]
waitMedium = [3, 4, 5, 6]
waitLong = [5, 6, 7, 8]

# this list will contain all the hyperlink references (hrefs) we find on the pages
hrefs = []

# collected information lists
productName = [] #comes from Name function
hyperlinks = [] #comes from 'core" function
manufacturers = [] #comes from CollectAsinManufacturer function
sellers = [] #comes from ProductSeller function
asins = [] #comes from CollectAsinManufacturer function
keywordUsed = [] #comes from 'core" function
artgs = [] #comes from OCR_Image function
descriptions = [] #comes from DescriptionText function
productIngredients = [] #comes from FindIngredients function
datesCollected = [] #comes from CollectDate fucntion
imageProofName = [] #comes from ProductScreenshot function
OcrResults = [] #comes from OCR_Image function


# Collect screenshot of product screen
def ProductScreenshotE(tally, name):
    #formats the number to be a 6 digit number eg 1 will be 000001
    number = "{0:0=2d}".format(tally)
    #create the output name
    screenshotName = name + "-product-" + number + ".png"
    outputLocation = "Product Screenshots/"+ screenshotName
    #print(outputLocation)
    driver.save_screenshot(outputLocation)
    imageProofName.append(screenshotName)


import os


# Get the list of all files and directories
path = "Searches/"
dir_list = os.listdir(path)

for file in dir_list:
    csvName = file.replace(".csv", "")
    csvName = csvName.strip()
    file = "Searches/" + file

    # This resets the lists so we can fill them all equally
    hrefs.clear()
    productName.clear()
    hyperlinks.clear()
    manufacturers.clear()
    sellers.clear()
    asins.clear()
    keywordUsed.clear()
    artgs.clear()
    descriptions.clear()
    productIngredients.clear()
    datesCollected.clear()
    imageProofName.clear()
    OcrResults.clear()

    #read file into dataframe
    import pandas as pd
    results_df = pd.read_csv(file, sep=',', encoding="utf-8", skipinitialspace=True)
    hyperlinks = results_df['Hyperlink'].to_list()
    keywordUsed = results_df['SearchKeywords'].to_list()
    print(len(hyperlinks))
    print(len(keywordUsed))
#%%

    #create window
    driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()))

    i = 1
    for href in hyperlinks:
        print(str(i) + " - " + href)
        if "primevideo" in href:
            productName.append(" ")
            manufacturers.append(" ")
            sellers.append(" ")
            asins.append(" ")
            keywordUsed.append(" ")
            artgs.append(" ")
            descriptions.append(" ")
            productIngredients.append(" ")
            datesCollected.append(" ")
            imageProofName.append(" ")
            OcrResults.append(" ")
        else:
            driver.get(href)
            time.sleep(random.choice(waitMedium)) #wait for page to load
            #sometimes Amazon will redirect you elsewhere
            current = driver.current_url
            if "www.primevideo.com" in current:
                #time.sleep(300)
                #driver.quit()
                pass
            
            CollectDate() #date collected
            #hyperlinks.append(hrefs[i])
                #keyword search
                #print(searchTerm)
            #keywordUsed.append(term)
            Name() #collect name of product
            FindIngredients() #collect ingredients
            DescriptionText() #collect product infromation under the "about this item" section
            CollectAsinManufacturer() #manufacturer and ASIN
            ProductSeller() #find seller
            ProductScreenshotE(i, csvName) #proof screenshot
            ImageCollection() #images from product thumbnails 
            OCR_Image() #run OCR on images to extract text
            time.sleep(random.choice(waitShort))
        i += 1

    driver.quit()

    import pandas as pd
    data = {
        'Name' : productName,
        'Hyperlink' : hyperlinks,
        'Manufacturer' : manufacturers,
        'Seller' : sellers,
        'ASIN' : asins,
        'SearchKeywords' : keywordUsed,
        'ARTG' : artgs,
        'Description' : descriptions,
        'Ingredients' : productIngredients,
        'DateCollected' : datesCollected,
        'ImageProofName' : imageProofName,
        'OCR_Results' : OcrResults
    }
    df = pd.DataFrame(data)
    df.to_csv(csvName + '-results.csv')
    #delete csv file once we're done with it
    Delete_Image(file)

    # opening vs code with MSI afterburner running is 6400MB in RAM
    # after it started running it jumped to 7600MB
    # 


#%% Output infromation to a csv file
import pandas as pd
data = {
    'Name' : productName,
    'Hyperlink' : hyperlinks,
    'Manufacturer' : manufacturers,
    'Seller' : sellers,
    'ASIN' : asins,
    'SearchKeywords' : keywordUsed,
    'ARTG' : artgs,
    'Description' : descriptions,
    'Ingredients' : productIngredients,
    'DateCollected' : datesCollected,
    'ImageProofName' : imageProofName,
    'OCR_Results' : OcrResults
}
df = pd.DataFrame(data)
df.to_csv(csvName + "-results" + '.csv')


#%%



#%% Wrapping up procedures




# %%
