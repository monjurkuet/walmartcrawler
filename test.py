import undetected_chromedriver as uc
import random
import sqlite3
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import platform
import re
from tqdm import tqdm

# Constants for file paths
#BROWSER_EXECUTABLE_PATH_WINDOWS = 'C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe'
BROWSER_EXECUTABLE_PATH_WINDOWS = "C:\\Users\\muham\\AppData\\Local\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
BROWSER_EXECUTABLE_PATH_LINUX = '/usr/bin/brave-browser'

def new_browser():
    options = uc.ChromeOptions()
    caps = options.to_capabilities()
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}
    SYSTEM_OS = platform.system()
    browser_executable_path = (
        BROWSER_EXECUTABLE_PATH_WINDOWS if SYSTEM_OS == 'Windows' else BROWSER_EXECUTABLE_PATH_LINUX
    )
    driver = uc.Chrome(
        browser_executable_path=browser_executable_path,
        headless=False,
        options=options,
        desired_capabilities=caps
    )
    return driver

def extract_products(driver):
    all_products=driver.find_elements(By.XPATH,'//div[@data-item-id and @role="group"]')
    for product in all_products:
        Product_Link=product.find_element(By.XPATH,'.//a[@link-identifier]').get_attribute('href').split('?')[0]
        Title=product.find_element(By.XPATH,'.//span[@data-automation-id="product-title"]').text
        Current_Price=product.find_element(By.XPATH,'.//span[contains(text(),"current price")]').text
        Current_Price=re.search("\$[0-9]+(\.[0-9]+)?",Current_Price)[0]
        try:
            Original_Price=product.find_element(By.XPATH,'.//span[contains(text(),"Was $")]').text.split(' ')[-1]
        except:
            Original_Price=None
        print(Original_Price)
        Source_Link=SEARCH_URL
        Image_Link=product.find_element(By.XPATH,'.//img').get_attribute('src').split('?')[0]
        cursor.execute('''REPLACE INTO productlist (Source_Link, Title, Original_Price, Current_Price, Product_Link, Image_Link)
                    VALUES (?, ?, ?, ?, ?, ?)''',
                    (Source_Link, Title, Original_Price, Current_Price, Product_Link, Image_Link))
        print(Title,Current_Price)
    conn.commit()

def solve_blocked(browser):
    try:
        element = WebDriverWait(browser,15).until(EC.presence_of_element_located((By.ID,'px-captcha')))
        # Wait for the px-captcha element styles to fully load
        time.sleep(0.5)
    except BaseException as e:
        print(f'px-captcha element not found')
        return
    print(f'solve blocked:{browser.current_url}')
    if  element:
        print(f'start press and hold')
        ActionChains(browser).click_and_hold(element).perform()
        start_time = time.time()
        while 1:
            if time.time() - start_time > random.uniform(6,10):
                ActionChains(browser).release(element).perform()
                return
            time.sleep(0.1)
    time.sleep(1)

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

SEARCH_URL=f'https://www.walmart.com/browse/party-occasions/character-party-supplies/2637_8253261'+'?sort=best_seller&facet=retailer_type%3AWalmart'+'&page={PAGE}'

driver=new_browser()
PAGE=1
driver.get(SEARCH_URL.format(PAGE=PAGE))
last_page=int(driver.find_elements(By.XPATH,'//nav[@aria-label="pagination"]//li')[-2].text)

for PAGE in tqdm(range(1,last_page+1)):
    driver.get(SEARCH_URL.format(PAGE=PAGE))
    extract_products(driver)
    time.sleep(5)

solve_blocked(driver)

conn.close()