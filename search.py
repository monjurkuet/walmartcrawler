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

def samelineprint(msg):
   LINE_FLUSH = '\r\033[K'
   UP_FRONT_LINE = '\033[F'
   print(UP_FRONT_LINE + LINE_FLUSH + str(msg))

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

def extract_products(driver,Source_Link):
    all_products=driver.find_elements(By.XPATH,'//div[@data-item-id and @role="group"]')
    for product in all_products:
        Product_Link=product.find_element(By.XPATH,'.//a[@link-identifier]').get_attribute('href').split('?')[0]
        Title=product.find_element(By.XPATH,'.//span[@data-automation-id="product-title"]').text
        try:
            Current_Price=product.find_element(By.XPATH,'.//span[contains(text(),"current price")]').text
            Current_Price=re.search("\$[0-9]+(\.[0-9]+)?",Current_Price)[0]
        except:
            Current_Price=None
        try:
            Original_Price=product.find_element(By.XPATH,'.//span[contains(text(),"Was $")]').text.split(' ')[-1]
        except:
            Original_Price=None
        Image_Link=product.find_element(By.XPATH,'.//img').get_attribute('src').split('?')[0]
        productid=product.find_element(By.XPATH,'.//a[@link-identifier]').get_attribute('link-identifier')
        cursor.execute('''REPLACE INTO productlist (Source_Link, Title, Original_Price, Current_Price, Product_Link, Image_Link,productid)
                    VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (Source_Link, Title, Original_Price, Current_Price, Product_Link, Image_Link,productid))
        samelineprint(Title+' '+productid)
    conn.commit()

def solve_blocked(browser):
    try:
        element = WebDriverWait(browser,15).until(EC.presence_of_element_located((By.ID,'px-captcha')))
        # Wait for the px-captcha element styles to fully load
        time.sleep(0.5)
    except BaseException as e:
        samelineprint(f'px-captcha element not found')
        return
    samelineprint(f'solve blocked:{browser.current_url}')
    if  element:
        samelineprint(f'start press and hold')
        ActionChains(browser).click_and_hold(element).perform()
        start_time = time.time()
        while 1:
            if time.time() - start_time > random.uniform(6,10):
                ActionChains(browser).release(element).perform()
                return
            time.sleep(0.1)
    time.sleep(1)

def check_captcha(driver,url):
    captchapresence=len(driver.find_elements(By.ID,'px-captcha'))
    if not captchapresence:
        return
    solve_blocked(driver)
    time.sleep(5)
    driver.get(url)
    time.sleep(5)
    check_captcha(driver,url)

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

with open('categories.txt') as f:
    categories = f.read().splitlines()

#driver=new_browser()

for category_url in tqdm(categories[1:]):
    #driver=new_browser()
    category_url=category_url.rstrip('/')
    samelineprint(f'Crawling : {category_url}')
    searchurl=f'{category_url}'+'?sort=best_seller&facet=retailer_type%3AWalmart'
    driver.get(searchurl)
    check_captcha(driver,searchurl)
    last_page=int(driver.find_elements(By.XPATH,'//nav[@aria-label="pagination"]//li')[-2].text)
    for PAGE in tqdm(range(1,last_page+1)):
        SEARCH_BASE_URL=f'{category_url}'+'?sort=best_seller&facet=retailer_type%3AWalmart'+'&page='+str(PAGE)
        BASE_URL=SEARCH_BASE_URL.format(PAGE=PAGE,category_url=category_url)
        samelineprint(f'Crawling : {BASE_URL}')
        driver.get(BASE_URL)
        check_captcha(driver,BASE_URL)
        extract_products(driver,BASE_URL)
        time.sleep(5)
    driver.quit()

conn.close()