import undetected_chromedriver as uc
import json
import sqlite3
import time

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

def ExtractData(driver):
   logs_raw = driver.get_log("performance")     
   logs = [json.loads(lr["message"])["message"] for lr in logs_raw]
   response_json=clean_logs(driver,logs,SEARCH_API_URL)
   searchResults=response_json['searchResults']['jobs']
   for eachJob in searchResults:
      title=eachJob['title']
      createdOn=eachJob['createdOn']
      amount=eachJob['amount']['amount']
      skillList=', '.join(i['prettyName'] for i in eachJob['attrs'])
      description=eachJob['description']
      hourlyBudget=f"{eachJob['hourlyBudget']['min']}-{eachJob['hourlyBudget']['max']}"
      duration=eachJob['duration']
      engagement=eachJob['engagement']
      enterpriseJob=eachJob['enterpriseJob']
      category=f"{eachJob['occupations']['category']['prefLabel']}, {eachJob['occupations']['oservice']['prefLabel']}, {', '.join(i['prefLabel'] for i in eachJob['occupations']['subcategories'])}"
      ciphertext=eachJob['ciphertext']
      # Insert the data into the "PostedJobs" table
      cursor.execute('''INSERT OR IGNORE INTO PostedJobs (title, createdOn, amount, skillList, description, hourlyBudget, duration, engagement, enterpriseJob, category, ciphertext)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     (title, createdOn, amount, skillList, description, hourlyBudget, duration, engagement, enterpriseJob, category, ciphertext))
      print(title, createdOn, amount, skillList, hourlyBudget, duration, engagement)
   driver.get_log("performance")  
   conn.commit()

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

SEARCH_URL='https://www.upwork.com/nx/jobs/search/?sort=recency&or_terms=scrape%20crawl'
SEARCH_API_URL='https://www.upwork.com/search/jobs/url'

while True:
   driver=GetDriver()
   driver.set_window_position(-2000,0)
   for i in range(1,5):
      try:
         driver.get(SEARCH_URL+f'&page={i}')
         print(f'Crawling : {SEARCH_URL}+&page={i}')
         time.sleep(5)
         if i==1:
            driver.find_element('xpath','//div[@class="up-dropdown jobs-per-page"]').click()
            time.sleep(5)
            driver.find_elements('xpath','//div[@class="up-dropdown-menu"]//li')[-1].click()
            time.sleep(5)
         ExtractData(driver)
         time.sleep(5)
      except Exception as e:
         print(e)
         input('Enter to continue.....')
   print('Sleeping........')
   driver.quit()
   time.sleep(300)

conn.close()