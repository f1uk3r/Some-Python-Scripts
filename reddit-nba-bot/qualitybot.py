import praw
import urllib
import requests
import json
import time
import config

def requestApi(url):
  req = requests.get(url)
  return req.json()

reddit = praw.Reddit(username = config.username, 
                    password = config.password,
                    client_id = config.client_id, 
                    client_secret = config.client_secret,
                    user_agent = "quality check")

streamableAPI = 'https://api.streamable.com/videos/'
gfycatAPI = 'https://api.gfycat.com/v1/gfycats/'

subreddit = reddit.subreddit('nba')

for submission in subreddit.stream.submissions():
  if 'gfycat' in submission.url:
    gfycatCode = submission.url.replace('https://gfycat.com/', '')
    gfycatApiUrl = gfycatAPI + gfycatCode
    gfycatJson = requestApi(gfycatApiUrl)
    framerate = str(gfycatJson['gfyItem']['frameRate'])
    width = str(gfycatJson['gfyItem']['width'])
    height = str(gfycatJson['gfyItem']['height'])
#    print(submission.shortlink + ', ' + submission.url + ', ' + framerate + ', ' + width + ', ' + height)
    if int(float(framerate)) < 24 or int(width) < 1000:
      if submission.approved_by == None and len(submission.report_reasons) == 0: 
          reportReason = 'Low Quality - ' + width + 'x' + height + ', ' + framerate + 'fps'
          print(reportReason)
          submission.report(reportReason)

  elif 'streamable' in submission.url:
    streamableCode = submission.url.replace('https://streamable.com/', '')
    streamableApiUrl = streamableAPI + streamableCode
    streamableJson = requestApi(streamableApiUrl)
    framerate = str(streamableJson['files']['mp4']['framerate'])
    bitrate = str(streamableJson['files']['mp4']['bitrate'])
    width = str(streamableJson['files']['mp4']['width'])
    height = str(streamableJson['files']['mp4']['height'])
#    print(submission.shortlink + ', ' + submission.url + ', ' + framerate + ', ' + bitrate + ', ' + width + ', ' + height)
    if int(framerate) < 24 or int(bitrate) <= 950000 or int(width) < 1000:
      if submission.approved_by == None and len(submission.report_reasons) == 0: 
          reportReason = 'Low Quality - ' + width + 'x' + height + ', ' + str(int(round(int(bitrate), -5)/1000)) + 'kbps, ' + framerate + 'fps'
          print(reportReason)
          submission.report(reportReason)