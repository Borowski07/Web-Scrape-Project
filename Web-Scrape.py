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

#%% Selenium Driver Setup (chrome window)

#url variable, used to call what webpage to visit
URL= ""

#compile webdriver / browser for selenium to run
driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()))


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




#%% go to product page


#loop through all the products
for link in hrefs:
    #Loads the product page using hyperlink from the resulkts page
    driver.get(link)
    #collect name of product
    name = driver.find_element(By.ID, "productTitle").text
    print(name)
    
    #collect ingredients
    #ingredients = driver.find_element()
    #print(ingredients)
    
    #find seller
    # //*[@class="tabular-buybox-container"] top box
    # //*[@class="tabular-buybox-text"][2] more specific
    seller = driver.find_element(By.XPATH, "//*[@class='tabular-buybox-text'][2]").text
    if seller == "":
        #get seller a different way becuase amazon offers recurring purchase options and thus has a different layout.
        seller = driver.find_element(By.XPATH, "//*[@id='sfsb_accordion_head']//div[2]//div//span[2]").text
    print(seller)
    
    #collect product infromation under the "about this item" section
    writtentext = []
    featuresList = driver.find_elements(By.XPATH, "//*[@id='feature-bullets']//li/span")
    for ft in featuresList:
        writtentext.append(ft.text)
    writtentext.append(driver.find_element(By.XPATH, "//*[@id='productDescription']/p/span").text)
    for text in writtentext:
        print(text)
    
    #manufacturer
    manufacturer = driver.find_element(By.XPATH, "//*[@id='detailBullets_feature_div']/ul/li[3]/span/span[2]").text
    print(manufacturer)

    #ASIN
    asin = driver.find_element(By.XPATH, "//*[@id='detailBullets_feature_div']/ul/li[4]/span/span[2]").text
    print(asin)

    print("-------------------------------------")
    time.sleep(3)


#%% collect image from page



#%% Output infromation to a csv file




#%% Wrapping up procedures

#just a timer, you could add whatever further functionality 
#after this point
time.sleep(100)

#closes the window
#driver.quit()

