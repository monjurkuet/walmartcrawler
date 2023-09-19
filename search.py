import undetected_chromedriver as uc
import json
import sqlite3
import time

def GetDriver():
   options = uc.ChromeOptions() 
   options.add_argument('--proxy-server=127.0.0.1:24000')
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

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

SEARCH_URL='https://www.walmart.com/browse/party-occasions/character-party-supplies/2637_8253261'+'?sort=best_seller&facet=retailer_type%3AWalmart'
SEARCH_API_URL='https://www.walmart.com/orchestra/snb/graphql/Browse/'

driver=GetDriver()
driver.set_window_position(-2000,0)
driver.get(SEARCH_URL)
ExtractData(driver,SEARCH_URL)

conn.close()