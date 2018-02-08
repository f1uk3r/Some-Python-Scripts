import requests, bs4
import copy
from selenium import webdriver
import time
import os
url = str(input("Paste url you want to prettify: "))

res = requests.get(url)
soup = bs4.BeautifulSoup(res.text, 'html.parser')
print(soup.prettify)
time.sleep(5)									#time to copy html to clipboard
driver = webdriver.Chrome()
driver.get("https://www.freeformatter.com/html-formatter.html")
time.sleep(25)
driver.quit()

clear = lambda : os.system('tput reset')
clear()
