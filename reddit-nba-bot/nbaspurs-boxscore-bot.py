# python3
# reddit-boxscore-bot.py by f1uk3r-- reads the data from stats.nba.net and makes a posts Postgame Thread on specified subreddit 
# pip install requests, praw
import praw
import config
import requests
import json
from datetime import date, timedelta, datetime
from time import sleep


#Team Dictionary helps to make urls for boxscore and for full-forms of abbrevation of teams
teamDict = {
    "ATL": ["Atlanta Hawks", "01", "atlanta-hawks-",
            "/r/atlantahawks", "1610612737", "Hawks"],
    "BKN": ["Brooklyn Nets", "17", "brooklyn-nets-",
            "/r/gonets", "1610612751", "Nets"],
    "BOS": ["Boston Celtics", "02", "boston-celtics-",
            "/r/bostonceltics", "1610612738", "Celtics"],
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
#getting a reddit instance by giving appropiate credentials
reddit = praw.Reddit(username = config.username, 
                    password = config.password,
                    client_id = config.client_id, 
                    client_secret = config.client_secret,
                    user_agent = "script:rnbaspurs-post-game-thread-bot:v1.0 (by /u/f1uk3r)")

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
    if each["vTeam"]["triCode"] == "SAS" or each["hTeam"]["triCode"] == "SAS":
        visitorTeam = teamDict[each["vTeam"]["triCode"]][0] + " (" + each["vTeam"]["win"] + "-" + each["vTeam"]["loss"] + ")"
        homeTeam = teamDict[each["hTeam"]["triCode"]][0] + " (" + each["hTeam"]["win"] + "-" + each["hTeam"]["loss"] + ")"
        print(str(index) + "    " + each["gameId"] + "    " + visitorTeam + " @ " + homeTeam)
        spursGameInfo = {"index": index, "gameId": each["gameId"], "visitorTeam": each["vTeam"]["triCode"], "homeTeam": each["hTeam"]["triCode"]}

dataBoxScore = requestApi("http://data.nba.net/prod/v1/" + date + "/" + str(spursGameInfo["gameId"]) + "_boxscore.json")
basicGameData = dataBoxScore["basicGameData"] #contains all the data related to this game
allStats = dataBoxScore["stats"]  #contains all the stats of this game
playerStats = allStats["activePlayers"] #contains all the stats of players of the team
loopStatus = not ((basicGameData["clock"] == "0.0" or basicGameData["clock"] == "") and basicGameData["period"]["current"] >= 4 and (basicGameData["vTeam"]["score"] != basicGameData["hTeam"]["score"]))
clockOld = basicGameData["clock"]

while loopStatus:
    dataBoxScore = requestApi("http://data.nba.net/prod/v1/" + date + "/" + str(spursGameInfo["gameId"]) + "_boxscore.json")
    basicGameData = dataBoxScore["basicGameData"] #contains all the data related to this game
    allStats = dataBoxScore["stats"]  #contains all the stats of this game
    playerStats = allStats["activePlayers"] #contains all the stats of players of the team
    loopStatus = not ((basicGameData["clock"] == "0.0" or basicGameData["clock"] == "") and basicGameData["period"]["current"] >= 4 and (basicGameData["vTeam"]["score"] != basicGameData["hTeam"]["score"]))
    if basicGameData["clock"] != clockOld:
        print(basicGameData["clock"] + " " + basicGameData["vTeam"]["triCode"] + " " + basicGameData["vTeam"]["score"]  + " - " + basicGameData["hTeam"]["score"] + " " + basicGameData["hTeam"]["triCode"])
    clockOld = basicGameData["clock"]
    time.sleep(30)

visitorTeamScore = basicGameData["vTeam"]["score"]
homeTeamScore = basicGameData["hTeam"]["score"]
#when game is activated, win-loss fields aren't updated. Check isGameActivated and update win-loss manually.
if basicGameData["isGameActivated"] == False:
    visitorTeam = teamDict[basicGameData["vTeam"]["triCode"]][0] + " (" + basicGameData["vTeam"]["seriesWin"] + "-" + basicGameData["vTeam"]["seriesLoss"] + ")"
    homeTeam = teamDict[basicGameData["hTeam"]["triCode"]][0] + " (" + basicGameData["hTeam"]["seriesWin"] + "-" + basicGameData["hTeam"]["seriesLoss"] + ")"
elif basicGameData["isGameActivated"] == True and ((int(visitorTeamScore) > int(homeTeamScore)) and len(basicGameData["vTeam"]["linescore"])>=4):
    visitorTeam = teamDict[basicGameData["vTeam"]["triCode"]][0] + " (" + str(int(basicGameData["vTeam"]["seriesWin"])+1) + "-" + basicGameData["vTeam"]["seriesLoss"] + ")"
    homeTeam = teamDict[basicGameData["hTeam"]["triCode"]][0] + " (" + basicGameData["hTeam"]["seriesWin"] + "-" + str(int(basicGameData["hTeam"]["seriesLoss"])+1) + ")"
elif basicGameData["isGameActivated"] == True and ((int(visitorTeamScore) < int(homeTeamScore)) and len(basicGameData["vTeam"]["linescore"])>=4):
    visitorTeam = teamDict[basicGameData["vTeam"]["triCode"]][0] + " (" + basicGameData["vTeam"]["seriesWin"] + "-" + str(int(basicGameData["vTeam"]["seriesLoss"])+1) + ")"
    homeTeam = teamDict[basicGameData["hTeam"]["triCode"]][0] + " (" + str(int(basicGameData["hTeam"]["seriesWin"])+1) + "-" + basicGameData["hTeam"]["seriesLoss"] + ")"
print(visitorTeam, homeTeam)

  #title is created here, 
if (int(visitorTeamScore) > int(homeTeamScore)) and len(basicGameData["vTeam"]["linescore"])==4:
    title = "[Post Game Thread] The " + visitorTeam + " defeat the " + homeTeam + ", " + visitorTeamScore + " - " + homeTeamScore
elif (int(visitorTeamScore) > int(homeTeamScore)) and len(basicGameData["vTeam"]["linescore"])>4:
    title = "[Post Game Thread] The " + visitorTeam + " defeat the " + homeTeam + " in OT, " + visitorTeamScore + " - " + homeTeamScore
elif (int(visitorTeamScore) < int(homeTeamScore)) and len(basicGameData["vTeam"]["linescore"])==4:
    title = "[Post Game Thread] The " + homeTeam + " defeat the visiting " + visitorTeam + ", " + homeTeamScore + " - " + visitorTeamScore
elif (int(visitorTeamScore) < int(homeTeamScore)) and len(basicGameData["vTeam"]["linescore"])>4:
    title = "[Post Game Thread] The " + homeTeam + " defeat the visiting " + visitorTeam + " in OT, " + homeTeamScore + " - " + visitorTeamScore
  
#calculates url to boxscores on nba and yahoo websites
vTeamBasicData = basicGameData["vTeam"]
hTeamBasicData = basicGameData["hTeam"]
nbaUrl = ("http://watch.nba.com/game/" + date + "/"
            + vTeamBasicData["triCode"]
            + hTeamBasicData["triCode"] + "#/boxscore")
yahooUrl = ("http://sports.yahoo.com/nba/"
            + teamDict[vTeamBasicData["triCode"]][2]
            + teamDict[hTeamBasicData["triCode"]][2]
            + date + teamDict[hTeamBasicData["triCode"]][1])
playerStats = allStats["activePlayers"]
body = """
||		
|:-:|		
|[](/{vTeamLogo}) **{vTeamScore} -  {hTeamScore}** [](/{hTeamLogo})|
|**Box Scores: [NBA]({nbaurl}) & [Yahoo]({yahoourl})**|
""".format(
            vTeamLogo = vTeamBasicData["triCode"],
            vTeamScore = vTeamBasicData["score"],
            hTeamScore = hTeamBasicData["score"],
            hTeamLogo = hTeamBasicData["triCode"],
            nbaurl = nbaUrl,
            yahoourl = yahooUrl
)

body += """
||
|:-:|											
|&nbsp;|		
|**GAME SUMMARY**|	
|**Location:** {arena}({attendance}), **Clock:** {clock}|
|**Officials:** {referee1}, {referee2} and {referee3}|
""".format(
            arena = basicGameData["arena"]["name"],
            attendance = basicGameData["attendance"],
            clock = basicGameData["clock"],
            referee1 = basicGameData["officials"]["formatted"][0]["firstNameLastName"],
            referee2 = basicGameData["officials"]["formatted"][1]["firstNameLastName"],
            referee3 = basicGameData["officials"]["formatted"][2]["firstNameLastName"]
)

body += """
|**Team**|**Q1**|**Q2**|**Q3**|**Q4**|**"""
# Condition for normal games
if len(vTeamBasicData["linescore"]) == 4:
    body += """Total**|
|:---|:--|:--|:--|:--|:--|
|""" + teamDict[vTeamBasicData["triCode"]][0] + "|" + vTeamBasicData["linescore"][0]["score"] + "|" + \
                vTeamBasicData["linescore"][1]["score"] + "|" + vTeamBasicData["linescore"][2][
                    "score"] + "|" + vTeamBasicData["linescore"][3]["score"] + "|" + vTeamBasicData[
                    "score"] + """|
|""" + teamDict[hTeamBasicData["triCode"]][0] + "|" + hTeamBasicData["linescore"][0]["score"] + "|" + \
                hTeamBasicData["linescore"][1]["score"] + "|" + hTeamBasicData["linescore"][2][
                    "score"] + "|" + hTeamBasicData["linescore"][3]["score"] + "|" + hTeamBasicData[
                    "score"] + "|\n"
    # condition for OT game
elif len(vTeamBasicData["linescore"]) > 4:
        # appending OT columns
    for i in range(4, len(vTeamBasicData["linescore"])):
        body += "OT" + str(i - 3) + "**|**"
    body += """Total**|
|:---|:--|:--|:--|:--|:--|"""
        # increase string ":--|" according to number of OT
    for i in range(4, len(vTeamBasicData["linescore"])):
        body += ":--|"
    body += "\n|" + teamDict[vTeamBasicData["triCode"]][0] + "|"
    for i in range(len(vTeamBasicData["linescore"])):
        body += vTeamBasicData["linescore"][i]["score"] + "|"
    body += vTeamBasicData["score"] + """|
|""" + teamDict[hTeamBasicData["triCode"]][0] + "|"
    for i in range(len(hTeamBasicData["linescore"])):
        body += hTeamBasicData["linescore"][i]["score"] + "|"
    body += hTeamBasicData["score"] + "|\n"

body += """
||		
|:-:|		
|&nbsp;|		
|**TEAM STATS**|

|**Team**|**PTS**|**FG**|**FG%**|**3P**|**3P%**|**FT**|**FT%**|**OREB**|**TREB**|**AST**|**PF**|**STL**|**TO**|**BLK**|
|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|
|{vTeamName}|{vpts}|{vfgm}-{vfga}|{vfgp}%|{vtpm}-{vtpa}|{vtpp}%|{vftm}-{vfta}|{vftp}%|{voreb}|{vtreb}|{vast}|{vpf}|{vstl}|{vto}|{vblk}|
|{hTeamName}|{hpts}|{hfgm}-{hfga}|{hfgp}%|{htpm}-{htpa}|{htpp}%|{hftm}-{hfta}|{hftp}%|{horeb}|{htreb}|{hast}|{hpf}|{hstl}|{hto}|{hblk}|

|**Team**|**Biggest Lead**|**Longest Run**|**PTS: In Paint**|**PTS: Off TOs**|**PTS: Fastbreak**|
|:--|:--|:--|:--|:--|:--|
|{vTeamName}|{vlead}|{vrun}|{vpaint}|{vpto}|{vfb}|
|{hTeamName}|{hlead}|{hrun}|{hpaint}|{hpto}|{hfb}|
""".format(
            vTeamName = teamDict[vTeamBasicData["triCode"]][0],
            vpts = allStats["vTeam"]["totals"]["points"],
            vfgm = allStats["vTeam"]["totals"]["fgm"],
            vfga = allStats["vTeam"]["totals"]["fga"],
            vfgp = allStats["vTeam"]["totals"]["fgp"],
            vtpm = allStats["vTeam"]["totals"]["tpm"],
            vtpa = allStats["vTeam"]["totals"]["tpa"],
            vtpp = allStats["vTeam"]["totals"]["tpp"],
            vftm = allStats["vTeam"]["totals"]["ftm"],
            vfta = allStats["vTeam"]["totals"]["fta"],
            vftp = allStats["vTeam"]["totals"]["ftp"],
            voreb = allStats["vTeam"]["totals"]["offReb"],
            vtreb = allStats["vTeam"]["totals"]["totReb"],
            vast = allStats["vTeam"]["totals"]["assists"],
            vpf = allStats["vTeam"]["totals"]["pFouls"],
            vstl = allStats["vTeam"]["totals"]["steals"],
            vto = allStats["vTeam"]["totals"]["turnovers"],
            vblk = allStats["vTeam"]["totals"]["blocks"],
            hTeamName = teamDict[hTeamBasicData["triCode"]][0],
            hpts = allStats["hTeam"]["totals"]["points"],
            hfgm = allStats["hTeam"]["totals"]["fgm"],
            hfga = allStats["hTeam"]["totals"]["fga"],
            hfgp = allStats["hTeam"]["totals"]["fgp"],
            htpm = allStats["hTeam"]["totals"]["tpm"],
            htpa = allStats["hTeam"]["totals"]["tpa"],
            htpp = allStats["hTeam"]["totals"]["tpp"],
            hftm = allStats["hTeam"]["totals"]["ftm"],
            hfta = allStats["hTeam"]["totals"]["fta"],
            hftp = allStats["hTeam"]["totals"]["ftp"],
            horeb = allStats["hTeam"]["totals"]["offReb"],
            htreb = allStats["hTeam"]["totals"]["totReb"],
            hast = allStats["hTeam"]["totals"]["assists"],
            hpf = allStats["hTeam"]["totals"]["pFouls"],
            hstl = allStats["hTeam"]["totals"]["steals"],
            hto = allStats["hTeam"]["totals"]["turnovers"],
            hblk = allStats["hTeam"]["totals"]["blocks"],
            vlead = appendPlusMinus(allStats["vTeam"]["biggestLead"]),
            vrun = allStats["vTeam"]["longestRun"],
            vpaint = allStats["vTeam"]["pointsInPaint"],
            vpto = allStats["vTeam"]["pointsOffTurnovers"],
            vfb = allStats["vTeam"]["fastBreakPoints"],
            hlead = appendPlusMinus(allStats["hTeam"]["biggestLead"]),
            hrun = allStats["hTeam"]["longestRun"],
            hpaint = allStats["hTeam"]["pointsInPaint"],
            hpto = allStats["hTeam"]["pointsOffTurnovers"],
            hfb = allStats["hTeam"]["fastBreakPoints"]
)

body += """
||		
|:-:|		
|&nbsp;|		
|**TEAM LEADERS**|

|**Team**|**Points**|**Rebounds**|**Assists**|
|:--|:--|:--|:--|
|{vTeam}|**{vpts}** {vply1}|**{vreb}** {vply2}|**{vast}** {vply3}|
|{hTeam}|**{hpts}** {hply1}|**{hreb}** {hply2}|**{hast}** {hply3}|
""".format(
        vTeam = teamDict[vTeamBasicData["triCode"]][0],
        vpts = allStats["vTeam"]["leaders"]["points"]["value"],
        vply1 = findPlayerName(dataPlayersLeague, allStats["vTeam"]["leaders"]["points"]["players"][0]["personId"]),
        vreb = allStats["vTeam"]["leaders"]["rebounds"]["value"],
        vply2 = findPlayerName(dataPlayersLeague, allStats["vTeam"]["leaders"]["rebounds"]["players"][0]["personId"]),
        vast = allStats["vTeam"]["leaders"]["assists"]["value"],
        vply3 = findPlayerName(dataPlayersLeague, allStats["vTeam"]["leaders"]["assists"]["players"][0]["personId"]),
        hTeam = teamDict[hTeamBasicData["triCode"]][0],
        hpts = allStats["hTeam"]["leaders"]["points"]["value"],
        hply1 = findPlayerName(dataPlayersLeague, allStats["hTeam"]["leaders"]["points"]["players"][0]["personId"]),
        hreb = allStats["hTeam"]["leaders"]["rebounds"]["value"],
        hply2 = findPlayerName(dataPlayersLeague, allStats["hTeam"]["leaders"]["rebounds"]["players"][0]["personId"]),
        hast = allStats["hTeam"]["leaders"]["assists"]["value"],
        hply3 = findPlayerName(dataPlayersLeague, allStats["hTeam"]["leaders"]["assists"]["players"][0]["personId"])
)

body += """
||		
|:-:|		
|&nbsp;|		
|**PLAYER STATS**|

||||||||||||||||
|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|
**[](/{vTeamLogo}) {vTeamName}**|**MIN**|**FGM-A**|**3PM-A**|**FTM-A**|**ORB**|**DRB**|**REB**|**AST**|**STL**|**BLK**|**TO**|**PF**|**+/-**|**PTS**|
""".format(
        vTeamLogo = vTeamBasicData["triCode"],
        vTeamName = teamDict[vTeamBasicData["triCode"]][0].rsplit(None, 1)[-1].upper()
)

# players stats are filled here, only starters have "pos" property (away team)
for i in range(len(playerStats)):
    stats = playerStats[i]
    if stats["teamId"] == vTeamBasicData["teamId"] and stats["pos"] != "":
        body += "|{pname}^{pos}|{min}|{fgm}-{fga}|{tpm}-{tpa}|{ftm}-{fta}|{oreb}|{dreb}|{treb}|{ast}|{stl}|{blk}|{to}|{pf}|{pm}|{pts}|\n".format(
                        pname = findPlayerName(dataPlayersLeague, stats["personId"]),
                        pos = stats["pos"],
                        min = stats["min"],
                        fgm = stats["fgm"],
                        fga = stats["fga"],
                        tpm = stats["tpm"],
                        tpa = stats["tpa"],
                        ftm = stats["ftm"],
                        fta = stats["fta"],
                        oreb = stats["offReb"],
                        dreb = stats["defReb"],
                        treb = stats["totReb"],
                        ast = stats["assists"],
                        stl = stats["steals"],
                        blk = stats["blocks"],
                        to = stats["turnovers"],
                        pf = stats["pFouls"],
                        pm = appendPlusMinus(stats["plusMinus"]),
                        pts = stats["points"]
                )
    elif stats["teamId"] == vTeamBasicData["teamId"]:
        body += "|{pname}|{min}|{fgm}-{fga}|{tpm}-{tpa}|{ftm}-{fta}|{oreb}|{dreb}|{treb}|{ast}|{stl}|{blk}|{to}|{pf}|{pm}|{pts}|\n".format(
                        pname = findPlayerName(dataPlayersLeague, stats["personId"]),
                        min = stats["min"],
                        fgm = stats["fgm"],
                        fga = stats["fga"],
                        tpm = stats["tpm"],
                        tpa = stats["tpa"],
                        ftm = stats["ftm"],
                        fta = stats["fta"],
                        oreb = stats["offReb"],
                        dreb = stats["defReb"],
                        treb = stats["totReb"],
                        ast = stats["assists"],
                        stl = stats["steals"],
                        blk = stats["blocks"],
                        to = stats["turnovers"],
                        pf = stats["pFouls"],
                        pm = appendPlusMinus(stats["plusMinus"]),
                        pts = stats["points"]
                )
body += """**[](/{hTeamLogo}) {hTeamName}**|**MIN**|**FGM-A**|**3PM-A**|**FTM-A**|**ORB**|**DRB**|**REB**|**AST**|**STL**|**BLK**|**TO**|**PF**|**+/-**|**PTS**|
""".format(
        hTeamLogo = hTeamBasicData["triCode"],
        hTeamName = teamDict[hTeamBasicData["triCode"]][0].rsplit(None, 1)[-1].upper()
)
    # home team players
for i in range(len(playerStats)):
    stats = playerStats[i]
    if stats["teamId"] != vTeamBasicData["teamId"] and stats["pos"] != "":
        body += "|{pname}^{pos}|{min}|{fgm}-{fga}|{tpm}-{tpa}|{ftm}-{fta}|{oreb}|{dreb}|{treb}|{ast}|{stl}|{blk}|{to}|{pf}|{pm}|{pts}|\n".format(
                        pname = findPlayerName(dataPlayersLeague, stats["personId"]),
                        pos = stats["pos"],
                        min = stats["min"],
                        fgm = stats["fgm"],
                        fga = stats["fga"],
                        tpm = stats["tpm"],
                        tpa = stats["tpa"],
                        ftm = stats["ftm"],
                        fta = stats["fta"],
                        oreb = stats["offReb"],
                        dreb = stats["defReb"],
                        treb = stats["totReb"],
                        ast = stats["assists"],
                        stl = stats["steals"],
                        blk = stats["blocks"],
                        to = stats["turnovers"],
                        pf = stats["pFouls"],
                        pm = appendPlusMinus(stats["plusMinus"]),
                        pts = stats["points"]
                )
    elif playerStats[i]["teamId"] != vTeamBasicData["teamId"] and playerStats[i]["pos"] == "":
        body += "|{pname}|{min}|{fgm}-{fga}|{tpm}-{tpa}|{ftm}-{fta}|{oreb}|{dreb}|{treb}|{ast}|{stl}|{blk}|{to}|{pf}|{pm}|{pts}|\n".format(
                        pname = findPlayerName(dataPlayersLeague, stats["personId"]),
                        min = stats["min"],
                        fgm = stats["fgm"],
                        fga = stats["fga"],
                        tpm = stats["tpm"],
                        tpa = stats["tpa"],
                        ftm = stats["ftm"],
                        fta = stats["fta"],
                        oreb = stats["offReb"],
                        dreb = stats["defReb"],
                        treb = stats["totReb"],
                        ast = stats["assists"],
                        stl = stats["steals"],
                        blk = stats["blocks"],
                        to = stats["turnovers"],
                        pf = stats["pFouls"],
                        pm = appendPlusMinus(stats["plusMinus"]),
                        pts = stats["points"]
                )
# footer
body += """
||
|:-:|
|^[bot-script](https://github.com/f1uk3r/Some-Python-Scripts/blob/master/reddit-nba-bot/reddit-boxscore-bot.py) ^by ^/u/f1uk3r|  """

#print(body) #uncomment print statement to see body on console
print(title)
correctTitleQuestion = int(input("Is the title of thread correct (Choose 1 for yes): "))
if correctTitleQuestion == 1:
    response = reddit.subreddit('nbaspurs').submit(title, selftext=body, send_replies=False)
else:
    title = input("Please enter the title you want to give to the thread: ")
    response = reddit.subreddit('nbaspurs').submit(title, selftext=body, send_replies=False)