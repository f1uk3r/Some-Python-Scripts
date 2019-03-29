# python3
# reddit-boxscore-bot.py by f1uk3r-- reads the data from stats.nba.net and makes a posts Postgame Thread on specified subreddit 
# pip install requests, praw
# this script should be run only if the game is in 4th quarter or above

import json
from datetime import date, timedelta, datetime
import time
import random
import praw
import requests
import config_reddit


# Team Dictionary helps to make urls for boxscore and for full-forms of abbrevation of teams
teamDict = {
    "ATL": ["Atlanta Hawks","01", "atlanta-hawks-",
            "/r/atlantahawks", "1610612737", "Hawks"],
    "BKN": ["Brooklyn Nets", "02", "boston-celtics-",
            "/r/bostonceltics", "1610612738", "Nets"],
    "BOS": ["Boston Celtics", "17", "brooklyn-nets-",
            "/r/gonets", "1610612751", "Celtics"],
    "CHA": ["Charlotte Hornets", "30", "charlotte-hornets-",
            "/r/charlottehornets", "1610612766", "Hornets"],
    "CHI": ["Chicago Bulls", "04", "chicago-bulls-",
            "/r/chicagobulls", "1610612741", "Bulls"],
    "CLE": ["Cleveland Cavaliers", "05", "cleveland-cavaliers-",
            "/r/clevelandcavs", "1610612739", "Cavaliers"],
    "DAL": ["Dallas Mavericks", "06", "dallas-mavericks-",
            "/r/mavericks", "1610612742", "Mavericks"],
    "DEN": ["Denver Nuggets", "07", "denver-nuggets-",
            "/r/denvernuggets", "1610612743", "Nuggets"],
    "DET": ["Detroit Pistons", "08", "detroit-pistons-",
            "/r/detroitpistons", "1610612765", "Pistons"],
    "GSW": ["Golden State Warriors", "09", "golden-state-warriors-",
            "/r/warriors", "1610612744", "Warriors"],
    "HOU": ["Houston Rockets", "10", "houston-rockets-",
            "/r/rockets", "1610612745", "Rockets"],
    "IND": ["Indiana Pacers", "11", "indiana-pacers-",
            "/r/pacers", "1610612754", "Pacers"],
    "LAC": ["Los Angeles Clippers", "12", "los-angeles-clippers-",
            "/r/laclippers", "1610612746", "Clippers"],
    "LAL": ["Los Angeles Lakers", "13", "los-angeles-lakers-",
            "/r/lakers", "1610612747", "Lakers"],
    "MEM": ["Memphis Grizzlies", "29", "memphis-grizzlies-",
            "/r/memphisgrizzlies", "1610612763", "Grizzlies"],
    "MIA": ["Miami Heat", "14", "miami-heat-",
            "/r/heat", "1610612748", "Heat"],
    "MIL": ["Milwaukee Bucks", "15", "milwaukee-bucks-",
            "/r/mkebucks", "1610612749", "Bucks"],
    "MIN": ["Minnesota Timberwolves", "16", "minnesota-timberwolves-",
            "/r/timberwolves", "1610612750", "Timberwolves"],
    "NOP": ["New Orleans Pelicans", "03", "new-orleans-pelicans-",
            "/r/nolapelicans", "1610612740", "Pelicans"],
    "NYK": ["New York Knicks", "18", "new-york-knicks-",
            "/r/nyknicks", "1610612752", "Knicks"],
    "OKC": ["Oklahoma City Thunder", "25", "oklahoma-city-thunder-",
            "/r/thunder", "1610612760", "Thunder"],
    "ORL": ["Orlando Magic", "19", "orlando-magic-",
            "/r/orlandomagic", "1610612753", "Magic"],
    "PHI": ["Philadelphia 76ers", "20", "philadelphia-76ers-",
            "/r/sixers", "1610612755", "76ers"],
    "PHX": ["Phoenix Suns", "21", "phoenix-suns-",
            "/r/suns", "1610612756", "Suns"],
    "POR": ["Portland Trail Blazers", "22", "portland-trail-blazers-",
            "/r/ripcity", "1610612757", "Trail Blazers"],
    "SAC": ["Sacramento Kings", "23", "sacramento-kings-",
            "/r/kings", "1610612758", "Kings"],
    "SAS": ["San Antonio Spurs", "24", "san-antonio-spurs-",
            "/r/nbaspurs", "1610612759", "Spurs"],
    "TOR": ["Toronto Raptors", "28", "toronto-raptors-",
            "/r/torontoraptors", "1610612761", "Raptors"],
    "UTA": ["Utah Jazz", "26", "utah-jazz-",
            "/r/utahjazz", "1610612762", "Jazz"],
    "WAS": ["Washington Wizards", "27", "washington-wizards-",
            "/r/washingtonwizards", "1610612764, ", "Wizards"]
}


# getting a reddit instance by giving appropiate credentials
reddit = praw.Reddit(
            username = config_reddit.username, 
            password = config_reddit.password,
            client_id = config_reddit.client_id, 
            client_secret = config_reddit.client_secret,
            user_agent = "script:rnba-game-thread-bot:v2.0 (by /u/f1uk3r)")


def requestApi(url):
    req = requests.get(url)
    return req.json()


def appendPlusMinus(someStat):
    """
    someStat is any stat
    appendPlusMinus just appends sign in front of stat in question 
    and returns it
    """
    if someStat.isdigit():
        if int(someStat)>0:
            return "+" + str(someStat)
        return str(someStat)
    else:
        return str(someStat)


def findPlayerName(dataPlayersLeague, playerId):
    """
    dataPlayerLeague is a list of all the players in the league
    data.nba.net have playerId parameter instead of player name
    function finds and returns player's name from dataPlayerLeague list 
    by playerId
    """
    for each in dataPlayersLeague:
        if each["personId"] == playerId:
            return each["firstName"] + " " + each["lastName"]


def beforeGameThread(basicGameData, date, teamDict): 
    """
    Variable basicGameData have live data
    Variable date is today's date
    Variable teamDict is the variable Dictionary at the top
    Function beforeGamePost setups the body of the thread before game starts
    and return body and title of the post
    """
    nbaUrlBoxscore = ("http://watch.nba.com/game/" + date + "/" 
                    + basicGameData["vTeam"]["triCode"] 
                    + basicGameData["hTeam"]["triCode"] + "#/boxscore")
    nbaUrlPreview = ("http://watch.nba.com/game/" + date + "/"
                    + basicGameData["vTeam"]["triCode"]
                    + basicGameData["hTeam"]["triCode"] + "#/preview")
    nbaUrlPlayByPlay = ("http://watch.nba.com/game/" + date + "/"
                    + basicGameData["vTeam"]["triCode"]
                    + basicGameData["hTeam"]["triCode"] + "#/matchup")
    nbaUrlMatchup = ("http://watch.nba.com/game/" + date + "/"
                    + basicGameData["vTeam"]["triCode"]
                    + basicGameData["hTeam"]["triCode"] + "#/pbp")
    timeEasternRaw = basicGameData["startTimeEastern"]
    timeOnlyEastern = timeEasternRaw[:5]
    if timeOnlyEastern[:2].isdigit():
        timeEasternHour = int(timeOnlyEastern[:2])
        timeEasternMinute = int(timeOnlyEastern[3:])
    else:
        timeEasternHour = int(timeOnlyEastern[:1])
        timeEasternMinute = int(timeOnlyEastern[2:])

    if timeEasternMinute==0:
        timeMinuteFinal = 59
        timeEasternHourFinal = timeEasternHour - 1
    else:
        timeMinuteFinal = timeEasternMinute - 1
        timeEasternHourFinal = timeEasternHour
    timeCentralHourFinal = timeEasternHourFinal - 1
    timeMountainHourFinal = timeCentralHourFinal - 1
    timePacificHourFinal = timeMountainHourFinal - 1


    beforeGameBody = """##General Information

**TIME**     |**MEDIA**                            |**LOCATION**        |
:------------|:------------------------------------|:-------------------|
{0}:{4} PM Eastern |**Game Preview**: [NBA.com]({5}) | {9}               | 
{1}:{4} PM Central |**Game Matchup**: [NBA.com]({6}) | **Team Subreddits**|
{2}:{4} PM Mountain|**Play By Play**: [NBA.com]({7})| {10}          |
{3}:{4} PM Pacific |**Box Score**: [NBA.com]({8}) | {11}          |

-----

[Reddit Stream](https://reddit-stream.com/comments/auto) (You must click this link from the comment page.)
""".format(
        str(timeEasternHourFinal), str(timeCentralHourFinal), 
        str(timeMountainHourFinal), str(timePacificHourFinal), 
        str(timeMinuteFinal), nbaUrlPreview, 
        nbaUrlMatchup, nbaUrlPlayByPlay, 
        nbaUrlBoxscore, basicGameData["arena"]["name"], 
        teamDict[basicGameData["vTeam"]["triCode"]][3], 
        teamDict[basicGameData["hTeam"]["triCode"]][3])

    title = ("GAME THREAD: " + teamDict[basicGameData["vTeam"]["triCode"]][0]
            + " (" + basicGameData["vTeam"]["win"] + "-"
            + basicGameData["vTeam"]["loss"] + ") @ "
            + teamDict[basicGameData["hTeam"]["triCode"]][0] + " ("
            + basicGameData["hTeam"]["win"] + "-"
            + basicGameData["hTeam"]["loss"] + ") - (" + dateTitle + ")")

    return beforeGameBody, title


def editGameThread(boxScoreData, bodyText, date, teamDict):
    """
    Variable boxScoreData have live data
    Variable bodyText have body when the post was originally created
    Variable date is today's date
    Variable teamDict is the variable Dictionary at the top
    Returns whole bodyText for editing
    """
    basicGameData = boxScoreData["basicGameData"]
    allStats = boxScoreData["stats"]
    nbaUrl = ("http://watch.nba.com/game/" + date + "/" 
            + basicGameData["vTeam"]["triCode"] 
            + basicGameData["hTeam"]["triCode"] + "#/boxscore")
    yahooUrl = ("http://sports.yahoo.com/nba/" 
            + teamDict[basicGameData["vTeam"]["triCode"]][2] 
            + teamDict[basicGameData["hTeam"]["triCode"]][2] 
            + date + teamDict[basicGameData["hTeam"]["triCode"]][1])
    playerStats = allStats["activePlayers"]
    body = bodyText + """
||		
|:-:|		
|[](/""" + basicGameData["vTeam"]["triCode"] + ") **" + basicGameData["vTeam"]["score"]  + " - " + basicGameData["hTeam"]["score"] + "** [](/" + basicGameData["hTeam"]["triCode"] + """)|
|**Box Scores: [NBA](""" + nbaUrl + ") & [Yahoo](" + yahooUrl + """)**|		


||
|:-:|											
|&nbsp;|		
|**GAME SUMMARY**|	
|**Location:** """ + basicGameData["arena"]["name"] + "(" + basicGameData["attendance"] + "), **Clock:** " + basicGameData["clock"] + """|
|**Officials:** """ + basicGameData["officials"]["formatted"][0]["firstNameLastName"] + ", " + basicGameData["officials"]["formatted"][1]["firstNameLastName"] + " and " + basicGameData["officials"]["formatted"][2]["firstNameLastName"] + """|	

|**Team**|**Q1**|**Q2**|**Q3**|**Q4**|**"""
    #Condition for normal games
    if len(basicGameData["vTeam"]["linescore"])==4:
        body += """Total**|
|:---|:--|:--|:--|:--|:--|
|""" + teamDict[basicGameData["vTeam"]["triCode"]][0] + "|" + basicGameData["vTeam"]["linescore"][0]["score"] + "|" + basicGameData["vTeam"]["linescore"][1]["score"] + "|" + basicGameData["vTeam"]["linescore"][2]["score"] + "|" + basicGameData["vTeam"]["linescore"][3]["score"] + "|"+ basicGameData["vTeam"]["score"] + """|
|""" + teamDict[basicGameData["hTeam"]["triCode"]][0] + "|" + basicGameData["hTeam"]["linescore"][0]["score"] + "|" + basicGameData["hTeam"]["linescore"][1]["score"] + "|" + basicGameData["hTeam"]["linescore"][2]["score"] + "|" + basicGameData["hTeam"]["linescore"][3]["score"] + "|"+ basicGameData["hTeam"]["score"] + "|\n"
  #condition for OT game
    elif len(basicGameData["vTeam"]["linescore"])>4:
    #appending OT columns
        for i in range(4, len(basicGameData["vTeam"]["linescore"])):
            body += "OT" + str(i-3) + "**|**"
        body += """Total**|
|:---|:--|:--|:--|:--|:--|"""
      #increase string ":--|" according to number of OT
        for i in range(4, len(basicGameData["vTeam"]["linescore"])):
            body += ":--|"
        body += "\n|" + teamDict[basicGameData["vTeam"]["triCode"]][0] + "|"
        for i in range(len(basicGameData["vTeam"]["linescore"])):
            body += basicGameData["vTeam"]["linescore"][i]["score"] + "|"
        body += basicGameData["vTeam"]["score"] + """|
|""" + teamDict[basicGameData["hTeam"]["triCode"]][0] + "|"
        for i in range(len(basicGameData["hTeam"]["linescore"])):
            body += basicGameData["hTeam"]["linescore"][i]["score"] + "|"
        body += basicGameData["hTeam"]["score"] + "|\n"

    body += """
||		
|:-:|		
|&nbsp;|		
|**TEAM STATS**|

|**Team**|**PTS**|**FG**|**FG%**|**3P**|**3P%**|**FT**|**FT%**|**OREB**|**TREB**|**AST**|**PF**|**STL**|**TO**|**BLK**|
|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|
|""" + teamDict[basicGameData["vTeam"]["triCode"]][0] + "|" + allStats["vTeam"]["totals"]["points"] + "|" + allStats["vTeam"]["totals"]["fgm"] + "-" + allStats["vTeam"]["totals"]["fga"] + "|" + allStats["vTeam"]["totals"]["fgp"] + "%|" + allStats["vTeam"]["totals"]["tpm"] + "-" + allStats["vTeam"]["totals"]["tpa"] + "|" + allStats["vTeam"]["totals"]["tpp"] + "%|" + allStats["vTeam"]["totals"]["ftm"] + "-" + allStats["vTeam"]["totals"]["fta"] + "|" + allStats["vTeam"]["totals"]["ftp"] + "%|" + allStats["vTeam"]["totals"]["offReb"] + "|" + allStats["vTeam"]["totals"]["totReb"] + "|" + allStats["vTeam"]["totals"]["assists"] + "|" + allStats["vTeam"]["totals"]["pFouls"] + "|" + allStats["vTeam"]["totals"]["steals"] + "|" + allStats["vTeam"]["totals"]["turnovers"] + "|" + allStats["vTeam"]["totals"]["blocks"] + """|
|""" + teamDict[basicGameData["hTeam"]["triCode"]][0] + "|" + allStats["hTeam"]["totals"]["points"] + "|" + allStats["hTeam"]["totals"]["fgm"] + "-" + allStats["hTeam"]["totals"]["fga"] + "|" + allStats["hTeam"]["totals"]["fgp"] + "%|" + allStats["hTeam"]["totals"]["tpm"] + "-" + allStats["hTeam"]["totals"]["tpa"] + "|" + allStats["hTeam"]["totals"]["tpp"] + "%|" + allStats["hTeam"]["totals"]["ftm"] + "-" + allStats["hTeam"]["totals"]["fta"] + "|" + allStats["hTeam"]["totals"]["ftp"] + "%|" + allStats["hTeam"]["totals"]["offReb"] + "|" + allStats["hTeam"]["totals"]["totReb"] + "|" + allStats["hTeam"]["totals"]["assists"] + "|" + allStats["hTeam"]["totals"]["pFouls"] + "|" + allStats["hTeam"]["totals"]["steals"] + "|" + allStats["hTeam"]["totals"]["turnovers"] + "|" + allStats["hTeam"]["totals"]["blocks"] + """|

|**Team**|**Biggest Lead**|**Longest Run**|**PTS: In Paint**|**PTS: Off TOs**|**PTS: Fastbreak**|
|:--|:--|:--|:--|:--|:--|
|""" + teamDict[basicGameData["vTeam"]["triCode"]][0] + "|" + appendPlusMinus(allStats["vTeam"]["biggestLead"]) + "|" + allStats["vTeam"]["longestRun"] + "|" + allStats["vTeam"]["pointsInPaint"] + "|" + allStats["vTeam"]["pointsOffTurnovers"] + "|" + allStats["vTeam"]["fastBreakPoints"] + """|
|""" + teamDict[basicGameData["hTeam"]["triCode"]][0] + "|" + appendPlusMinus(allStats["hTeam"]["biggestLead"]) + "|" + allStats["hTeam"]["longestRun"] + "|" + allStats["hTeam"]["pointsInPaint"] + "|" + allStats["hTeam"]["pointsOffTurnovers"] + "|" + allStats["hTeam"]["fastBreakPoints"] + """|

||		
|:-:|		
|&nbsp;|		
|**TEAM LEADERS**|

|**Team**|**Points**|**Rebounds**|**Assists**|
|:--|:--|:--|:--|
|""" + teamDict[basicGameData["vTeam"]["triCode"]][0] + "|**" + allStats["vTeam"]["leaders"]["points"]["value"] + "** " + findPlayerName(dataPlayersLeague, allStats["vTeam"]["leaders"]["points"]["players"][0]["personId"]) + "|**" + allStats["vTeam"]["leaders"]["rebounds"]["value"] + "** " + findPlayerName(dataPlayersLeague, allStats["vTeam"]["leaders"]["rebounds"]["players"][0]["personId"])  + "|**" + allStats["vTeam"]["leaders"]["assists"]["value"] + "** " + findPlayerName(dataPlayersLeague, allStats["vTeam"]["leaders"]["assists"]["players"][0]["personId"]) + """|
|""" + teamDict[basicGameData["hTeam"]["triCode"]][0] + "|**" + allStats["hTeam"]["leaders"]["points"]["value"] + "** " + findPlayerName(dataPlayersLeague, allStats["hTeam"]["leaders"]["points"]["players"][0]["personId"]) + "|**" + allStats["hTeam"]["leaders"]["rebounds"]["value"] + "** " + findPlayerName(dataPlayersLeague, allStats["hTeam"]["leaders"]["rebounds"]["players"][0]["personId"])  + "|**" + allStats["hTeam"]["leaders"]["assists"]["value"] + "** " + findPlayerName(dataPlayersLeague, allStats["hTeam"]["leaders"]["assists"]["players"][0]["personId"]) + """|

||		
|:-:|		
|&nbsp;|		
|**PLAYER STATS**|

||||||||||||||||
|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|
**[](/""" + basicGameData["vTeam"]["triCode"] + ") " + teamDict[basicGameData["vTeam"]["triCode"]][0].rsplit(None, 1)[-1].upper() + """**|**MIN**|**FGM-A**|**3PM-A**|**FTM-A**|**ORB**|**DRB**|**REB**|**AST**|**STL**|**BLK**|**TO**|**PF**|**+/-**|**PTS**|
"""

  #players stats are filled here, only starters have "pos" property (away team)
    for i in range(len(playerStats)):
        if playerStats[i]["teamId"] == basicGameData["vTeam"]["teamId"] and playerStats[i]["pos"] != "":
            body += "|" + findPlayerName(dataPlayersLeague, playerStats[i]["personId"]) + "^" + playerStats[i]["pos"] + "|" + playerStats[i]["min"] + "|" + playerStats[i]["fgm"] + "-" + playerStats[i]["fga"] + "|" + playerStats[i]["tpm"] + "-" + playerStats[i]["tpa"] + "|" + playerStats[i]["ftm"] + "-" + playerStats[i]["fta"] + "|" + playerStats[i]["offReb"] + "|" + playerStats[i]["defReb"] + "|" + playerStats[i]["totReb"] + "|" + playerStats[i]["assists"] + "|" + playerStats[i]["steals"] + "|" + playerStats[i]["blocks"] + "|" + playerStats[i]["turnovers"] + "|" + playerStats[i]["pFouls"] + "|" + appendPlusMinus(playerStats[i]["plusMinus"]) + "|" + playerStats[i]["points"] + "|\n"
        elif playerStats[i]["teamId"] == basicGameData["vTeam"]["teamId"]:
            body += "|" + findPlayerName(dataPlayersLeague, playerStats[i]["personId"]) + "|" + playerStats[i]["min"] + "|" + playerStats[i]["fgm"] + "-" + playerStats[i]["fga"] + "|" + playerStats[i]["tpm"] + "-" + playerStats[i]["tpa"] + "|" + playerStats[i]["ftm"] + "-" + playerStats[i]["fta"] + "|" + playerStats[i]["offReb"] + "|" + playerStats[i]["defReb"] + "|" + playerStats[i]["totReb"] + "|" + playerStats[i]["assists"] + "|" + playerStats[i]["steals"] + "|" + playerStats[i]["blocks"] + "|" + playerStats[i]["turnovers"] + "|" + playerStats[i]["pFouls"] + "|" + appendPlusMinus(playerStats[i]["plusMinus"]) + "|" + playerStats[i]["points"] + "|\n"

    body += """**[](/""" + basicGameData["hTeam"]["triCode"] + ") " + teamDict[basicGameData["hTeam"]["triCode"]][0].rsplit(None, 1)[-1].upper() + """**|**MIN**|**FGM-A**|**3PM-A**|**FTM-A**|**ORB**|**DRB**|**REB**|**AST**|**STL**|**BLK**|**TO**|**PF**|**+/-**|**PTS**|
"""
  #home team players
    for i in range(len(playerStats)):
        if playerStats[i]["teamId"] != basicGameData["vTeam"]["teamId"] and playerStats[i]["pos"] != "":
            body += "|" + findPlayerName(dataPlayersLeague, playerStats[i]["personId"]) + "^" + playerStats[i]["pos"] + "|" + playerStats[i]["min"] + "|" + playerStats[i]["fgm"] + "-" + playerStats[i]["fga"] + "|" + playerStats[i]["tpm"] + "-" + playerStats[i]["tpa"] + "|" + playerStats[i]["ftm"] + "-" + playerStats[i]["fta"] + "|" + playerStats[i]["offReb"] + "|" + playerStats[i]["defReb"] + "|" + playerStats[i]["totReb"] + "|" + playerStats[i]["assists"] + "|" + playerStats[i]["steals"] + "|" + playerStats[i]["blocks"] + "|" + playerStats[i]["turnovers"] + "|" + playerStats[i]["pFouls"] + "|" + appendPlusMinus(playerStats[i]["plusMinus"]) + "|" + playerStats[i]["points"] + "|\n"
        elif playerStats[i]["teamId"] != basicGameData["vTeam"]["teamId"] and playerStats[i]["pos"] == "":
            body += "|" + findPlayerName(dataPlayersLeague, playerStats[i]["personId"]) + "|" + playerStats[i]["min"] + "|" + playerStats[i]["fgm"] + "-" + playerStats[i]["fga"] + "|" + playerStats[i]["tpm"] + "-" + playerStats[i]["tpa"] + "|" + playerStats[i]["ftm"] + "-" + playerStats[i]["fta"] + "|" + playerStats[i]["offReb"] + "|" + playerStats[i]["defReb"] + "|" + playerStats[i]["totReb"] + "|" + playerStats[i]["assists"] + "|" + playerStats[i]["steals"] + "|" + playerStats[i]["blocks"] + "|" + playerStats[i]["turnovers"] + "|" + playerStats[i]["pFouls"] + "|" + appendPlusMinus(playerStats[i]["plusMinus"]) + "|" + playerStats[i]["points"] + "|\n"
      #footer
    body += """
||
|:-:|
|^[bot-script](https://github.com/f1uk3r/Some-Python-Scripts/blob/master/reddit-nba-bot/reddit-boxscore-bot.py) ^by ^/u/f1uk3r|  """
    return body

#finding date of game
now = date.today() - timedelta(1)
dateToday = now.strftime("%Y%m%d")          # Check the date before using script
dateTitle = now.strftime("%B %d, %Y")
#print(date)

#getting today's game
data = requestApi("http://data.nba.net/prod/v1/" + dateToday + "/scoreboard.json")
gamesToday = data["numGames"]
games = data["games"]

#getting informations of players through API
dataPlayers = requestApi("http://data.nba.net/prod/v1/2018/players.json")
dataPlayersLeague = (dataPlayers["league"]["standard"]
                    + dataPlayers["league"]["africa"]
                    + dataPlayers["league"]["sacramento"]
                    + dataPlayers["league"]["vegas"]
                    + dataPlayers["league"]["utah"])


redditGamePostList = []
print(len(games))
while True:
    for i in range(len(games)):
        print(i, len(redditGamePostList))
        if  i < len(redditGamePostList):
            dataBoxScore = requestApi("http://data.nba.net/prod/v1/" + dateToday
                                        + "/" + str(games[i]["gameId"]) 
                                        + "_boxscore.json")

            basicGameData = dataBoxScore["basicGameData"]
            if redditGamePostList[i] is not None:
                gameStartTime = datetime.strptime(
                                basicGameData["startTimeUTC"][:19],
                                                '%Y-%m-%dT%H:%M:%S')
                timeNow = datetime.utcnow()
                timeDifference = gameStartTime-timeNow
                if ((timeDifference.seconds  > 0 and timeDifference.days == 0) or
                    (timeDifference.seconds  < 300 and timeDifference.days == -1)):
                    print(timeDifference.days, timeDifference.seconds)
                elif not ((basicGameData["clock"] == "0.0" or 
                        basicGameData["clock"] == "") and 
                        basicGameData["period"]["current"] >= 4 and 
                        (basicGameData["vTeam"]["score"] 
                        != basicGameData["hTeam"]["score"])):
                #if all of the above condition met then
                    redditGamePostList[i]["postResponse"].edit(editGameThread(
                                                dataBoxScore, 
                                                redditGamePostList[i]["bodyText"], 
                                                dateToday, teamDict))
                else:
                    basicGameData = dataBoxScore["basicGameData"]
                    redditGamePostList[i]["postResponse"].edit(editGameThread(
                                                dataBoxScore, 
                                                redditGamePostList[i]["bodyText"], 
                                                dateToday, teamDict))
                    redditGamePostList[i] = None
        else:
            dataBoxScore = requestApi("http://data.nba.net/prod/v1/" + dateToday
                                        + "/" + str(games[i]["gameId"]) 
                                        + "_boxscore.json")
            basicGameData = dataBoxScore["basicGameData"]
            gameStartTime = datetime.strptime(
                            basicGameData["startTimeUTC"][:19], '%Y-%m-%dT%H:%M:%S')
            timeNow = datetime.utcnow()
            timeDifference = gameStartTime-timeNow
            if timeDifference.seconds  < 3600 or timeDifference.days == -1:
                bodyPost, title = beforeGameThread(basicGameData, 
                                                    dateToday, teamDict)
                response = reddit.subreddit('nbameme').submit(title, 
                                                        selftext=bodyPost,
                                                        send_replies=False)
                redditGamePostList.append({"postResponse":response, 
                                            "bodyText":bodyPost})
                print(title)
    time.sleep(60)
    if all(game is None for game in redditGamePostList):
        break