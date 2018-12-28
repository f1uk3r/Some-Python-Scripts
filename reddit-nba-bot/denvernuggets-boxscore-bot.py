# python3
# reddit-boxscore-bot.py by f1uk3r-- reads the data from stats.nba.net and makes a posts Postgame Thread on specified subreddit 
# pip install requests, praw
import praw
import config
import requests
import json
from datetime import date, timedelta


#Team Dictionary helps to make urls for boxscore and for full-forms of abbrevation of teams
teamDict = {
  "ATL": ["Atlanta Hawks","01", "atlanta-hawks-", "http://np.reddit.com/r/atlantahawks"],
  "BKN": ["Brooklyn Nets", "02", "boston-celtics-", "http://np.reddit.com/r/bostonceltics"],
  "BOS": ["Boston Celtics", "17", "brooklyn-nets-","http://np.reddit.com/r/gonets"],
  "CHA": ["Charlotte Hornets", "30", "charlotte-hornets-","http://np.reddit.com/r/charlottehornets"],
  "CHI": ["Chicago Bulls", "04", "chicago-bulls-","http://np.reddit.com/r/chicagobulls"],
  "CLE": ["Cleveland Cavaliers", "05", "cleveland-cavaliers-","http://np.reddit.com/r/clevelandcavs"],
  "DAL": ["Dallas Mavericks", "06", "dallas-mavericks-","http://np.reddit.com/r/mavericks"],
  "DEN": ["Denver Nuggets", "07", "denver-nuggets-","http://np.reddit.com/r/denvernuggets"],
  "DET": ["Detroit Pistons", "08", "detroit-pistons-", "http://np.reddit.com/r/detroitpistons"],
  "GSW": ["Golden State Warriors", "09", "golden-state-warriors-", "http://np.reddit.com/r/warriors"],
  "HOU": ["Houston Rockets", "10", "houston-rockets-", "http://np.reddit.com/r/rockets"],
  "IND": ["Indiana Pacers", "11", "indiana-pacers-", "http://np.reddit.com/r/pacers"],
  "LAC": ["Los Angeles Clippers", "12", "los-angeles-clippers-", "http://np.reddit.com/r/laclippers"],
  "LAL": ["Los Angeles Lakers", "13", "los-angeles-lakers-", "http://np.reddit.com/r/lakers"],
  "MEM": ["Memphis Grizzlies", "29", "memphis-grizzlies-", "http://np.reddit.com/r/memphisgrizzlies"],
  "MIA": ["Miami Heat", "14", "miami-heat-", "http://np.reddit.com/r/heat"],
  "MIL": ["Milwaukee Bucks", "15", "milwaukee-bucks-", "http://np.reddit.com/r/mkebucks"],
  "MIN": ["Minnesota Timberwolves", "16", "minnesota-timberwolves-", "http://np.reddit.com/r/timberwolves"],
  "NOP": ["New Orleans Pelicans", "03", "new-orleans-pelicans-", "http://np.reddit.com/r/nolapelicans"],
  "NYK": ["New York Knicks", "18", "new-york-knicks-", "http://np.reddit.com/r/nyknicks"],
  "OKC": ["Oklahoma City Thunder", "25", "oklahoma-city-thunder-", "http://np.reddit.com/r/thunder"],
  "ORL": ["Orlando Magic", "19", "orlando-magic-", "http://np.reddit.com/r/orlandomagic"],
  "PHI": ["Philadelphia 76ers", "20", "philadelphia-76ers-", "http://np.reddit.com/r/sixers"],
  "PHX": ["Phoenix Suns", "21", "phoenix-suns-", "http://np.reddit.com/r/suns"],
  "POR": ["Portland Trail Blazers", "22", "portland-trail-blazers-", "http://np.reddit.com/r/ripcity"],
  "SAC": ["Sacramento Kings", "23", "sacramento-kings-", "http://np.reddit.com/r/kings"],
  "SAS": ["San Antonio Spurs", "24", "san-antonio-spurs-", "http://np.reddit.com/r/nbaspurs"],
  "TOR": ["Toronto Raptors", "28", "toronto-raptors-", "http://np.reddit.com/r/torontoraptors"],
  "UTA": ["Utah Jazz", "26", "utah-jazz-", "http://np.reddit.com/r/utahjazz"],
  "WAS": ["Washington Wizards", "27", "washington-wizards-", "http://np.reddit.com/r/washingtonwizards"]
}
#getting a reddit instance by giving appropiate credentials
reddit = praw.Reddit(username = config.username, 
                    password = config.password,
                    client_id = config.client_id, 
                    client_secret = config.client_secret,
                    user_agent = "script:rdenvernuggets-post-game-thread-bot:v1.0 (by /u/f1uk3r)")

def requestApi(url):
  req = requests.get(url)
  return req.json()

#appending + sign in front of biggest lead and +/- stats
def appendPlusMinus(someStat):
  if someStat.isdigit():
    if int(someStat)>0:
      return "+" + str(someStat)
    return str(someStat)
  else:
    return str(someStat)

#getting informations of players through API since the boxscore API lacks name of players
dataPlayers = requestApi("http://data.nba.net/prod/v1/2018/players.json")
dataPlayersLeague = dataPlayers["league"]["standard"]

#finding player's name when player's ID is given, dataPlayersLeague is a list of all players
def findPlayerName(dataPlayersLeague, playerId):
  for each in dataPlayersLeague:
    if each["personId"] == playerId:
      return each["firstName"] + " " + each["lastName"]

#finding date of games
now = date.today() - timedelta(1)
date = now.strftime("%Y%m%d") #check the date before using script
#print(date)

#getting today's game
data = requestApi("http://data.nba.net/prod/v1/" + date + "/scoreboard.json")
gamesToday = data["numGames"]
games = data["games"]
print("Showing finished games")

#prints information of games that have ended, stores relevant information in tabulateList
header = ["index","gameId", "title", "gameDuration"]
tabulateList = []
index = 1
for each in games:
  if (each["clock"] == "0.0" or each["clock"] == "") and each["period"]["current"] >= 4 and (each["vTeam"]["score"] != each["hTeam"]["score"]) and (each["vTeam"]["triCode"]=="DEN" or each["hTeam"]["triCode"] == "DEN"):  #a finished game should not have empty endTime
    gameId = each["gameId"]
    gameDuration = each["gameDuration"]["hours"] + ":" + each["gameDuration"]["minutes"]
    visitorTeam = teamDict[each["vTeam"]["triCode"]][0] + " (" + each["vTeam"]["win"] + "-" + each["vTeam"]["loss"] + ")"
    visitorTeamId = each["vTeam"]["teamId"]
    visitorTeamScore = each["vTeam"]["score"]
    homeTeam = teamDict[each["hTeam"]["triCode"]][0] + " (" + each["hTeam"]["win"] + "-" + each["hTeam"]["loss"] + ")"
    homeTeamScore = each["hTeam"]["score"]
    if (int(visitorTeamScore) > int(homeTeamScore)) and len(each["vTeam"]["linescore"])==4:
      title = "[Post Game Thread] The " + visitorTeam + " defeats the @ " + homeTeam + ", " + visitorTeamScore + " - " + homeTeamScore
      print(str(index) + "    " + gameId + "    " + visitorTeam + " @ " + homeTeam)
    elif (int(visitorTeamScore) > int(homeTeamScore)) and len(each["vTeam"]["linescore"])>4:
      title = "[Post Game Thread] The " + visitorTeam + " defeats the @ " + homeTeam + " in OT, " + visitorTeamScore + " - " + homeTeamScore
      print(str(index) + "    " + gameId + "    " + visitorTeam + " @ " + homeTeam)
    elif (int(visitorTeamScore) < int(homeTeamScore)) and len(each["vTeam"]["linescore"])==4:
      title = "[Post Game Thread] The " + homeTeam + " defeats the v " + visitorTeam + ", " + homeTeamScore + " - " + visitorTeamScore
      print(str(index) + "    " + gameId + "    " + homeTeam + " v " + visitorTeam)
    elif (int(visitorTeamScore) < int(homeTeamScore)) and len(each["vTeam"]["linescore"])>4:
      title = "[Post Game Thread] The " + homeTeam + " defeats the v " + visitorTeam + " in OT, " + homeTeamScore + " - " + visitorTeamScore
      print(str(index) + "    " + gameId + "    " + homeTeam + " v " + visitorTeam)
    row = {"index": index, "gameId": gameId, "title": title, 
    "visitorTeam": each["vTeam"]["triCode"], "visitorTeamScore": visitorTeamScore,
    "homeTeam": each["hTeam"]["triCode"], "homeTeamScore": homeTeamScore,
    "gameDuration": gameDuration, "visitorTeamId": visitorTeamId}
    tabulateList.append(row)

game = 0
dataBoxScore = requestApi("http://data.nba.net/prod/v1/" + date + "/" + str(tabulateList[game]["gameId"]) + "_boxscore.json")
basicGameData = dataBoxScore["basicGameData"] #contains all the data related to this game
allStats = dataBoxScore["stats"]  #contains all the stats of this game
playerStats = allStats["activePlayers"] #contains all the stats of players of the team

#calculates url to boxscores on nba and yahoo websites
nbaUrl = "http://www.nba.com/game/" + date + "/" + tabulateList[game]["visitorTeam"] + tabulateList[game]["homeTeam"] + "#/boxscore"
yahooUrl = "http://sports.yahoo.com/nba/" + teamDict[tabulateList[game]["visitorTeam"]][2] + teamDict[tabulateList[game]["homeTeam"]][2] + date + teamDict[tabulateList[game]["homeTeam"]][1]

#Body of reddit post starts here
body = '''	
|[](/''' + tabulateList[game]["visitorTeam"] + ")**(" + tabulateList[game]["visitorTeamScore"]  + ")**|" + " [](/" + tabulateList[game]["homeTeam"] + ")**(" + tabulateList[game]["homeTeamScore"] + ''')**|
|:-:|:-:|
	

						
|**GAME SUMMARY**|
|:-:|
|**Box Scores: [NBA](''' + nbaUrl + ") & [Yahoo](" + yahooUrl + ''')**|	
|**Location:** ''' + basicGameData["arena"]["name"] + "(" + basicGameData["attendance"] + "), **Duration:** " + tabulateList[game]["gameDuration"] + '''|
|**Officials:** ''' + basicGameData["officials"]["formatted"][0]["firstNameLastName"] + ", " + basicGameData["officials"]["formatted"][1]["firstNameLastName"] + " and " + basicGameData["officials"]["formatted"][2]["firstNameLastName"] + '''|	


|**Team**|**Q1**|**Q2**|**Q3**|**Q4**|**'''
#Condition for normal games
if len(basicGameData["vTeam"]["linescore"])==4:
  body += '''Total**|
|:--|:--:|:--:|:--:|:--:|:--:|
|''' + teamDict[tabulateList[game]["visitorTeam"]][0] + "|" + basicGameData["vTeam"]["linescore"][0]["score"] + "|" + basicGameData["vTeam"]["linescore"][1]["score"] + "|" + basicGameData["vTeam"]["linescore"][2]["score"] + "|" + basicGameData["vTeam"]["linescore"][3]["score"] + "|"+ tabulateList[game]["visitorTeamScore"] + '''|
|''' + teamDict[tabulateList[game]["homeTeam"]][0] + "|" + basicGameData["hTeam"]["linescore"][0]["score"] + "|" + basicGameData["hTeam"]["linescore"][1]["score"] + "|" + basicGameData["hTeam"]["linescore"][2]["score"] + "|" + basicGameData["hTeam"]["linescore"][3]["score"] + "|"+ tabulateList[game]["homeTeamScore"] + '''|
'''

#condition for OT game
elif len(basicGameData["vTeam"]["linescore"])>4:
#appending OT columns
  for i in range(4, len(basicGameData["vTeam"]["linescore"])):
    body += "OT" + str(i-3) + "**|**"
  body += '''Total**|
|:--|:--:|:--:|:--:|:--:|:--:|'''
#increase string ":--:|" according to number of OT
  for i in range(4, len(basicGameData["vTeam"]["linescore"])):
    body += ":--:|"
  body += "\n|" + teamDict[tabulateList[game]["visitorTeam"]][0] + "|"
  for i in range(len(basicGameData["vTeam"]["linescore"])):
    body += basicGameData["vTeam"]["linescore"][i]["score"] + "|"
  body += tabulateList[game]["visitorTeamScore"] + '''|
|''' + teamDict[tabulateList[game]["homeTeam"]][0] + "|"
  for i in range(len(basicGameData["hTeam"]["linescore"])):
    body += basicGameData["hTeam"]["linescore"][i]["score"] + "|"
  body += tabulateList[game]["homeTeamScore"] + '''|
'''

body += '''

|**TEAM STATS**|
|:-:|			


|**Team**|**PTS**|**FG**|**FG%**|**3P**|**3P%**|**FT**|**FT%**|**OREB**|**TREB**|**AST**|**PF**|**STL**|**TO**|**BLK**|
|:--|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
|''' + teamDict[tabulateList[game]["visitorTeam"]][0] + "|" + allStats["vTeam"]["totals"]["points"] + "|" + allStats["vTeam"]["totals"]["fgm"] + "-" + allStats["vTeam"]["totals"]["fga"] + "|" + allStats["vTeam"]["totals"]["fgp"] + "%|" + allStats["vTeam"]["totals"]["tpm"] + "-" + allStats["vTeam"]["totals"]["tpa"] + "|" + allStats["vTeam"]["totals"]["tpp"] + "%|" + allStats["vTeam"]["totals"]["ftm"] + "-" + allStats["vTeam"]["totals"]["fta"] + "|" + allStats["vTeam"]["totals"]["ftp"] + "%|" + allStats["vTeam"]["totals"]["offReb"] + "|" + allStats["vTeam"]["totals"]["totReb"] + "|" + allStats["vTeam"]["totals"]["assists"] + "|" + allStats["vTeam"]["totals"]["pFouls"] + "|" + allStats["vTeam"]["totals"]["steals"] + "|" + allStats["vTeam"]["totals"]["turnovers"] + "|" + allStats["vTeam"]["totals"]["blocks"] + '''|
|''' + teamDict[tabulateList[game]["homeTeam"]][0] + "|" + allStats["hTeam"]["totals"]["points"] + "|" + allStats["hTeam"]["totals"]["fgm"] + "-" + allStats["hTeam"]["totals"]["fga"] + "|" + allStats["hTeam"]["totals"]["fgp"] + "%|" + allStats["hTeam"]["totals"]["tpm"] + "-" + allStats["hTeam"]["totals"]["tpa"] + "|" + allStats["hTeam"]["totals"]["tpp"] + "%|" + allStats["hTeam"]["totals"]["ftm"] + "-" + allStats["hTeam"]["totals"]["fta"] + "|" + allStats["hTeam"]["totals"]["ftp"] + "%|" + allStats["hTeam"]["totals"]["offReb"] + "|" + allStats["hTeam"]["totals"]["totReb"] + "|" + allStats["hTeam"]["totals"]["assists"] + "|" + allStats["hTeam"]["totals"]["pFouls"] + "|" + allStats["hTeam"]["totals"]["steals"] + "|" + allStats["hTeam"]["totals"]["turnovers"] + "|" + allStats["hTeam"]["totals"]["blocks"] + '''|


|**Team**|**Biggest Lead**|**Longest Run**|**PTS: In Paint**|**PTS: Off TOs**|**PTS: Fastbreak**|
|:--|:--:|:--:|:--:|:--:|:--:|
|''' + teamDict[tabulateList[game]["visitorTeam"]][0] + "|" + appendPlusMinus(allStats["vTeam"]["biggestLead"]) + "|" + allStats["vTeam"]["longestRun"] + "|" + allStats["vTeam"]["pointsInPaint"] + "|" + allStats["vTeam"]["pointsOffTurnovers"] + "|" + allStats["vTeam"]["fastBreakPoints"] + '''|
|''' + teamDict[tabulateList[game]["homeTeam"]][0] + "|" + appendPlusMinus(allStats["hTeam"]["biggestLead"]) + "|" + allStats["hTeam"]["longestRun"] + "|" + allStats["hTeam"]["pointsInPaint"] + "|" + allStats["hTeam"]["pointsOffTurnovers"] + "|" + allStats["hTeam"]["fastBreakPoints"] + '''|



|**TEAM LEADERS**|
|:-:|			


|**Team**|**Points**|**Rebounds**|**Assists**|
|:--|:--:|:--:|:--:|
|''' + teamDict[tabulateList[game]["visitorTeam"]][0] + "|**" + allStats["vTeam"]["leaders"]["points"]["value"] + "** " + findPlayerName(dataPlayersLeague, allStats["vTeam"]["leaders"]["points"]["players"][0]["personId"]) + "|**" + allStats["vTeam"]["leaders"]["rebounds"]["value"] + "** " + findPlayerName(dataPlayersLeague, allStats["vTeam"]["leaders"]["rebounds"]["players"][0]["personId"])  + "|**" + allStats["vTeam"]["leaders"]["assists"]["value"] + "** " + findPlayerName(dataPlayersLeague, allStats["vTeam"]["leaders"]["assists"]["players"][0]["personId"]) + '''|
|''' + teamDict[tabulateList[game]["homeTeam"]][0] + "|**" + allStats["hTeam"]["leaders"]["points"]["value"] + "** " + findPlayerName(dataPlayersLeague, allStats["hTeam"]["leaders"]["points"]["players"][0]["personId"]) + "|**" + allStats["hTeam"]["leaders"]["rebounds"]["value"] + "** " + findPlayerName(dataPlayersLeague, allStats["hTeam"]["leaders"]["rebounds"]["players"][0]["personId"])  + "|**" + allStats["hTeam"]["leaders"]["assists"]["value"] + "** " + findPlayerName(dataPlayersLeague, allStats["hTeam"]["leaders"]["assists"]["players"][0]["personId"]) + '''|



|**PLAYER STATS**|
|:-:|			


||||||||||||||||
|:--|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
**[](/''' + tabulateList[game]["visitorTeam"] + ") " + teamDict[tabulateList[game]["visitorTeam"]][0].rsplit(None, 1)[-1].upper() + '''**|**MIN**|**FGM-A**|**3PM-A**|**FTM-A**|**ORB**|**DRB**|**REB**|**AST**|**STL**|**BLK**|**TO**|**PF**|**+/-**|**PTS**|
'''

#players stats are filled here, only starters have "pos" property (away team)
for i in range(len(playerStats)):
  if playerStats[i]["teamId"] == tabulateList[game]["visitorTeamId"] and playerStats[i]["pos"] != "":
    body += "|" + findPlayerName(dataPlayersLeague, playerStats[i]["personId"]) + "^" + playerStats[i]["pos"] + "|" + playerStats[i]["min"] + "|" + playerStats[i]["fgm"] + "-" + playerStats[i]["fga"] + "|" + playerStats[i]["tpm"] + "-" + playerStats[i]["tpa"] + "|" + playerStats[i]["ftm"] + "-" + playerStats[i]["fta"] + "|" + playerStats[i]["offReb"] + "|" + playerStats[i]["defReb"] + "|" + playerStats[i]["totReb"] + "|" + playerStats[i]["assists"] + "|" + playerStats[i]["steals"] + "|" + playerStats[i]["blocks"] + "|" + playerStats[i]["turnovers"] + "|" + playerStats[i]["pFouls"] + "|" + appendPlusMinus(playerStats[i]["plusMinus"]) + "|" + playerStats[i]["points"] + "|\n"
  elif playerStats[i]["teamId"] == tabulateList[game]["visitorTeamId"]:
    body += "|" + findPlayerName(dataPlayersLeague, playerStats[i]["personId"]) + "|" + playerStats[i]["min"] + "|" + playerStats[i]["fgm"] + "-" + playerStats[i]["fga"] + "|" + playerStats[i]["tpm"] + "-" + playerStats[i]["tpa"] + "|" + playerStats[i]["ftm"] + "-" + playerStats[i]["fta"] + "|" + playerStats[i]["offReb"] + "|" + playerStats[i]["defReb"] + "|" + playerStats[i]["totReb"] + "|" + playerStats[i]["assists"] + "|" + playerStats[i]["steals"] + "|" + playerStats[i]["blocks"] + "|" + playerStats[i]["turnovers"] + "|" + playerStats[i]["pFouls"] + "|" + appendPlusMinus(playerStats[i]["plusMinus"]) + "|" + playerStats[i]["points"] + "|\n"

body += '''**[](/''' + tabulateList[game]["homeTeam"] + ") " + teamDict[tabulateList[game]["homeTeam"]][0].rsplit(None, 1)[-1].upper() + '''**|**MIN**|**FGM-A**|**3PM-A**|**FTM-A**|**ORB**|**DRB**|**REB**|**AST**|**STL**|**BLK**|**TO**|**PF**|**+/-**|**PTS**|
'''
#home team players
for i in range(len(playerStats)):
  if playerStats[i]["teamId"] != tabulateList[game]["visitorTeamId"] and playerStats[i]["pos"] != "":
    body += "|" + findPlayerName(dataPlayersLeague, playerStats[i]["personId"]) + "^" + playerStats[i]["pos"] + "|" + playerStats[i]["min"] + "|" + playerStats[i]["fgm"] + "-" + playerStats[i]["fga"] + "|" + playerStats[i]["tpm"] + "-" + playerStats[i]["tpa"] + "|" + playerStats[i]["ftm"] + "-" + playerStats[i]["fta"] + "|" + playerStats[i]["offReb"] + "|" + playerStats[i]["defReb"] + "|" + playerStats[i]["totReb"] + "|" + playerStats[i]["assists"] + "|" + playerStats[i]["steals"] + "|" + playerStats[i]["blocks"] + "|" + playerStats[i]["turnovers"] + "|" + playerStats[i]["pFouls"] + "|" + appendPlusMinus(playerStats[i]["plusMinus"]) + "|" + playerStats[i]["points"] + "|\n"
  elif playerStats[i]["teamId"] != tabulateList[game]["visitorTeamId"]:
    body += "|" + findPlayerName(dataPlayersLeague, playerStats[i]["personId"]) + "|" + playerStats[i]["min"] + "|" + playerStats[i]["fgm"] + "-" + playerStats[i]["fga"] + "|" + playerStats[i]["tpm"] + "-" + playerStats[i]["tpa"] + "|" + playerStats[i]["ftm"] + "-" + playerStats[i]["fta"] + "|" + playerStats[i]["offReb"] + "|" + playerStats[i]["defReb"] + "|" + playerStats[i]["totReb"] + "|" + playerStats[i]["assists"] + "|" + playerStats[i]["steals"] + "|" + playerStats[i]["blocks"] + "|" + playerStats[i]["turnovers"] + "|" + playerStats[i]["pFouls"] + "|" + appendPlusMinus(playerStats[i]["plusMinus"]) + "|" + playerStats[i]["points"] + "|\n"
#footer
body += '''

|^[bot-script](https://github.com/f1uk3r/Some-Python-Scripts/blob/master/reddit-nba-bot/reddit-boxscore-bot.py) ^by ^/u/f1uk3r|  
|:-:|'''

print(tabulateList[game]["title"])
#print(body) #uncomment print statement to see body on console
#reddit.subreddit('denvernuggets').submit(tabulateList[game]["title"], selftext=body, send_replies=False) #change nba to subreddit name if posting to other subreddits

for submission in reddit.subreddit('denvernuggets').search("post game thread", sort="hot", time_filter="day"):
#if "r/NBA Game Threads Index + Daily Discussion" not in submission.title:
  print(submission.title)
  submission.reply(body)