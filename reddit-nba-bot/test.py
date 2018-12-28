import praw
import config
import requests
import json
from datetime import date, timedelta
import datetime

reddit = praw.Reddit(username = config.username, 
                    password = config.password,
                    client_id = config.client_id, 
                    client_secret = config.client_secret,
                    user_agent = "Just browsing through r/nba (by /u/f1uk3r)")

allPosts = []
postTime = []

for submission in reddit.subreddit('nba').search("post game thread", sort='top'):
  date = datetime.datetime.fromtimestamp(submission.created_utc)
  dif = datetime.datetime.utcnow() - date
  if dif<datetime.timedelta(days=1000):
    allPosts.append(submission)

for each in allPosts:
  date = datetime.datetime.fromtimestamp(each.created_utc)
  dif = datetime.datetime.utcnow() - date
  postTime.append(dif)

for i in range(len(allPosts)):
  print(str(postTime[i]) + "  " + str(allPosts[i]) + "  " + allPosts[i].title + "/n")