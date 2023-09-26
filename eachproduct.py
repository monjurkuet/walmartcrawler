import undetected_chromedriver as uc
import sqlite3
import time
import re
import platform
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm
import random

WEBDRIVERCOUNTER=0

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

driver=new_browser()

pattern = r'"upc":"(.*?)"'
categorypattern = r'"categoryName":"(.*?)"'

# Execute the query
cursor.execute("SELECT Product_Link,productid FROM productlist WHERE productid NOT IN (SELECT productid FROM productdetails)")
# Fetch all the rows
rows = [{'Product_Link':i[0],'productid':i[1]} for i in cursor.fetchall()]

for data in tqdm(rows):
   Product_Link=data['Product_Link']
   productid=data['productid']
   driver.get(Product_Link)
   check_captcha(driver,Product_Link)
   try:
      UPC = re.search(pattern, driver.page_source).group(1)
   except:
      UPC=None
   try:
      Category=re.search(categorypattern, driver.page_source).group(1).encode('latin1').decode('unicode_escape')
   except:
      Category=None
   # Execute the query
   cursor.execute("INSERT OR IGNORE INTO productdetails (productid, Category, UPC) VALUES (?, ?, ?)", 
               (productid, Category, UPC))
   conn.commit()
   print(f'Crawled : {productid} {Category}')
   time.sleep(random.uniform(1,5))
   WEBDRIVERCOUNTER+=1
   if WEBDRIVERCOUNTER==100:
      driver.quit()
      driver=new_browser()
      WEBDRIVERCOUNTER=0

conn.close()