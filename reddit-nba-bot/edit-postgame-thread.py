# python3
# edit-postgame-thread.py by f1uk3r-- edit postgame thread created by OP with highlights from reddit and nba 
# pip install requests, praw, bs4, tabulate, pafy
import praw
import config
import requests
import json
from datetime import date, timedelta
import bs4, requests
import sys
from tabulate import tabulate
import pafy

#Team Dictionary helps to make urls for boxscore and for full-forms of abbrevation of teams
teamDict = {
  "ATL": ["Atlanta Hawks","01", "atlanta-hawks-", "/r/atlantahawks", "1610612737", "Hawks"],
  "BKN": ["Brooklyn Nets", "02", "boston-celtics-", "/r/bostonceltics", "1610612738", "Nets"],
  "BOS": ["Boston Celtics", "17", "brooklyn-nets-","/r/gonets", "1610612751", "Celtics"],
  "CHA": ["Charlotte Hornets", "30", "charlotte-hornets-","/r/charlottehornets", "1610612766", "Hornets"],
  "CHI": ["Chicago Bulls", "04", "chicago-bulls-","/r/chicagobulls", "1610612741", "Bulls"],
  "CLE": ["Cleveland Cavaliers", "05", "cleveland-cavaliers-","/r/clevelandcavs", "1610612739", "Cavaliers"],
  "DAL": ["Dallas Mavericks", "06", "dallas-mavericks-","/r/mavericks", "1610612742", "Mavericks"],
  "DEN": ["Denver Nuggets", "07", "denver-nuggets-","/r/denvernuggets", "1610612743", "Nuggets"],
  "DET": ["Detroit Pistons", "08", "detroit-pistons-", "/r/detroitpistons", "1610612765", "Pistons"],
  "GSW": ["Golden State Warriors", "09", "golden-state-warriors-", "/r/warriors", "1610612744", "Warriors"],
  "HOU": ["Houston Rockets", "10", "houston-rockets-", "/r/rockets", "1610612745", "Rockets"],
  "IND": ["Indiana Pacers", "11", "indiana-pacers-", "/r/pacers", "1610612754", "Pacers"],
  "LAC": ["Los Angeles Clippers", "12", "los-angeles-clippers-", "/r/laclippers", "1610612746", "Clippers"],
  "LAL": ["Los Angeles Lakers", "13", "los-angeles-lakers-", "/r/lakers", "1610612747", "Lakers"],
  "MEM": ["Memphis Grizzlies", "29", "memphis-grizzlies-", "/r/memphisgrizzlies", "1610612763", "Grizzlies"],
  "MIA": ["Miami Heat", "14", "miami-heat-", "/r/heat", "1610612748", "Heat"],
  "MIL": ["Milwaukee Bucks", "15", "milwaukee-bucks-", "/r/mkebucks", "1610612749", "Bucks"],
  "MIN": ["Minnesota Timberwolves", "16", "minnesota-timberwolves-", "/r/timberwolves", "1610612750", "Timberwolves"],
  "NOP": ["New Orleans Pelicans", "03", "new-orleans-pelicans-", "/r/nolapelicans", "1610612740", "Pelicans"],
  "NYK": ["New York Knicks", "18", "new-york-knicks-", "/r/nyknicks", "1610612752", "Knicks"],
  "OKC": ["Oklahoma City Thunder", "25", "oklahoma-city-thunder-", "/r/thunder", "1610612760", "Thunder"],
  "ORL": ["Orlando Magic", "19", "orlando-magic-", "/r/orlandomagic", "1610612753", "Magic"],
  "PHI": ["Philadelphia 76ers", "20", "philadelphia-76ers-", "/r/sixers", "1610612755", "76ers"],
  "PHX": ["Phoenix Suns", "21", "phoenix-suns-", "/r/suns", "1610612756", "Suns"],
  "POR": ["Portland Trail Blazers", "22", "portland-trail-blazers-", "/r/ripcity", "1610612757", "Trail Blazers"],
  "SAC": ["Sacramento Kings", "23", "sacramento-kings-", "/r/kings", "1610612758", "Kings"],
  "SAS": ["San Antonio Spurs", "24", "san-antonio-spurs-", "/r/nbaspurs", "1610612759", "Spurs"],
  "TOR": ["Toronto Raptors", "28", "toronto-raptors-", "/r/torontoraptors", "1610612761", "Raptors"],
  "UTA": ["Utah Jazz", "26", "utah-jazz-", "/r/utahjazz", "1610612762", "Jazz"],
  "WAS": ["Washington Wizards", "27", "washington-wizards-", "/r/washingtonwizards", "1610612764, ", "Wizards"]
}

#Save the name of Channel and link in the list here
allChannels = [
  ['MLG Highlights', 'https://www.youtube.com/channel/UCoh_z6QB0AGB1oxWufvbDUg'],
  ['Moar Highlights', 'https://www.youtube.com/channel/UCeW4gzPrv1sHkXyKQgQGRFw'],
  ['House of Highlights', 'https://www.youtube.com/channel/UCqQo7ewe87aYAe7ub5UqXMw'],
  ['FreeDawkins', 'https://www.youtube.com/channel/UCEjOSbbaOfgnfRODEEMYlCw'], 
  ['DownToBuck', 'https://www.youtube.com/channel/UCNaGVvWvXaYI16vAxQUfq3g']
  ]

reddit = praw.Reddit(username = config.username, 
                    password = config.password,
                    client_id = config.client_id, 
                    client_secret = config.client_secret,
                    user_agent = "script:rnba-post-game-thread-bot:v2.0 (by /u/f1uk3r)")

def requestApi(url):
  req = requests.get(url)
  return req.json()

#finding date of games
now = date.today() - timedelta(0)
date = now.strftime("%Y%m%d") #check the date before using script
dateTitle = now.strftime("%B %d, %Y")
#print(date)

#getting today's game
data = requestApi("http://data.nba.net/prod/v1/" + date + "/scoreboard.json")
gamesToday = data["numGames"]
games = data["games"]

responseList = []

for submission in reddit.subreddit('test').search("post game thread", sort="new", time_filter="day"):
    if submission.author.name == "f1uk3r":
      responseList.append(submission)

if len(responseList) == 1:
  response = responseList[0]
else:
  for i in range(len(responseList)):
    print(str(i) + " " + responseList[i].title)
  
  game = int(input("Choose the Post Game Thread you want to edit: "))

  if game in range(len(responseList)):
    response = responseList[game]

highlightList = []
requiredHighlightList = []
for submission in reddit.subreddit('nba').search("site:streamable.com", sort="new", time_filter="day"):
  highlightList.append(submission)

for i in range(len(highlightList)):
  print(str(i) + " " + highlightList[i].title)

s = input("Choose the highlights(s) (by index) you want to add in Post Game Thread: ")
highlightIndexList = list(map(int, s.split()))

for each in highlightIndexList:
  requiredHighlightList.append(highlightList[each])

youtubeHighlightList = []
#Number of videos to list; Keep it less than 30
listVid = 15
#Dictionary for non bmp characters
non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)

print("List of Channels:")

for i in range(len(allChannels)):
	print(str(i+1) + ". " + str(allChannels[i][0]))
channelIndex = 1
while channelIndex != 0:
  channelIndex = int(input("Choose one of the channel by index number(Press 0 to exit): "))
  if channelIndex > 0 and channelIndex < (len(allChannels) + 1):
    res = requests.get(str(allChannels[channelIndex - 1][1]) + '/videos')
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    allVids = soup.findAll('div', {'class':'yt-lockup-content'})
    wantedVids = allVids[:listVid]
    vidTitles = []
    vidLinks = []
    vidDuration = []
    vidUploaded = []
    for each in wantedVids:
      vidATag = each.find('a')
      vidSpanTag = each.find('span')
      vidLiTag = each.findAll('li')
      vidTitles.append(str(vidATag.text).translate(non_bmp_map))
      vidLinks.append("https://youtube.com" + str(vidATag['href']))
      vidDuration.append(str(vidSpanTag.text).replace("- Duration: ", ""))
      vidUploaded.append(vidLiTag[1].text)
    vidIndex = range(1, listVid + 1)
    header = ["Index", "Title", "Duration", "Uploaded"]
    table = zip(vidIndex, vidTitles, vidDuration, vidUploaded)
    print(tabulate((table), header, tablefmt="grid"))
    # this will make a list of space seperated value (for eg. 5 4 2 1) and download in that order
    choosenVids = list(map(int, input("Enter index of all videos you want to download(Space seperated values): ").split()))
    for each in choosenVids:
      if int(each)>listVid or int(each)<1:
        print("Index out of bound")
      else:
        url = str(vidLinks[int(each-1)])
        title = str(vidTitles[int(each-1)])
        uploader = allChannels[channelIndex - 1][0]
        youtubeHighlightList.append([url, title, uploader])
        
  elif channelIndex == 0:
    print("Thanks")
  else:
    print("Please choose a number from the index or press 0 to exit") 

body = '''###Game Highlights:

- [**Full Game Highlights**]({0})

    Source: {1}'''.format(str(youtubeHighlightList[0][0]), str(youtubeHighlightList[0][2]))

for i in range(1, len(youtubeHighlightList)):
  body += '''

- [**{0}**]({1})  

    Source: {2}'''.format(str(youtubeHighlightList[i][1]), str(youtubeHighlightList[i][0]), str(youtubeHighlightList[i][2]))

body += '''

###Play Highlights:

'''

for each in requiredHighlightList:
  body += '''- [**{0}**]({1}) 
 
    [Source](https://www.reddit.com{2}): /u/{3}

'''.format(each.title, each.url, each.permalink, each.author)

body += response.selftext

response.edit(body)
