import praw
import config
import requests
import json
import datetime


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
  "LAC": ["Los Angles Clippers", "12", "los-angeles-clippers-", "http://np.reddit.com/r/laclippers"],
  "LAL": ["Los Angles Lakers", "13", "los-angeles-lakers-", "http://np.reddit.com/r/lakers"],
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
                    user_agent = "script:reddit-boxscore-test:v0.1 (by /u/f1uk3r)")

def requestApi(url):
  req = requests.get(url)
  return req.json()

#getting informations of players through API since the boxscore API lacks name of players
dataPlayers = requestApi("http://data.nba.net/prod/v1/2018/players.json")
dataPlayersLeague = dataPlayers["league"]["standard"]

#finding player's name when player's ID is given, dataPlayersLeague is a list of all players
def findPlayerName(dataPlayersLeague, playerId):
  for each in dataPlayersLeague:
    if each["personId"] == playerId:
      return each["firstName"] + " " + each["lastName"]

#finding date of games
now = datetime.datetime.now()
date = str(now.year) + str(now.month) + str(now.day-1)

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
  if each["isGameActivated"] == False and each["endTimeUTC"] != "":
    gameId = each["gameId"]
    gameDuration = each["gameDuration"]["hours"] + ":" + each["gameDuration"]["minutes"]
    visitorTeam = teamDict[each["vTeam"]["triCode"]][0] + " (" + each["vTeam"]["win"] + "-" + each["vTeam"]["loss"] + ")"
    visitorTeamId = each["vTeam"]["teamId"]
    visitorTeamScore = each["vTeam"]["score"]
    homeTeam = teamDict[each["hTeam"]["triCode"]][0] + "(" + each["hTeam"]["win"] + "-" + each["hTeam"]["loss"] + ")"
    homeTeamScore = each["hTeam"]["score"]
    if (int(visitorTeamScore) > int(homeTeamScore)):
      title = "[Post Game Thread] The " + visitorTeam + " defeats the @ " + homeTeam + ", " + visitorTeamScore + " - " + homeTeamScore
      print(str(index) + "    " + gameId + "    " + visitorTeam + " @ " + homeTeam)
    else:
      title = "[Post Game Thread] The " + homeTeam + " defeats the v " + visitorTeam + ", " + homeTeamScore + " - " + visitorTeamScore
      print(str(index) + "    " + gameId + "    " + homeTeam + " v " + visitorTeam)
    row = {"index": index, "gameId": gameId, "title": title, 
    "visitorTeam": each["vTeam"]["triCode"], "visitorTeamScore": visitorTeamScore,
    "homeTeam": each["hTeam"]["triCode"], "homeTeamScore": homeTeamScore,
    "gameDuration": gameDuration, "visitorTeamId": visitorTeamId}
    tabulateList.append(row)
    index += 1

game = int(input("Choose the game (by index) you want to make Post Game Thread of: ")) -1
dataBoxScore = requestApi("http://data.nba.net/prod/v1/" + date + "/" + str(tabulateList[game]["gameId"]) + "_boxscore.json")

basicGameData = dataBoxScore["basicGameData"] #contains all the data related to this game
allStats = dataBoxScore["stats"]  #contains all the stats of this game
playerStats = allStats["activePlayers"] #contains all the stats of players of the team

#calculates url to boxscores on nba and yahoo websites
nbaUrl = "http://watch.nba.com/game/" + date + "/" + tabulateList[game]["visitorTeam"] + tabulateList[game]["homeTeam"] + "#/boxscore"
yahooUrl = "http://sports.yahoo.com/nba/" + teamDict[tabulateList[game]["visitorTeam"]][2] + teamDict[tabulateList[game]["homeTeam"]][2] + date + teamDict[tabulateList[game]["homeTeam"]][1]

#Body of reddit post starts here
body = '''
||		
|:-:|		
|[](/''' + tabulateList[game]["visitorTeam"] + ") **" + tabulateList[game]["visitorTeamScore"]  + " - " + tabulateList[game]["homeTeamScore"] + "** [](/" + tabulateList[game]["homeTeam"] + ''')|
|**Box Scores: [NBA](''' + nbaUrl + ") & [Yahoo](" + yahooUrl + ''')**|													
|&nbsp;|		
|**GAME SUMMARY**|		

|**Team**|**Q1**|**Q2**|**Q3**|**Q4**|**Total**|
|:---|:--|:--|:--|:--|:--|
|''' + teamDict[tabulateList[game]["visitorTeam"]][0] + "|" + basicGameData["vTeam"]["linescore"][0]["score"] + "|" + basicGameData["vTeam"]["linescore"][1]["score"] + "|" + basicGameData["vTeam"]["linescore"][2]["score"] + "|" + basicGameData["vTeam"]["linescore"][3]["score"] + "|"+ tabulateList[game]["visitorTeamScore"] + '''|
|''' + teamDict[tabulateList[game]["homeTeam"]][0] + "|" + basicGameData["hTeam"]["linescore"][0]["score"] + "|" + basicGameData["hTeam"]["linescore"][1]["score"] + "|" + basicGameData["hTeam"]["linescore"][2]["score"] + "|" + basicGameData["hTeam"]["linescore"][3]["score"] + "|"+ tabulateList[game]["homeTeamScore"] + '''|

||		
|:-:|		
|&nbsp;|		
|**Team Stats**|

|**Team**|**PTS**|**FG**|**FT**|**3P**|**OREB**|**TREB**|**ASS**|**PF**|**STL**|**TO**|**BLK**|
|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|
|''' + teamDict[tabulateList[game]["visitorTeam"]][0] + "|" + allStats["vTeam"]["totals"]["points"] + "|" + allStats["vTeam"]["totals"]["fgm"] + "-" + allStats["vTeam"]["totals"]["fga"] + " (" + allStats["vTeam"]["totals"]["fgp"] + ")|" + allStats["vTeam"]["totals"]["ftm"] + "-" + allStats["vTeam"]["totals"]["fta"] + " (" + allStats["vTeam"]["totals"]["ftp"] + ")|" + allStats["vTeam"]["totals"]["tpm"] + "-" + allStats["vTeam"]["totals"]["tpa"] + " (" + allStats["vTeam"]["totals"]["tpp"] + ")|" + allStats["vTeam"]["totals"]["offReb"] + "|" + allStats["vTeam"]["totals"]["totReb"] + "|" + allStats["vTeam"]["totals"]["assists"] + "|" + allStats["vTeam"]["totals"]["pFouls"] + "|" + allStats["vTeam"]["totals"]["steals"] + "|" + allStats["vTeam"]["totals"]["turnovers"] + "|" + allStats["vTeam"]["totals"]["blocks"] + '''|
|''' + teamDict[tabulateList[game]["homeTeam"]][0] + "|" + allStats["hTeam"]["totals"]["points"] + "|" + allStats["hTeam"]["totals"]["fgm"] + "-" + allStats["hTeam"]["totals"]["fga"] + " (" + allStats["hTeam"]["totals"]["fgp"] + ")|" + allStats["hTeam"]["totals"]["ftm"] + "-" + allStats["hTeam"]["totals"]["fta"] + " (" + allStats["hTeam"]["totals"]["ftp"] + ")|" + allStats["hTeam"]["totals"]["tpm"] + "-" + allStats["hTeam"]["totals"]["tpa"] + " (" + allStats["hTeam"]["totals"]["tpp"] + ")|" + allStats["hTeam"]["totals"]["offReb"] + "|" + allStats["hTeam"]["totals"]["totReb"] + "|" + allStats["hTeam"]["totals"]["assists"] + "|" + allStats["hTeam"]["totals"]["pFouls"] + "|" + allStats["hTeam"]["totals"]["steals"] + "|" + allStats["hTeam"]["totals"]["turnovers"] + "|" + allStats["hTeam"]["totals"]["blocks"] + '''|

||		
|:-:|		
|&nbsp;|		
|**Miscellaneous Team Stats**|

|**Team**|**Fast-Break Pts**|**Pts in Paint**|**Biggest Lead**|**Pts off TO**|**Longest Run**|
|:--|:--|:--|:--|:--|:--|
|''' + teamDict[tabulateList[game]["visitorTeam"]][0] + "|" + allStats["vTeam"]["fastBreakPoints"] + "|" + allStats["vTeam"]["pointsInPaint"] + "|" + allStats["vTeam"]["biggestLead"] + "|" + allStats["vTeam"]["pointsOffTurnovers"] + "|" + allStats["vTeam"]["longestRun"] + '''|
|''' + teamDict[tabulateList[game]["homeTeam"]][0] + "|" + allStats["hTeam"]["fastBreakPoints"] + "|" + allStats["hTeam"]["pointsInPaint"] + "|" + allStats["hTeam"]["biggestLead"] + "|" + allStats["hTeam"]["pointsOffTurnovers"] + "|" + allStats["hTeam"]["longestRun"] + '''|

||		
|:-:|		
|&nbsp;|		
|**Team Leaders(Stats)**|

|**Team**|**Points Leader**|**Rebounds Leader**|**Assists Leader**|
|:--|:--|:--|:--|
|''' + teamDict[tabulateList[game]["visitorTeam"]][0] + "|" + findPlayerName(dataPlayersLeague, allStats["vTeam"]["leaders"]["points"]["players"][0]["personId"]) + "(" + allStats["vTeam"]["leaders"]["points"]["value"] + ")" + "|" + findPlayerName(dataPlayersLeague, allStats["vTeam"]["leaders"]["rebounds"]["players"][0]["personId"]) + "(" + allStats["vTeam"]["leaders"]["rebounds"]["value"] + ")" + "|" + findPlayerName(dataPlayersLeague, allStats["vTeam"]["leaders"]["assists"]["players"][0]["personId"]) + "(" + allStats["vTeam"]["leaders"]["assists"]["value"] + ")" + '''|
|''' + teamDict[tabulateList[game]["homeTeam"]][0] + "|" + findPlayerName(dataPlayersLeague, allStats["hTeam"]["leaders"]["points"]["players"][0]["personId"]) + "(" + allStats["hTeam"]["leaders"]["points"]["value"] + ")" + "|" + findPlayerName(dataPlayersLeague, allStats["hTeam"]["leaders"]["rebounds"]["players"][0]["personId"]) + "(" + allStats["hTeam"]["leaders"]["rebounds"]["value"] + ")" + "|" + findPlayerName(dataPlayersLeague, allStats["hTeam"]["leaders"]["assists"]["players"][0]["personId"]) + "(" + allStats["hTeam"]["leaders"]["assists"]["value"] + ")" + '''|

||		
|:-:|		
|&nbsp;|		
|**Individual Player's Stats**|

**[](/''' + tabulateList[game]["visitorTeam"] + ") " + teamDict[tabulateList[game]["visitorTeam"]][0].rsplit(None, 1)[-1].upper() + '''**|**MIN**|**FGM-A**|**3PM-A**|**FTM-A**|**ORB**|**DRB**|**REB**|**AST**|**STL**|**BLK**|**TO**|**PF**|**+/-**|**PTS**|
|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|
'''

#players stats are filled here, only starters have "pos" property 
for i in range(len(playerStats)):
  if playerStats[i]["teamId"] == tabulateList[game]["visitorTeamId"] and playerStats[i]["pos"] != "":
    body += "|" + findPlayerName(dataPlayersLeague, playerStats[i]["personId"]) + "^" + playerStats[i]["pos"] + "|" + playerStats[i]["min"] + "|" + playerStats[i]["fgm"] + "-" + playerStats[i]["fga"] + "|" + playerStats[i]["tpm"] + "-" + playerStats[i]["tpa"] + "|" + playerStats[i]["ftm"] + "-" + playerStats[i]["fta"] + "|" + playerStats[i]["offReb"] + "|" + playerStats[i]["defReb"] + "|" + playerStats[i]["totReb"] + "|" + playerStats[i]["assists"] + "|" + playerStats[i]["steals"] + "|" + playerStats[i]["blocks"] + "|" + playerStats[i]["turnovers"] + "|" + playerStats[i]["pFouls"] + "|" + playerStats[i]["plusMinus"] + "|" + playerStats[i]["points"] + "|\n"
  elif playerStats[i]["teamId"] == tabulateList[game]["visitorTeamId"]:
    body += "|" + findPlayerName(dataPlayersLeague, playerStats[i]["personId"]) + "|" + playerStats[i]["min"] + "|" + playerStats[i]["fgm"] + "-" + playerStats[i]["fga"] + "|" + playerStats[i]["tpm"] + "-" + playerStats[i]["tpa"] + "|" + playerStats[i]["ftm"] + "-" + playerStats[i]["fta"] + "|" + playerStats[i]["offReb"] + "|" + playerStats[i]["defReb"] + "|" + playerStats[i]["totReb"] + "|" + playerStats[i]["assists"] + "|" + playerStats[i]["steals"] + "|" + playerStats[i]["blocks"] + "|" + playerStats[i]["turnovers"] + "|" + playerStats[i]["pFouls"] + "|" + playerStats[i]["plusMinus"] + "|" + playerStats[i]["points"] + "|\n"

body += '''
**[](/''' + tabulateList[game]["homeTeam"] + ") " + teamDict[tabulateList[game]["homeTeam"]][0].rsplit(None, 1)[-1].upper() + '''**|**MIN**|**FGM-A**|**3PM-A**|**FTM-A**|**ORB**|**DRB**|**REB**|**AST**|**STL**|**BLK**|**TO**|**PF**|**+/-**|**PTS**|
|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|
'''

for i in range(len(playerStats)):
  if playerStats[i]["teamId"] != tabulateList[game]["visitorTeamId"] and playerStats[i]["pos"] != "":
    body += "|" + findPlayerName(dataPlayersLeague, playerStats[i]["personId"]) + "^" + playerStats[i]["pos"] + "|" + playerStats[i]["min"] + "|" + playerStats[i]["fgm"] + "-" + playerStats[i]["fga"] + "|" + playerStats[i]["tpm"] + "-" + playerStats[i]["tpa"] + "|" + playerStats[i]["ftm"] + "-" + playerStats[i]["fta"] + "|" + playerStats[i]["offReb"] + "|" + playerStats[i]["defReb"] + "|" + playerStats[i]["totReb"] + "|" + playerStats[i]["assists"] + "|" + playerStats[i]["steals"] + "|" + playerStats[i]["blocks"] + "|" + playerStats[i]["turnovers"] + "|" + playerStats[i]["pFouls"] + "|" + playerStats[i]["plusMinus"] + "|" + playerStats[i]["points"] + "|\n"
  elif playerStats[i]["teamId"] != tabulateList[game]["visitorTeamId"]:
    body += "|" + findPlayerName(dataPlayersLeague, playerStats[i]["personId"]) + "|" + playerStats[i]["min"] + "|" + playerStats[i]["fgm"] + "-" + playerStats[i]["fga"] + "|" + playerStats[i]["tpm"] + "-" + playerStats[i]["tpa"] + "|" + playerStats[i]["ftm"] + "-" + playerStats[i]["fta"] + "|" + playerStats[i]["offReb"] + "|" + playerStats[i]["defReb"] + "|" + playerStats[i]["totReb"] + "|" + playerStats[i]["assists"] + "|" + playerStats[i]["steals"] + "|" + playerStats[i]["blocks"] + "|" + playerStats[i]["turnovers"] + "|" + playerStats[i]["pFouls"] + "|" + playerStats[i]["plusMinus"] + "|" + playerStats[i]["points"] + "|\n"

body += '''
**Game Details**

**Game Duration:** ''' + tabulateList[game]["gameDuration"] + '''

**Game Officials:** ''' + basicGameData["officials"]["formatted"][0]["firstNameLastName"] + ", " + basicGameData["officials"]["formatted"][1]["firstNameLastName"] + " and " + basicGameData["officials"]["formatted"][2]["firstNameLastName"] + '''

**Game Attendance:** ''' + basicGameData["attendance"] + '''

**Arena Name:** ''' + basicGameData["arena"]["name"]

reddit.subreddit('test').submit(tabulateList[game]["title"], selftext=body)