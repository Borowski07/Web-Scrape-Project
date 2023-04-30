#############################################################################################
# Author: Matthew Borowski                                                                 #
# Date Created: Monday 21/04/2023 15:51                                                     #
# Project Name: Detecting non-compliance therapeutic goods selling on e-commerce websites.  #
# Project Group ID: 9785-23-06                                                              #
#############################################################################################

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

#this is the list of folders that are needed for the program to run
foldersToMake = ["Searches", "Product Images", "Product Screenshots", "Web Scrape Information", "Results"]

#this will make the folders if the file location hasnt got the folders created yet.
import os
for folderName in foldersToMake:
    newpath = SaveLocation + "/" + folderName
    if not os.path.exists(newpath):
        os.makedirs(newpath)

#%% import poison list, ARTG list and set up checking dependacies

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
claimTermsTable = pd.read_csv("claim-terms.csv") 
#converts description to list
claimTerms = claimTermsTable['Keyword'].to_list()

# ------ ARTG Number Check ------ 
# Read ARTG list CSV file into a pandas DataFrame
artg_list = pd.read_csv('artg_list.csv')
# Extract the set of unique manufacturers from the ARTG list DataFrame
artg_manufacturers = set(artg_list['Sponsor Name'].str.strip().str.lower())

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

#system guesss
artgSponsorList = pd.unique(artg_list['Sponsor Name'].to_list()) #this comes from the imported artg csv file
complianceSystemGuess = [] #comes from the complianceSystemGuess() function
complianceSystemCorrect = [] #complianceSystemCorrectness() function

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
        outputLocation = SaveLocation + "/Product Images/"+ proofName
        
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
    ingredName = "Ingred"
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
            if ingredName in infoSec.text:
            #if infoSec.text == ingredName:
                # the [2] on the end was added because it originally didnt need it but it it wouldnt pick anything up
                # if this continues, I will need ot do a if null check and continue onto the next one to collect info.
                if i == 1:
                    ingredients = driver.find_element(By.XPATH, "//*[@id='important-information']/div[1]/p[2]").text
                elif i == 2:
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
def ProductScreenshot(tally, name):
    #formats the number to be a 6 digit number eg 1 will be 000001
    number = "{0:0=2d}".format(tally)
    #create the output name
    screenshotName = name + "-product-" + number + ".png"
    outputLocation = SaveLocation + "/Product Screenshots/"+ screenshotName
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
    path = SaveLocation + "/Product Images/"
    dir_list = os.listdir(path)

    for file in dir_list:
        file = SaveLocation + "/Product Images/" + file

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
        #use lower so we can just find patterns and not specific upper/lowercase situations
        #results will still be taken from the uppercase ocr results
        ocr_lower = ocr_result.lower()
        OCR_ArtgResult = []
        try:
            startIndex = ocr_lower.find("aust l")
            endIndex = startIndex + 13
            OCR_ArtgResult.append(ocr_result[startIndex:endIndex].strip()) 
        except:
            pass
        try:
            startIndex = ocr_lower.find("austl ")
            endIndex = startIndex + 12
            OCR_ArtgResult.append(ocr_result[startIndex:endIndex].strip())
        except:
            pass
        try:
            startIndex = ocr_lower.find("austl")
            endIndex = startIndex + 11
            OCR_ArtgResult.append(ocr_result[startIndex:endIndex].strip())
        except:
            pass
        try:
            startIndex = ocr_lower.find("aust r")
            endIndex = startIndex + 13
            OCR_ArtgResult.append(ocr_result[startIndex:endIndex].strip())
        except:
            pass
        try:
            startIndex = ocr_lower.find("austr ")
            endIndex = startIndex + 12
            OCR_ArtgResult.append(ocr_result[startIndex:endIndex].strip())
        except:
            pass
        try:
            startIndex = ocr_lower.find("austrs")
            #this test is because the word 'AUSTRALIA' would be picked up mistakenly
            #this isnt an issue for the other tests.
            testIndex = startIndex + 5
            testLetter = ocr_lower[testIndex]
            if testLetter != "A": 
                endIndex = startIndex + 12
                OCR_ArtgResult.append(ocr_result[startIndex:endIndex].strip())
        except:
            pass
        
        artgFinal = ""
        if len(OCR_ArtgResult) >= 1:
            for info in OCR_ArtgResult:
                artgFinal = artgFinal + " " + info
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


#%% Whole search code inclding modified saearch 

# Collects the hyperlink references from the product results page
def PageHrefsWholeSearch(n, i, keyword):
    import time
    #wait so the website can load (possible problem with slower connections.)
    time.sleep(random.choice(waitMedium))
    # find all the products on the page by using an XPATH search to find all 
    products = driver.find_elements(By.XPATH, "//*[@class='a-link-normal s-no-outline']")
    # lists of info for collected products for this page
    pageHrefs = []
    pageKeyword = []
    #pageDateCollected = []
    # loop through all the product elements and collect their href links.
    for prod in products:
        #print(prod.get_attribute("href"))
        #adds href link to end of list of links
        pageHrefs.append(prod.get_attribute("href"))
        pageKeyword.append(keyword)
        #date = str(datetime.today().strftime('%Y-%m-%d'))
        #pageDateCollected.append(date)
    # export page of things with 
    import pandas as pd
    data = {
        'Hyperlink' : pageHrefs,
        'SearchKeywords' : pageKeyword
    }
    df = pd.DataFrame(data)
    keyword = keyword.strip()
    keyword = keyword.replace("&" , "")
    keyword = keyword.replace("'" , "")
    pageNum = (n *40) + i
    df.to_csv(SaveLocation + "/Searches/" + keyword + '-page-' + str(pageNum) + '.csv')



#%% Collect all the 400 pages of the 'Vitamins & Supplements' section

print("------------------------------------")
print("started process at: " + str(datetime.today()))
print("------------------------------------")

#URL for the entire vitamin and supplements range
URL = "https://www.amazon.com.au/gp/browse.html?node=5148202051&ref_=nav_em_hpc_vitamins_0_2_16_11"
term = "Vitamins and Supplements"

#create window
driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()))
#goes to URL in the chrome window
driver.get(URL)
time.sleep(3) #wait for page to laod

#finds the final page number and makes it an int that can be used later
lastPageNum = driver.find_element(By.XPATH, "//*[@class = 's-pagination-strip']//span[4]").text
lastPageInt = int(lastPageNum)

#goes to next page
from selenium.webdriver.common.action_chains import ActionChains
nextButton = driver.find_element(By.XPATH, "//*[@class = 's-pagination-item s-pagination-next s-pagination-button s-pagination-separator']")
ac = ActionChains(driver)
ac.move_to_element(nextButton).click().perform()

#This will save the base URL that we will manipulate later
URL_Base =  driver.current_url

time.sleep(3)
driver.quit() #kills the window

URL_Previous = "https://www.amazon.com.au/gp/browse.html?node=5148202051&ref_=nav_em_hpc_vitamins_0_2_16_11"

#find out the amount of loops needed when taking 40 pages at a time.
import math
totalIterations = math.ceil(lastPageInt/40)
n = 0
while n < totalIterations:
    i = 1
    driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()))
    #load amazon page
    driver.get(URL_Previous)
    time.sleep(random.choice(waitMedium))
    while i <= 40:
        time.sleep(random.choice(waitMedium))
        #collect info from page and saves out to csv file
        PageHrefsWholeSearch(n, i, term)
        try:
            #move onto next page
            from selenium.webdriver.common.action_chains import ActionChains
            nextButton = driver.find_element(By.XPATH, "//*[@class = 's-pagination-item s-pagination-next s-pagination-button s-pagination-separator']")
            ac = ActionChains(driver)
            ac.move_to_element(nextButton).click().perform()

            #save page in case its the last page to be collected.
            URL_Previous = driver.current_url
        except:
            pass
        i += 1
    driver.quit()
    time.sleep(random.choice(waitMedium))
    n += 1

print("------------------------------------")
print("completed all at: " + str(datetime.today()))
print("------------------------------------")


#%% This will run through all the search files and collect the product information

import os

# Get the list of all files and directories
path = SaveLocation +"/Searches/"
dir_list = os.listdir(path)

for file in dir_list:
    csvName = file.replace(".csv", "")
    csvName = csvName.strip()
    #file = "Searches/" + file
    file = path + file

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
    #results_df = pd.read_csv(file, sep=',', encoding="utf-8", skipinitialspace=True)
    results_df = pd.read_csv(file, sep=',')
    hyperlinks = results_df['Hyperlink'].to_list()
    keywordUsed = results_df['SearchKeywords'].to_list()
    #print(len(hyperlinks))
    #print(len(keywordUsed))


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
            artgs.append(" ")
            descriptions.append(" ")
            productIngredients.append(" ")
            datesCollected.append(" ")
            imageProofName.append(" ")
            OcrResults.append(" ")
        else:
            driver.get(href)
            #time.sleep(15) #wait for page to load
            time.sleep(random.choice(waitMedium)) #wait for page to load
            #sometimes Amazon will redirect you elsewhere
            #current = driver.current_url
            #if "www.primevideo.com" in current:
            #    #time.sleep(300)
            #    #driver.quit()
            #    pass
            
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
            ProductScreenshot(i, csvName) #proof screenshot
            ImageCollection() #images from product thumbnails 
            OCR_Image() #run OCR on images to extract text
            time.sleep(1)
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
    df.to_csv(SaveLocation + '/Web Scrape Information/' + csvName + '-results.csv')
    #delete csv file once we're done with it
    Delete_Image(file)

    # opening vs code with MSI afterburner running is 6400MB in RAM
    # after it started running it jumped to 7600MB

#%% combine all the files from folder into a different place.

path = SaveLocation +"/Web Scrape Information/"
dir_list = os.listdir(path)

#import glob

csv_files = [] 
# list all csv files only
#csv_files = glob.glob('*.{}'.format('csv'))
for file in dir_list:
    csv_files.append(file)
#print(csv_files)

import pandas as pd
#create new dataframe for the results.
dfCompiled = pd.DataFrame() 
# append the CSV files
for file in csv_files:
    file = path + file
    df = pd.read_csv(file)
    dfCompiled = dfCompiled.append(df, ignore_index=True)
 
# cleans up the unwanted column of indexes from the smaller csv files
dfCompiled = dfCompiled.drop(dfCompiled.columns[0], axis=1)

#%%

manufacturers.clear()
artgs.clear()
descriptions.clear()
productIngredients.clear()


import pandas as pd

# results lists
compliancePoison = [] #comes from PoisonCheck fucntion
complianceARTG = [] #comes from CheckARTG function
therapueticClaims = [] #comes from CheckTherpeuticClaims function
complianceFinal = [] #comes from the ComplianceFinal function
complianceSystemGuess = [] #comes from the complianceSystemGuess function
complianceSystemCorrect = [] #coems from the ComplianceSystemCorrectness function

#need a loop here to go through all the files and collect 
#df = pd.read_csv('product_info.csv')

artgs = dfCompiled['ARTG'].to_list()
manufacturers = dfCompiled['Manufacturer'].to_list()
descriptions = dfCompiled['Description'].to_list()
productIngredients = dfCompiled['Ingredients'].to_list()

#%% Compliance checks

#ARTG Check artg number and manufacturer.
def CheckARTG():
    #copied the dataframe because it is a destructive method
    dfCompiledCopy = dfCompiled
    # Normalize manufacturer names in product_info dataframe
    dfCompiledCopy['Manufacturer'] = dfCompiledCopy['Manufacturer'].str.strip().str.lower()
    # Convert the product_info DataFrame to a list of dictionaries
    product_list = dfCompiledCopy.to_dict('records')
    #for i in range(len(artgs)):
    for product in product_list:
        #sets up variables for comparisons
        product_artg = product['ARTG']
        product_manufacturer = product['Manufacturer']
        
        if pd.isna(product_manufacturer) or not product_manufacturer.strip():
            #product does not have a manufacturer
            complianceARTG.append("non-compliant") 
        else:
            if pd.isna(product_artg) or not product_artg.strip():
                #product doesnt have an ARTG number
                complianceARTG.append("non-compliant") 
            else: 
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
def CheckPoison():
    for ingred in productIngredients:
        safe = CheckIngredients(ingred)
        if safe == True:
            compliancePoison.append("compliant")
        else:
            compliancePoison.append("non-compliant")

# checks descriptions against claim keywords
def CheckTherpeuticClaims():
    number_claims = []
    for descript in descriptions: #goes through each description
        descript = str(descript) #this works around the NaN that can occur when importing nothing in a cell
        descript = descript.lower() #this could be a problem for words like AIDS and aids have 2 different intentions/meanings
        #print(descript)
        bad_claims = 0
        for keyword in claimTerms: #goes through each keyword for each description 
            keyword = keyword.lower() # converts dictionary to lowercase
            if keyword in descript: # if keyword is in a description adds 1 to number of claims in number_claim variable
                bad_claims += 1 
        number_claims.append(bad_claims)
        if bad_claims >= 1:
            therapueticClaims.append("non-compliant")
        else:
            therapueticClaims.append("compliant")

def ComplianceFinal():
    complianceList = []
    i = 0
    while i < len(artgs):
        complianceList.append(compliancePoison[i])
        complianceList.append(complianceARTG[i])
        complianceList.append(therapueticClaims[i])
        if all(x == "compliant" for x in complianceList):
            complianceFinal.append("compliant")
        else:
            complianceFinal.append("non-compliant")
        i += 1
        #print(complianceList)
        complianceList.clear()
    #for temp in complianceFinal:
    #    print(temp)

def ComplianceSystemGuess():
    artgSponsorListTemp = [sponsor.lower() for sponsor in artgSponsorList]
    print(artgSponsorListTemp)
    for manufacturer in manufacturers:
        manufacturer = str(manufacturer).lower()
        if manufacturer in artgSponsorListTemp:
            complianceSystemGuess.append('compliant')
        else:
            complianceSystemGuess.append('non-compliant')

def ComplianceSystemCorrectness():
    i = 0
    while i < len(complianceSystemGuess):
        if complianceSystemGuess[i] == complianceFinal[i]:
            complianceSystemCorrect.append("Correct")
        else:
            complianceSystemCorrect.append("Incorrect")
        i += 1

#%%

#complete system checks
CheckARTG()
CheckPoison()
CheckTherpeuticClaims()
ComplianceFinal()
ComplianceSystemGuess()
ComplianceSystemCorrectness()

#add new columns and remove unwanted columns
dfCompiled['CompPoison'] = compliancePoison
dfCompiled['CompARTG'] = complianceARTG
dfCompiled['CompTherapueticClaims'] = therapueticClaims
dfCompiled['CompFinal'] = complianceFinal
dfCompiled['CompSystemGuess'] = complianceSystemGuess
dfCompiled['GuessOutcome'] = complianceSystemCorrect
#have to drop this column as its the indexes from the smaller files
dfCompiled = dfCompiled.drop(dfCompiled.columns[0], axis = 1)

#export csv file
CurrentTime = str(datetime.today().strftime('%Y-%m-%d'))
#print(CurrentTime)
dfCompiled.to_csv(SaveLocation + '/Results/'  + 'complete-results_' +  CurrentTime + '.csv')


#%%

#%% import packages
import pandas as pd
import numpy as np


dfCompiled = pd.read_csv(SaveLocation + '/Results/' + 'complete-results_2023-04-26.csv')
dfCompiled = dfCompiled.drop(dfCompiled.columns[0], axis = 1)

#%%
# find all the non-compliant products
finalOutput = dfCompiled.loc[dfCompiled.CompFinal == 'non-compliant', :]
CurrentTime = str(datetime.today().strftime('%Y-%m-%d'))
# export the final non-compliant products
finalOutput.to_csv(SaveLocation + '/Results/'  + 'non-compliant-results_' +  CurrentTime + '.csv')

# %%
