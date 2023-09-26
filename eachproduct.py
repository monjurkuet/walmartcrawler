import undetected_chromedriver as uc
import sqlite3
import time
import re

def samelineprint(msg):
   LINE_FLUSH = '\r\033[K'
   UP_FRONT_LINE = '\033[F'
   return(UP_FRONT_LINE + LINE_FLUSH + str(msg))

def GetDriver():
   options = uc.ChromeOptions() 
   caps = options.to_capabilities()
   caps['goog:loggingPrefs'] = {'performance': 'ALL'} 
   return uc.Chrome(headless=False,options=options,desired_capabilities=caps) 


conn = sqlite3.connect('database.db')
cursor = conn.cursor()

driver=GetDriver()

pattern = r'"upc":"(.*?)"'
categorypattern = r'"categoryName":"(.*?)"'

# Execute the query
cursor.execute("SELECT Product_Link FROM productlist WHERE Product_Link NOT IN (SELECT Product_Link FROM productdetails)")
# Fetch all the rows
rows = [i[0] for i in cursor.fetchall()]

for Product_Link in rows:
   driver.get(Product_Link)
   UPC = re.search(pattern, driver.page_source).group(1)
   Category=re.search(categorypattern, driver.page_source).group(1).encode('latin1').decode('unicode_escape')
   # Execute the query
   cursor.execute("INSERT INTO productdetails (Product_Link, Category, UPC) VALUES (?, ?, ?)", 
               (Product_Link, Category, UPC))
   conn.commit()
   print(UPC,Category)

conn.close()