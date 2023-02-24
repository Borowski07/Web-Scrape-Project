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

# find search bar to start searches
searchBar = driver.find_element(By.ID, "twotabsearchtextbox")

# we can update this section to take a list of search terms to check 
# from a txt file or something that can be editted externally.
searchTerm = "Vitamins & Supplements"

#input the current search term into the search box and send the enter key command
searchBar.send_keys(searchTerm)
searchBar.send_keys(Keys.ENTER)

#%% Collect products from the page

# XPATH for all the chunks that contain the hrefs
#//*[@class="a-link-normal s-no-outline"]

# find all the products on the page by using an XPATH search to find all 
products = driver.find_elements(By.XPATH, "//*[@class='a-link-normal s-no-outline']")

#%%  collect products from page

# this list will contain all the hyperlink references (hrefs) we find on the pages
hrefs = []

# loop through all the product elements and collect their href links.
for prod in products:
    print(prod.get_attribute("href"))
    #adds href link to end of list of links
    hrefs.append(prod.get_attribute("href"))


#%% go to next page of search




#%% go to product page




#%% collect image from page



#%% Output infromation to a csv file




#%% Wrapping up procedures

#just a timer, you could add whatever further functionality 
#after this point
time.sleep(100)

#closes the window
#driver.quit()

