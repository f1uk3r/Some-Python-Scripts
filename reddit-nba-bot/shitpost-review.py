import praw
import config_reddit
import requests
import json
from datetime import date, timedelta, datetime
import random
import csv

def requestApi(url):
  req = requests.get(url)
  return req.json()

a = 2
b = 0
dataTable = []
dummy = "https://api.pushshift.io/reddit/search/submission/?subreddit=nba&size=250&sort=desc&domain=self.nba&sort_type=score&filter=selftext,title,num_comments,score,url&after={0}y&before={1}y".format(str(a), str(b))

while (a < 10):
  rawData = requestApi(dummy)
  for each in rawData["data"]:
    dataTable.append([each["title"],each["score"],each["num_comments"],each["url"]])
  a += 2
  b += 2

with open('rawData.csv', 'w') as csvFile:
    writer = csv.writer(csvFile)
    writer.writerows(dataTable)
csvFile.close()