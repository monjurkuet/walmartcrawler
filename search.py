import undetected_chromedriver as uc
import json
import sqlite3
import time
import cv2
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from io import BytesIO
from PIL import Image
import numpy as np

def GetDriver():
   options = uc.ChromeOptions() 
   caps = options.to_capabilities()
   caps['goog:loggingPrefs'] = {'performance': 'ALL'} 
   return uc.Chrome(headless=False,options=options,desired_capabilities=caps) 

def clean_logs(driver,logs,target_url):
   for log in logs:
      try:
         resp_url = log["params"]["response"]["url"]
         if target_url in resp_url:
               request_id = log["params"]["requestId"]
               response_body=driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})
               response_json=json.loads(response_body['body'])
               return response_json
      except:
         pass   
   return None

def ExtractData(driver,SEARCH_URL):
   logs_raw = driver.get_log("performance")     
   logs = [json.loads(lr["message"])["message"] for lr in logs_raw]
   response_json=clean_logs(driver,logs,SEARCH_API_URL)
   searchResults=response_json['data']['search']['searchResult']['itemStacks'][0]['itemsV2']
   for eachProduct in searchResults:
      if eachProduct['__typename']=='Product':
         Source_Link=SEARCH_URL
         Title=eachProduct['name']
         Original_Price=None
         if eachProduct['priceInfo']['listPrice'] is not None:
            Original_Price=eachProduct['priceInfo']['listPrice']['price']
         Current_Price=None
         if eachProduct['priceInfo']['currentPrice'] is not None:
            Current_Price=eachProduct['priceInfo']['currentPrice']['price']
         Product_Link='https://www.walmart.com'+eachProduct['canonicalUrl']
         Image_Link=eachProduct['imageInfo']['thumbnailUrl'].split('?')[0]
         # Insert the data into the "productlist" table
         cursor.execute('''INSERT OR IGNORE INTO productlist (Source_Link, Title, Original_Price, Current_Price, Product_Link, Image_Link)
                  VALUES (?, ?, ?, ?, ?, ?)''',
                  (Source_Link, Title, Original_Price, Current_Price, Product_Link, Image_Link))
         print(Title,Current_Price)
   driver.get_log("performance")  
   conn.commit()

pixelRatio = 2
def solve_blocked(browser, retry=3):
    '''
    Solve blocked
    (Cross-domain iframe cannot get elements temporarily)
    Simulate the mouse press and hold to complete the verification
    '''
    if not retry:
        return False
    element = None
    try:
        element = WebDriverWait(browser,15).until(EC.presence_of_element_located((By.ID,'px-captcha')))
        # Wait for the px-captcha element styles to fully load
        time.sleep(0.5)
    except BaseException as e:
        print(f'px-captcha element not found')
        return
    print(f'solve blocked:{browser.current_url}, Retry {retry} remaining times')
    template = cv2.imread(('captcha.png'), 0)
    # Set the minimum number of feature points to match value 10
    MIN_MATCH_COUNT = 8 
    if  element:
        print(f'start press and hold')
        ActionChains(browser).click_and_hold(element).perform()
        start_time = time.time()
        while 1:
            if time.time() - start_time > 20:
                break
            x, y = element.location['x'], element.location['y']
            width, height = element.size.get('width'), element.size.get('height')                
            left = x * pixelRatio
            top = y * pixelRatio
            right = (x+width) * pixelRatio
            bottom = (y+height) * pixelRatio
            png = browser.get_screenshot_as_png() 
            im = Image.open(BytesIO(png))
            im = im.crop((left, top, right, bottom)) 
            target = cv2.cvtColor(np.asarray(im),cv2.COLOR_RGB2BGR)  
            # Initiate SIFT detector
            sift = cv2.SIFT_create()
            # find the keypoints and descriptors with SIFT
            kp1, des1 = sift.detectAndCompute(template,None)
            kp2, des2 = sift.detectAndCompute(target,None)
            # create set FLANN match
            FLANN_INDEX_KDTREE = 0
            index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
            search_params = dict(checks = 50)
            flann = cv2.FlannBasedMatcher(index_params, search_params)
            matches = flann.knnMatch(des1,des2,k=2)
            # store all the good matches as per Lowe's ratio test.
            good = []
            # Discard matches greater than 0.7
            for m,n in matches:
                if m.distance < 0.7*n.distance:
                    good.append(m)
            print( "Not enough matches are found - %d/%d" % (len(good),MIN_MATCH_COUNT))
            if len(good)>=MIN_MATCH_COUNT:
                print(f'release button')
                ActionChains(browser).release(element).perform()
                return
            time.sleep(0.5)
    time.sleep(1)
    retry -= 1
    solve_blocked(retry)

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

SEARCH_URL='https://www.walmart.com/browse/party-occasions/character-party-supplies/2637_8253261'+'?sort=best_seller&facet=retailer_type%3AWalmart'
SEARCH_API_URL='https://www.walmart.com/orchestra/snb/graphql/Browse/'

driver=GetDriver()
driver.set_window_position(-2000,0)
driver.get(SEARCH_URL)
ExtractData(driver,SEARCH_URL)
solve_blocked(driver)
conn.close()