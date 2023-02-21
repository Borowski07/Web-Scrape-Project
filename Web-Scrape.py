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

URL= "https://www.amazon.com.au/"

#compile webdriver / browser for selenium to run
driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()))




# %%
