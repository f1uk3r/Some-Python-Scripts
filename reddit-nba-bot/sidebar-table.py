import config
import requests
import json
import praw
from datetime import date, timedelta
from tabulate import tabulate

#Team Dictionary helps to make urls for boxscore and for full-forms of abbrevation of teams
teamDict = {
  "ATL": ["Atlanta Hawks","01", "atlanta-hawks-", "/r/atlantahawks", "1610612737"],
  "BKN": ["Brooklyn Nets", "02", "boston-celtics-", "/r/bostonceltics", "1610612738"],
  "BOS": ["Boston Celtics", "17", "brooklyn-nets-","/r/gonets", "1610612751"],
  "CHA": ["Charlotte Hornets", "30", "charlotte-hornets-","/r/charlottehornets", "1610612766"],
  "CHI": ["Chicago Bulls", "04", "chicago-bulls-","/r/chicagobulls", "1610612741"],
  "CLE": ["Cleveland Cavaliers", "05", "cleveland-cavaliers-","/r/clevelandcavs", "1610612739"],
  "DAL": ["Dallas Mavericks", "06", "dallas-mavericks-","/r/mavericks", "1610612742"],
  "DEN": ["Denver Nuggets", "07", "denver-nuggets-","/r/denvernuggets", "1610612743"],
  "DET": ["Detroit Pistons", "08", "detroit-pistons-", "/r/detroitpistons", "1610612765"],
  "GSW": ["Golden State Warriors", "09", "golden-state-warriors-", "/r/warriors", "1610612744"],
  "HOU": ["Houston Rockets", "10", "houston-rockets-", "/r/rockets", "1610612745"],
  "IND": ["Indiana Pacers", "11", "indiana-pacers-", "/r/pacers", "1610612754"],
  "LAC": ["Los Angeles Clippers", "12", "los-angeles-clippers-", "/r/laclippers", "1610612746"],
  "LAL": ["Los Angeles Lakers", "13", "los-angeles-lakers-", "/r/lakers", "1610612747"],
  "MEM": ["Memphis Grizzlies", "29", "memphis-grizzlies-", "/r/memphisgrizzlies", "1610612763"],
  "MIA": ["Miami Heat", "14", "miami-heat-", "/r/heat", "1610612748"],
  "MIL": ["Milwaukee Bucks", "15", "milwaukee-bucks-", "/r/mkebucks", "1610612749"],
  "MIN": ["Minnesota Timberwolves", "16", "minnesota-timberwolves-", "/r/timberwolves", "1610612750"],
  "NOP": ["New Orleans Pelicans", "03", "new-orleans-pelicans-", "/r/nolapelicans", "1610612740"],
  "NYK": ["New York Knicks", "18", "new-york-knicks-", "/r/nyknicks", "1610612752"],
  "OKC": ["Oklahoma City Thunder", "25", "oklahoma-city-thunder-", "/r/thunder", "1610612760"],
  "ORL": ["Orlando Magic", "19", "orlando-magic-", "/r/orlandomagic", "1610612753"],
  "PHI": ["Philadelphia 76ers", "20", "philadelphia-76ers-", "/r/sixers", "1610612755"],
  "PHX": ["Phoenix Suns", "21", "phoenix-suns-", "/r/suns", "1610612756"],
  "POR": ["Portland Trail Blazers", "22", "portland-trail-blazers-", "/r/ripcity", "1610612757"],
  "SAC": ["Sacramento Kings", "23", "sacramento-kings-", "/r/kings", "1610612758"],
  "SAS": ["San Antonio Spurs", "24", "san-antonio-spurs-", "/r/nbaspurs", "1610612759"],
  "TOR": ["Toronto Raptors", "28", "toronto-raptors-", "/r/torontoraptors", "1610612761"],
  "UTA": ["Utah Jazz", "26", "utah-jazz-", "/r/utahjazz", "1610612762"],
  "WAS": ["Washington Wizards", "27", "washington-wizards-", "/r/washingtonwizards", "1610612764"]
}

#logging in to get reddit class
reddit = praw.Reddit(username = config.username, 
                    password = config.password,
                    client_id = config.client_id, 
                    client_secret = config.client_secret,
                    user_agent = "nbaspurs sidebar test (by /u/f1uk3r)")

#change it to "nbaspurs" for update on main subreddit
sub = "33bourCSS"

#finding player's name when player's ID is given, dataPlayersLeague is a list of all players
def findPlayerName(dataPlayersLeague, playerId):
  for each in dataPlayersLeague:
    if each["personId"] == playerId:
      return each["firstName"] + " " + each["lastName"]

#getting json data from requsted url
def requestApi(url):
  req = requests.get(url)
  return req.json()

#getting players data for players table
def playerDataList(dataPlayersLeague, playerId):
  playerData = requestApi("http://data.nba.net/prod/v1/2018/players/" + str(playerId) + "_profile.json")
  playerCurrentData = playerData["league"]["standard"]["stats"]["latest"]
  if playerCurrentData["ppg"] != "-1":
    playerRequiredData = [findPlayerName(dataPlayersLeague, playerId), playerCurrentData["ppg"],playerCurrentData["rpg"],playerCurrentData["apg"],playerCurrentData["spg"],playerCurrentData["bpg"]]
    return playerRequiredData
  return []

#getting whole NBA Schedule
nbaSchedule = requestApi("http://data.nba.net/prod/v1/2018/schedule.json")
allGames = nbaSchedule["league"]["standard"]
allSpursGames = []
for each in allGames:
  if each["gameUrlCode"][9:12] == "SAS" or each["gameUrlCode"][-3:] == "SAS":
    allSpursGames.append(each)

#finding date of games
now = date.today()
yesterday = date.today() - timedelta(1)
dateToday = now.strftime("%Y%m%d") #check the date before using script
dateYesterday = yesterday.strftime("%Y%m%d")
#print(date)

#getting games which are to be displayed from all 82 games
for i in range(len(allSpursGames)):
  if allSpursGames[i]["startDateEastern"] == dateToday or allSpursGames[i]["startDateEastern"] == dateYesterday:
    requiredSpursGames = [allSpursGames[i-2],allSpursGames[i-1],allSpursGames[i],allSpursGames[i+1],allSpursGames[i+2],allSpursGames[i+3]]

#Sidebar body starts here
sidebarBody = '''[Pounding the Rock](http://www.poundingtherock.com/) | [Spurstalk](http://www.spurstalk.com/forums/) | [Spurs Discord](https://discord.gg/rcvBDQ6)

------
**[2018-2019 Spurs Schedule](http://www.nba.com/spurs/schedule/) | Record: '''

#getting record from another json (can be improved by getting this record from schedule.json)
conferenceStandings = requestApi("http://data.nba.net/prod/v1/current/standings_conference.json")
westTeams = conferenceStandings["league"]["standard"]["conference"]["west"]
for eachTeam in westTeams:
  if eachTeam["teamId"] == "1610612759":
    sidebarBody += eachTeam["win"] + "-" + eachTeam["loss"]

#body continues
sidebarBody += '''**

------

| | | | | | | |
:--:|:--:|:--:|:--:|:--:|:--:|:--:|'''

#schedule part of the body
for each in requiredSpursGames:
  if each["gameUrlCode"][9:12] == "SAS":
    sasIsAwayTeam = True
  else:
    sasIsAwayTeam = False
  if each["hTeam"]["score"]!="":
    if int(each["hTeam"]["score"])<int(each["vTeam"]["score"]) and sasIsAwayTeam:
      sasStatus = "W"
      finalCol = each["vTeam"]["score"] + "-" + each["hTeam"]["score"]
    elif int(each["hTeam"]["score"])<int(each["vTeam"]["score"]) and sasIsAwayTeam==False:
      sasStatus = "L"
      finalCol = each["vTeam"]["score"] + "-" + each["hTeam"]["score"]
    elif int(each["hTeam"]["score"])>int(each["vTeam"]["score"]) and sasIsAwayTeam:
      sasStatus = "L"
      finalCol = each["vTeam"]["score"] + "-" + each["hTeam"]["score"]
    elif int(each["hTeam"]["score"])>int(each["vTeam"]["score"]) and sasIsAwayTeam==False:
      sasStatus = "W"
      finalCol = each["vTeam"]["score"] + "-" + each["hTeam"]["score"]
  else:
    sasStatus = each["startTimeEastern"]
    gameDetail = requestApi("http://data.nba.net/prod/v1/" + each["startDateEastern"] + "/" + each["gameId"] + "_boxscore.json")
    if sasIsAwayTeam:
      print(gameDetail["basicGameData"]["watch"]["broadcast"]["broadcasters"]["vTeam"])
      if len(gameDetail["basicGameData"]["watch"]["broadcast"]["broadcasters"]["vTeam"])!=0:
        finalCol = gameDetail["basicGameData"]["watch"]["broadcast"]["broadcasters"]["vTeam"][0]["shortName"]
    else:
      finalCol = gameDetail["basicGameData"]["watch"]["broadcast"]["broadcasters"]["hTeam"][0]["shortName"]
  sidebarBody += "\n" + each["startDateEastern"][4:6] + "/" + each["startDateEastern"][-2:] + " | [](" + teamDict[each["gameUrlCode"][9:12]][3] + ") | @ | [](" + teamDict[each["gameUrlCode"][-3:]][3] + ") | " + sasStatus + " | " + finalCol + " |"

#body continues
sidebarBody += '''

| | | | | | | |
|--:|:--:|:--:|:--:|:--:|:--:|:--:|
**Player** | **PTS** | **REB** | **AST** | **STL** | **BLK** |'''

#getting informations of players through API since the boxscore API lacks name of players
dataPlayers = requestApi("http://data.nba.net/prod/v1/2018/players.json")
dataPlayersLeague = dataPlayers["league"]["standard"] + dataPlayers["league"]["africa"] + dataPlayers["league"]["sacramento"] + dataPlayers["league"]["vegas"] + dataPlayers["league"]["utah"]
#getting roster of spurs
teamData = requestApi("http://data.nba.net/prod/v1/2018/teams/1610612759/roster.json")
teamPlayers = teamData["league"]["standard"]["players"]
#body is appended with the data of players
for each in teamPlayers:
  player = playerDataList(dataPlayersLeague, each["personId"])
  if player != []:
    sidebarBody += "\n"
    for every in player:
      sidebarBody +=  every + " | "

#body near the end
sidebarBody += '''

**BE NICE.**

Troll posts will be removed and violators may be banned. Lighthearted shittalking is allowed. We will make judgement calls about what qualifies.

**POST SPURS RELATED CONTENT ONLY.**

Reaction GIFs, image macros, or memes will be removed if they do not contain content that is substantially related to the Spurs.

**NO SPAMMING.**

Original content from your blog about the Spurs (or similar such content) is welcome, but if that's the only thing you post, and you do not otherwise participate in the community, your posts may be removed.  Duplicate posts may be removed. Short text "comment" posts may also be removed.

* [](http://en.wikipedia.org/wiki/1998%E2%80%9399_San_Antonio_Spurs_season)
* [](http://en.wikipedia.org/wiki/2002%E2%80%9303_San_Antonio_Spurs_season)
* [](http://en.wikipedia.org/wiki/2004%E2%80%9305_San_Antonio_Spurs_season)
* [](http://en.wikipedia.org/wiki/2006%E2%80%9307_San_Antonio_Spurs_season)
* [](http://en.wikipedia.org/wiki/2013%E2%80%9314_San_Antonio_Spurs_season)
* [](http://en.wikipedia.org/wiki/2017%E2%80%9318_San_Antonio_Spurs_season)

1. [](http://en.wikipedia.org/wiki/James_Silas)
2. [](http://en.wikipedia.org/wiki/George_Gervin)
3. [](http://en.wikipedia.org/wiki/Johnny_Moore_%28basketball%29)
4. [](http://en.wikipedia.org/wiki/David_Robinson_%28basketball%29)
5. [](http://en.wikipedia.org/wiki/Sean_Elliott)
6. [](http://en.wikipedia.org/wiki/Avery_Johnson)
7. [](http://en.wikipedia.org/wiki/Bruce_Bowen)
8. [](http://en.wikipedia.org/wiki/Tim_Duncan)

* [](https://en.wikipedia.org/wiki/1999_NBA_Playoffs)
* [](https://en.wikipedia.org/wiki/2003_NBA_Playoffs)
* [](https://en.wikipedia.org/wiki/2005_NBA_Playoffs)
* [](https://en.wikipedia.org/wiki/2007_NBA_Playoffs)
* [](https://en.wikipedia.org/wiki/2013_NBA_Playoffs)
* [](https://en.wikipedia.org/wiki/2014_NBA_Playoffs)

######nba######
* [](http://reddit.com/r/nba)

#####reddit#####
* [](http://reddit.com)'''

#uncomment for testing
#print(sidebarBody)

#update sidebar here
reddit.subreddit(sub).mod.update(description=sidebarBody)