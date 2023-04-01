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

#%% Selenium Driver Setup (chrome window)

#url variable, used to call what webpage to visit
URL= ""

#read setting file for setup
#opens file in read mode
settingsFile = open("settings.txt", mode = "r")
lines = []
for line in settingsFile:
    lines.append(line)
    print(line)



#setting up where to save images etc.
prefs = {"downlaod.default_directory": lines[2]}
options = Options()
options.add_experimental_option("prefs", prefs)

#compile webdriver / browser for selenium to run
#driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()))
driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()), options = options)

# %% Open webpage and run start scraping

#starting with amazon webpage for scraping.
URL= "https://www.amazon.com.au/"

#navigates the empty chrome window to the url specified
driver.get(URL)

#wait so the website can load (possible problem with slower connections.)
time.sleep(3)

# find search bar to start searches
searchBar = driver.find_element(By.ID, "twotabsearchtextbox")

# we can update this section to take a list of search terms to check 
# from a txt file or something that can be editted externally.
searchTerm = "Vitamins & Supplements"

#input the current search term into the search box and send the enter key command
searchBar.send_keys(searchTerm)
searchBar.send_keys(Keys.ENTER)

#%% Collect products from the page

#wait so the website can load (possible problem with slower connections.)
time.sleep(2)

# XPATH for all the chunks that contain the hrefs
#//*[@class="a-link-normal s-no-outline"]
# find all the products on the page by using an XPATH search to find all 
products = driver.find_elements(By.XPATH, "//*[@class='a-link-normal s-no-outline']")

#%% Collect products from page

# this list will contain all the hyperlink references (hrefs) we find on the pages
hrefs = []

# loop through all the product elements and collect their href links.
for prod in products:
    print(prod.get_attribute("href"))
    #adds href link to end of list of links
    hrefs.append(prod.get_attribute("href"))


#%% go to next page of search




#%% set up lists for collected information

productName = [] #comes from Name function
hyperlinks = [] #comes from 'core" function
manufacturers = [] #comes from CollectAsinManufacturer function
sellers = [] #comes from ProductSeller function
asins = [] #comes from CollectAsinManufacturer function
keywords = [] #comes from 'core" function
artgs = [] #comes from OCR_Image function
descriptions = [] #comes from DescriptionText function
productIngredients = [] #comes from FindIngredients function
datesCollected = [] #comes from CollectDate fucntion
imageProofName = [] #comes from ProductScreenshot function
OcrResults = [] #comes from OCR_Image function


#%% Load all function

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
        print(img.get_attribute("src"))

    x = 0
    for imgRef in highResImgHrefs:   
        #going to image webpage 
        driver.get(imgRef)

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
    print(file + " deleting")
    os.remove(file)

# Collect name of product
def Name():
    name = driver.find_element(By.ID, "productTitle").text
    productName.append(name)
    print(name)

# Date collected
def CollectDate():
    date = str(datetime.today().strftime('%Y-%m-%d'))
    datesCollected.append(date)
    print(date)

# Collect ingredients
def FindIngredients():
    ingredName = "Ingredients:"
    try:
        #section = driver.find_element(By.ID, "important-information")
        #ingredients = driver.find_element()
        #find what section has the ingredients, its nmot always in the same position
        infoSections = driver.find_elements(By.XPATH, "//*[@id='important-information']/div/h4")
        
        #for infoSec in infoSections:
        #    print(infoSec.text)
        i = 0
        ingredients = ""
        for infoSec in infoSections:
            i += 1
            if infoSec.text == ingredName:
                if i == "1":
                    ingredients = driver.find_element(By.XPATH, "//*[@id='important-information']/div[1]/p").text
                elif i == "2":
                    ingredients = driver.find_element(By.XPATH, "//*[@id='important-information']/div[2]/p").text
                else:
                    ingredients = driver.find_element(By.XPATH, "//*[@id='important-information']/div[3]/p").text
                #position of ingredients in list at i index
                #//*[@id='important-information']/div[i]/p[2]
                #dynamicXPath = "//*[@id='important-information']/div[" + i + "]/p"
                #print(dynamicXPath)
                #ingredients = driver.find_elements(By.XPATH, dynamicXPath).text
                print(ingredients)
    except:
        print("---- no ingredients listed ----")
    productIngredients.append(ingredients)

# Find seller
def ProductSeller():
    # //*[@class="tabular-buybox-container"] top box
    # //*[@class="tabular-buybox-text"][2] more specific
    seller = driver.find_element(By.XPATH, "//*[@class='tabular-buybox-text'][2]").text
    if seller == "":
        #get seller a different way becuase amazon offers recurring purchase options and thus has a different layout.
        seller = driver.find_element(By.XPATH, "//*[@id='sfsb_accordion_head']//div[2]//div//span[2]").text
    print(seller)
    sellers.append(seller)

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
    print(manufacturer)
    manufacturers.append(manufacturer)
    print(asin)
    asins.append(asin)

# Collect screenshot of product screen
def ProductScreenshot(tally):
    #formats the number to be a 6 digit number eg 1 will be 000001
    number = "{0:0=6d}".format(tally)
    #create the output name
    screenshotName = "proof"+ number + ".png"
    outputLocation = "Product Screenshots/"+ screenshotName
    print(outputLocation)
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
        print(ocr_result)
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
            startIndex = ocr_result.find("AUST R")
            endIndex = startIndex + 13
            ARTG_R = ocr_result[startIndex:endIndex].strip()
        except:
            ARTG_R = ""
        artgFinal = ARTG_L + " " +ARTG_R
        print(artgFinal)
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
        print("---- no description section ----")

    for text in writtentext:
        print(text)
    textOutput = ""
    for txt in writtentext:
        textOutput = textOutput + txt
    descriptions.append(textOutput)
    


#%% go to product page

#Counting the number of products
n = 0

#loop through all the products
for link in hrefs:
    #Loads the product page using hyperlink from the resulkts page
    driver.get(link)
    hyperlinks.append(link)
    #wait for page to load
    time.sleep(3)

    Name() #collect name of product
    FindIngredients() #collect ingredients
    
    #------------------problem like this needs a solution---------------------
    #https://www.amazon.com.au/Swisse-Ultiboost-Vitamin-0-202-Kilograms/dp/B013JKSIUG/ref=sr_1_46?keywords=Vitamins%2B%26%2BSupplements&qid=1680339856&sr=8-46&th=1
    #---------------------------------------
    ProductSeller() #find seller

    DescriptionText() #collect product infromation under the "about this item" section
    CollectAsinManufacturer() #manufacturer and ASIN

    #keyword search
    print(searchTerm)
    keywords.append(searchTerm)

    CollectDate() #date collected
    ProductScreenshot(n) #proof screenshot
    ImageCollection() #images from product thumbnails 
    OCR_Image() #run OCR on images to extract text

    
    print("-------------------------------------")
    time.sleep(1)
    n = n + 1





#%% Output infromation to a csv file




#%% Wrapping up procedures

#just a timer, you could add whatever further functionality 
#after this point
time.sleep(100)

#closes the window
#driver.quit()

