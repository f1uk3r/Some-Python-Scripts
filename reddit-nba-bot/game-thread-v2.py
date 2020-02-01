import praw
import requests
import traceback
import bs4
import re
import random
from apscheduler.schedulers.blocking import BlockingScheduler
import json
from datetime import date, timedelta, datetime
import config
import logging

sched = BlockingScheduler({'apscheduler.timezone': 'UTC'})
#logging.basicConfig()
#logging.getLogger('apscheduler').setLevel(logging.DEBUG)

# Team Dictionary helps to make urls for boxscore and for full-forms of abbrevation of teams
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
            "/r/washingtonwizards", "1610612764, ", "Wizards"],
    "ADL": ["Adelaide 36ers", "00", "adelaide-36ers",
            "/r/nba", "15019"],
    "SLA": ["Buenos Aires San Lorenzo", "00", "buenos-aires-san-lorenzo",
            "/r/nba", "12330"],
    "FRA": ["Franca Franca", "00", "franca-franca",
            "/r/nba", "12332"],
    "GUA": ["Guangzhou Long-Lions", "00", "guangzhou-long-lions",
            "/r/nba", "15018"],
    "MAC": ["Haifa Maccabi Haifa", "00", "haifa-maccabi-haifa",
            "/r/nba", "93"],
    "MEL": ["Melbourne United", "00", "melbourne-united",
            "/r/nba", "15016"],
    "NZB": ["New Zealand Breakers", "00", "new-zealand-breakers",
            "/r/nba", "15020"],
    "SDS": ["Shanghai Sharks", "00", "shanghai-sharks",
            "/r/nba", "12329"]
}

# getting a reddit instance by giving appropiate credentials
reddit = praw.Reddit(
    username=config.username,
    password=config.password,
    client_id=config.client_id,
    client_secret=config.client_secret,
    user_agent="script:rnba-game-thread-bot:v2.0 (by /u/f1uk3r)")


def requestApi(url):
    req = requests.get(url)
    return req.json()


def requestSoup(url):
    req = requests.get(url)
    soup = bs4.BeautifulSoup(req.text, 'html.parser')
    return soup

    
def appendPlusMinus(someStat):
    """
    someStat is any stat
    appendPlusMinus just appends sign in front of stat in question 
    and returns it
    """
    if someStat.isdigit():
        if int(someStat) > 0:
            return "+" + str(someStat)
        return str(someStat)
    else:
        return str(someStat)

#game thread fuctions starts from here
def initialGameThreadText(basicGameData, date, teamDict, dateTitle):
    """
    Variable basicGameData have live data
    Variable date is today's date
    Variable teamDict is the variable Dictionary at the top
    Function beforeGamePost setups the body of the thread before game starts
    and return body and title of the post
    """
    try:
        nbaUrlBoxscore = ("http://www.nba.com/games/" + date + "/"
                          + basicGameData["vTeam"]["triCode"]
                          + basicGameData["hTeam"]["triCode"] + "#/boxscore")
        nbaUrlPreview = ("http://www.nba.com/games/" + date + "/"
                         + basicGameData["vTeam"]["triCode"]
                         + basicGameData["hTeam"]["triCode"] + "#/preview")
        nbaUrlPlayByPlay = ("http://www.nba.com/games/" + date + "/"
                            + basicGameData["vTeam"]["triCode"]
                            + basicGameData["hTeam"]["triCode"] + "#/matchup")
        nbaUrlMatchup = ("http://www.nba.com/games/" + date + "/"
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

        if timeEasternMinute == 0:
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
    except:
        return "", ""


def boxScoreText(boxScoreData, bodyText, date, teamDict):
    """
    Variable boxScoreData have live data
    Variable bodyText have body when the post was originally created
    Variable date is today's date
    Variable teamDict is the variable Dictionary at the top
    Returns whole bodyText for editing
    """
    basicGameData = boxScoreData["basicGameData"]
    allStats = boxScoreData["stats"]
    vTeamBasicData = basicGameData["vTeam"]
    hTeamBasicData = basicGameData["hTeam"]
    nbaUrl = ("http://www.nba.com/games/" + date + "/"
              + vTeamBasicData["triCode"]
              + hTeamBasicData["triCode"] + "#/boxscore")
    yahooUrl = ("http://sports.yahoo.com/nba/"
                + teamDict[vTeamBasicData["triCode"]][2]
                + teamDict[hTeamBasicData["triCode"]][2]
                + date + teamDict[hTeamBasicData["triCode"]][1])
    playerStats = allStats["activePlayers"]
    body = bodyText + """
||		
|:-:|		
|[](/{vTeamLogo}) **{vTeamScore} -  {hTeamScore}** [](/{hTeamLogo})|
|**Box Scores: [NBA]({nbaurl}) & [Yahoo]({yahoourl})**|
""".format(
        vTeamLogo=vTeamBasicData["triCode"],
        vTeamScore=vTeamBasicData["score"],
        hTeamScore=hTeamBasicData["score"],
        hTeamLogo=hTeamBasicData["triCode"],
        nbaurl=nbaUrl,
        yahoourl=yahooUrl
    )

    body += """

||
|:-:|											
|&nbsp;|		
|**GAME SUMMARY**|
|**Location:** {arena}({attendance}), **Clock:** {clock}|
|**Officials:** {referee1}, {referee2} and {referee3}|

""".format(
        arena=basicGameData["arena"]["name"],
        attendance=basicGameData["attendance"],
        clock=basicGameData["clock"],
        referee1=basicGameData["officials"]["formatted"][0]["firstNameLastName"],
        referee2=basicGameData["officials"]["formatted"][1]["firstNameLastName"],
        referee3=basicGameData["officials"]["formatted"][2]["firstNameLastName"]
    )

    body += """|**Team**|**Q1**|**Q2**|**Q3**|**Q4**|**"""
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
        vTeamName=teamDict[vTeamBasicData["triCode"]][0],
        vpts=allStats["vTeam"]["totals"]["points"],
        vfgm=allStats["vTeam"]["totals"]["fgm"],
        vfga=allStats["vTeam"]["totals"]["fga"],
        vfgp=allStats["vTeam"]["totals"]["fgp"],
        vtpm=allStats["vTeam"]["totals"]["tpm"],
        vtpa=allStats["vTeam"]["totals"]["tpa"],
        vtpp=allStats["vTeam"]["totals"]["tpp"],
        vftm=allStats["vTeam"]["totals"]["ftm"],
        vfta=allStats["vTeam"]["totals"]["fta"],
        vftp=allStats["vTeam"]["totals"]["ftp"],
        voreb=allStats["vTeam"]["totals"]["offReb"],
        vtreb=allStats["vTeam"]["totals"]["totReb"],
        vast=allStats["vTeam"]["totals"]["assists"],
        vpf=allStats["vTeam"]["totals"]["pFouls"],
        vstl=allStats["vTeam"]["totals"]["steals"],
        vto=allStats["vTeam"]["totals"]["turnovers"],
        vblk=allStats["vTeam"]["totals"]["blocks"],
        hTeamName=teamDict[hTeamBasicData["triCode"]][0],
        hpts=allStats["hTeam"]["totals"]["points"],
        hfgm=allStats["hTeam"]["totals"]["fgm"],
        hfga=allStats["hTeam"]["totals"]["fga"],
        hfgp=allStats["hTeam"]["totals"]["fgp"],
        htpm=allStats["hTeam"]["totals"]["tpm"],
        htpa=allStats["hTeam"]["totals"]["tpa"],
        htpp=allStats["hTeam"]["totals"]["tpp"],
        hftm=allStats["hTeam"]["totals"]["ftm"],
        hfta=allStats["hTeam"]["totals"]["fta"],
        hftp=allStats["hTeam"]["totals"]["ftp"],
        horeb=allStats["hTeam"]["totals"]["offReb"],
        htreb=allStats["hTeam"]["totals"]["totReb"],
        hast=allStats["hTeam"]["totals"]["assists"],
        hpf=allStats["hTeam"]["totals"]["pFouls"],
        hstl=allStats["hTeam"]["totals"]["steals"],
        hto=allStats["hTeam"]["totals"]["turnovers"],
        hblk=allStats["hTeam"]["totals"]["blocks"],
        vlead=appendPlusMinus(allStats["vTeam"]["biggestLead"]),
        vrun=allStats["vTeam"]["longestRun"],
        vpaint=allStats["vTeam"]["pointsInPaint"],
        vpto=allStats["vTeam"]["pointsOffTurnovers"],
        vfb=allStats["vTeam"]["fastBreakPoints"],
        hlead=appendPlusMinus(allStats["hTeam"]["biggestLead"]),
        hrun=allStats["hTeam"]["longestRun"],
        hpaint=allStats["hTeam"]["pointsInPaint"],
        hpto=allStats["hTeam"]["pointsOffTurnovers"],
        hfb=allStats["hTeam"]["fastBreakPoints"]
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
        vTeam=teamDict[vTeamBasicData["triCode"]][0],
        vpts=allStats["vTeam"]["leaders"]["points"]["value"],
        vply1=allStats["vTeam"]["leaders"]["points"]["players"][0]["firstName"] + " " +
              allStats["vTeam"]["leaders"]["points"]["players"][0]["lastName"],
        vreb=allStats["vTeam"]["leaders"]["rebounds"]["value"],
        vply2=allStats["vTeam"]["leaders"]["rebounds"]["players"][0]["firstName"] + " " +
              allStats["vTeam"]["leaders"]["rebounds"]["players"][0]["lastName"],
        vast=allStats["vTeam"]["leaders"]["assists"]["value"],
        vply3=allStats["vTeam"]["leaders"]["assists"]["players"][0]["firstName"] + " " +
              allStats["vTeam"]["leaders"]["assists"]["players"][0]["lastName"],
        hTeam=teamDict[hTeamBasicData["triCode"]][0],
        hpts=allStats["hTeam"]["leaders"]["points"]["value"],
        hply1=allStats["hTeam"]["leaders"]["points"]["players"][0]["firstName"] + " " +
              allStats["hTeam"]["leaders"]["points"]["players"][0]["lastName"],
        hreb=allStats["hTeam"]["leaders"]["rebounds"]["value"],
        hply2=allStats["hTeam"]["leaders"]["rebounds"]["players"][0]["firstName"] + " " +
              allStats["hTeam"]["leaders"]["rebounds"]["players"][0]["lastName"],
        hast=allStats["hTeam"]["leaders"]["assists"]["value"],
        hply3=allStats["hTeam"]["leaders"]["assists"]["players"][0]["firstName"] + " " +
              allStats["hTeam"]["leaders"]["assists"]["players"][0]["lastName"]
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
        vTeamLogo=vTeamBasicData["triCode"],
        vTeamName=teamDict[vTeamBasicData["triCode"]][0].rsplit(None, 1)[-1].upper()
    )

    # players stats are filled here, only starters have "pos" property (away team)
    for i in range(len(playerStats)):
        stats = playerStats[i]
        if stats["teamId"] == vTeamBasicData["teamId"] and stats["pos"] != "":
            body += "|{pname}^{pos}|{min}|{fgm}-{fga}|{tpm}-{tpa}|{ftm}-{fta}|{oreb}|{dreb}|{treb}|{ast}|{stl}|{blk}|{to}|{pf}|{pm}|{pts}|\n".format(
                pname=stats["firstName"] + " " + stats["lastName"],
                pos=stats["pos"],
                min=stats["min"],
                fgm=stats["fgm"],
                fga=stats["fga"],
                tpm=stats["tpm"],
                tpa=stats["tpa"],
                ftm=stats["ftm"],
                fta=stats["fta"],
                oreb=stats["offReb"],
                dreb=stats["defReb"],
                treb=stats["totReb"],
                ast=stats["assists"],
                stl=stats["steals"],
                blk=stats["blocks"],
                to=stats["turnovers"],
                pf=stats["pFouls"],
                pm=appendPlusMinus(stats["plusMinus"]),
                pts=stats["points"]
            )
        elif stats["teamId"] == vTeamBasicData["teamId"]:
            body += "|{pname}|{min}|{fgm}-{fga}|{tpm}-{tpa}|{ftm}-{fta}|{oreb}|{dreb}|{treb}|{ast}|{stl}|{blk}|{to}|{pf}|{pm}|{pts}|\n".format(
                pname=stats["firstName"] + " " + stats["lastName"],
                min=stats["min"],
                fgm=stats["fgm"],
                fga=stats["fga"],
                tpm=stats["tpm"],
                tpa=stats["tpa"],
                ftm=stats["ftm"],
                fta=stats["fta"],
                oreb=stats["offReb"],
                dreb=stats["defReb"],
                treb=stats["totReb"],
                ast=stats["assists"],
                stl=stats["steals"],
                blk=stats["blocks"],
                to=stats["turnovers"],
                pf=stats["pFouls"],
                pm=appendPlusMinus(stats["plusMinus"]),
                pts=stats["points"]
            )
    body += """**[](/{hTeamLogo}) {hTeamName}**|**MIN**|**FGM-A**|**3PM-A**|**FTM-A**|**ORB**|**DRB**|**REB**|**AST**|**STL**|**BLK**|**TO**|**PF**|**+/-**|**PTS**|
""".format(
        hTeamLogo=hTeamBasicData["triCode"],
        hTeamName=teamDict[hTeamBasicData["triCode"]][0].rsplit(None, 1)[-1].upper()
    )
    # home team players
    for i in range(len(playerStats)):
        stats = playerStats[i]
        if stats["teamId"] != vTeamBasicData["teamId"] and stats["pos"] != "":
            body += "|{pname}^{pos}|{min}|{fgm}-{fga}|{tpm}-{tpa}|{ftm}-{fta}|{oreb}|{dreb}|{treb}|{ast}|{stl}|{blk}|{to}|{pf}|{pm}|{pts}|\n".format(
                pname=stats["firstName"] + " " + stats["lastName"],
                pos=stats["pos"],
                min=stats["min"],
                fgm=stats["fgm"],
                fga=stats["fga"],
                tpm=stats["tpm"],
                tpa=stats["tpa"],
                ftm=stats["ftm"],
                fta=stats["fta"],
                oreb=stats["offReb"],
                dreb=stats["defReb"],
                treb=stats["totReb"],
                ast=stats["assists"],
                stl=stats["steals"],
                blk=stats["blocks"],
                to=stats["turnovers"],
                pf=stats["pFouls"],
                pm=appendPlusMinus(stats["plusMinus"]),
                pts=stats["points"]
            )
        elif playerStats[i]["teamId"] != vTeamBasicData["teamId"] and playerStats[i]["pos"] == "":
            body += "|{pname}|{min}|{fgm}-{fga}|{tpm}-{tpa}|{ftm}-{fta}|{oreb}|{dreb}|{treb}|{ast}|{stl}|{blk}|{to}|{pf}|{pm}|{pts}|\n".format(
                pname=stats["firstName"] + " " + stats["lastName"],
                min=stats["min"],
                fgm=stats["fgm"],
                fga=stats["fga"],
                tpm=stats["tpm"],
                tpa=stats["tpa"],
                ftm=stats["ftm"],
                fta=stats["fta"],
                oreb=stats["offReb"],
                dreb=stats["defReb"],
                treb=stats["totReb"],
                ast=stats["assists"],
                stl=stats["steals"],
                blk=stats["blocks"],
                to=stats["turnovers"],
                pf=stats["pFouls"],
                pm=appendPlusMinus(stats["plusMinus"]),
                pts=stats["points"]
            )
    # footer
    body += """

||
|:-:|
|^[bot-script](https://github.com/f1uk3r/Some-Python-Scripts/blob/master/reddit-nba-bot/reddit-boxscore-bot.py) ^by ^/u/f1uk3r|  """
    return body


def createGameThread(dateToday, gameId):
    dateTitle = datetime.utcnow().strftime("%B %d, %Y")
    dataBoxScore = requestApi("http://data.nba.net/prod/v1/" + dateToday
                              + "/" + gameId + "_boxscore.json")
    basicGameData = dataBoxScore["basicGameData"]
    bodyPost, title = initialGameThreadText(basicGameData, dateToday, teamDict, dateTitle)
    if bodyPost == "" or title == "":
        sched.add_job(createGameThread, args=[dateToday, gameId], run_date=datetime.utcnow() + timedelta(minutes=1))
    else:
        response = reddit.subreddit('nba').submit(title, selftext=bodyPost, send_replies=False)
        sched.add_job(updateGameThread, 'date', run_date=datetime.utcnow() + timedelta(minutes=1), max_instances=15,
                      args=[gameId, dateToday, bodyPost], kwargs={'response': response})
        print(gameId + " thread created")


def updateGameThread(gameId, dateToday, bodyPost, response=None):
    dataBoxScore = requestApi("http://data.nba.net/prod/v1/" + dateToday + "/" + gameId + "_boxscore.json")
    try:
        response.edit(boxScoreText(dataBoxScore, bodyPost, dateToday, teamDict))
    except Exception:
        traceback.print_exc()
    if checkIfGameIsFinished(gameId, dateToday):
        print(gameId + " game finished")
    else:
        sched.add_job(updateGameThread, 'date', run_date=datetime.utcnow() + timedelta(minutes=1), max_instances=15,
                      args=[gameId, dateToday, bodyPost], kwargs={'response': response})
        print(gameId + " thread edited")


def checkIfGameIsFinished(gameId, dateToday):
    dataBoxScore = requestApi("http://data.nba.net/prod/v1/" + dateToday + "/" + gameId + "_boxscore.json")
    basicGameData = dataBoxScore["basicGameData"]
    if ((basicGameData["clock"] == "0.0" or basicGameData["clock"] == "")
            and basicGameData["period"]["current"] >= 4
            and (basicGameData["vTeam"]["score"] != basicGameData["hTeam"]["score"])):
        return True
    else:
        return False


def processGameThreads():
    # finding date of game
    now = datetime.utcnow()
    dateToday = now.strftime("%Y%m%d")  # Check the date before using script
    # print(date)

    # getting today's game
    data = requestApi("http://data.nba.net/prod/v1/" + dateToday + "/scoreboard.json")
    games = data["games"]

    for game in games:
        dataBoxScore = requestApi(
            "http://data.nba.net/prod/v1/" + dateToday + "/" + str(game["gameId"]) + "_boxscore.json")
        basicGameData = dataBoxScore["basicGameData"]
        gameStartTime = datetime.strptime(basicGameData["startTimeUTC"][:19],
                                          '%Y-%m-%dT%H:%M:%S')
        sched.add_job(createGameThread, args=[dateToday, game["gameId"]], run_date=gameStartTime - timedelta(hours=1))
        print(basicGameData["gameUrlCode"] + " game scheduled")

    now = datetime.utcnow()
    tomorrow = now + timedelta(days=1)
    dateTomorrow = tomorrow.strftime("%Y%m%d")
    dataTomorrow = requestApi(f"http://data.nba.net/prod/v1/{dateTomorrow}/scoreboard.json")
    if dataTomorrow["numGames"] != 0:
        nextDay = datetime.strptime(dataTomorrow["games"][0]["startTimeUTC"][:19],'%Y-%m-%dT%H:%M:%S') - timedelta(hours=2)
    else:
        nextDay = datetime.utcnow() + timedelta(days=1)
    sched.add_job(processGameThreads, run_date=nextDay, max_instances=15)
    print("processGameThread() is scheduled to run tomorrow")


# Next Day Thread Stuff
def postNextDayThread(gamesDataList, dateTitle, teamDict):
    """
    Variable basicGameData have live data
    Variable dateTitle is today's dateTitle
    Variable teamDict is the variable Dictionary at the top
    Function beforeGamePost setups the body of the thread before game starts
    and return body and title of the post
    """
    postTextBody = """Here is a place to have in depth, x's and o's, discussions on yesterday's games. Post-game discussions are linked in the table, keep your memes and reactions there.

Please keep your discussion of a particular game in the respective comment thread. **All direct replies to this post will be removed.**


|Away|Home|Score|GT|PGT|
|:--|:--|:-:|:-:|:-:|
"""
    pgtLink = "No PGT Found"
    gtLink = "No GT Found"
    for each in gamesDataList:
        for submission in (reddit.subreddit('nba').search("game thread "
                                                          + teamDict[each["vTeam"]["triCode"]][0] + " "
                                                          + teamDict[each["hTeam"]["triCode"]][0] + " " + dateTitle,
                                                          sort="new", time_filter="day")):
            if ("Game Threads Index" not in submission.title
                    and "[post game thread]" not in submission.title
                    and f"GAME THREAD: {teamDict[each['vTeam']['triCode']][0]}" 
                    in submission.title and teamDict[each['hTeam']['triCode']][0] 
                    in submission.title):
                gtLink = "[Link](" + str(submission.url) + ")"

        for submission in (reddit.subreddit('nba').search("post game thread "
                                                          + teamDict[each["vTeam"]["triCode"]][0] + " "
                                                          + teamDict[each["hTeam"]["triCode"]][0], sort="new",
                                                          time_filter="day")):
            if ("Game Threads Index" not in submission.title
                    and "Ranking today's game" not in submission.title
                    and teamDict[each["vTeam"]["triCode"]][0] in submission.title
                    and teamDict[each["hTeam"]["triCode"]][0] in submission.title):
                pgtLink = "[Link](" + str(submission.url) + ")"

        postTextBody += """|[](/{vTeamLogo}) {vTeamName} |[](/{hTeamLogo}) {hTeamName} | {vTeamScore} - {hTeamScore} | ({gtLinkUrl}) | ({pgtLinkUrl}) |
""".format(
            vTeamLogo=each["vTeam"]["triCode"],
            vTeamName=teamDict[each["vTeam"]["triCode"]][0],
            hTeamLogo=each["hTeam"]["triCode"],
            hTeamName=teamDict[each["hTeam"]["triCode"]][0],
            vTeamScore=each["vTeam"]["score"],
            hTeamScore=each["hTeam"]["score"],
            gtLinkUrl=str(gtLink),
            pgtLinkUrl=str(pgtLink)
        )

    title = ("[SERIOUS NEXT DAY THREAD] Post-Game Discussion (" + dateTitle + ")")
    response = reddit.subreddit('nba').submit(title, selftext=postTextBody, send_replies=False)
    #print(response)
    #response.mod.distinguish(how="yes")
    #response.mod.sticky()
    return response


def commentNextDayThread(boxScoreData, date, teamDict, response):
    """
    Variable boxScoreData have live data
    Variable date is today's date
    Variable teamDict is the variable Dictionary at the top
    Returns whole bodyText for commenting
    """
    basicGameData = boxScoreData["basicGameData"]
    allStats = boxScoreData["stats"]
    vTeamBasicData = basicGameData["vTeam"]
    hTeamBasicData = basicGameData["hTeam"]
    nbaUrl = ("http://www.nba.com/games/" + date + "/"
              + basicGameData["vTeam"]["triCode"]
              + basicGameData["hTeam"]["triCode"] + "#/boxscore")
    yahooUrl = ("http://sports.yahoo.com/nba/"
                + teamDict[basicGameData["vTeam"]["triCode"]][2]
                + teamDict[basicGameData["hTeam"]["triCode"]][2]
                + date + teamDict[basicGameData["hTeam"]["triCode"]][1])
    body = """

{vTeamName} @ {hTeamName}

[](/{vTeamLogo}) **{vTeamScore} -  {hTeamScore}** [](/{hTeamLogo})

**Box Scores: [NBA]({nbaurl}) & [Yahoo]({yahoourl})**

""".format(
        vTeamName=teamDict[vTeamBasicData["triCode"]][-1],
        hTeamName=teamDict[hTeamBasicData["triCode"]][-1],
        vTeamLogo=vTeamBasicData["triCode"],
        vTeamScore=vTeamBasicData["score"],
        hTeamScore=hTeamBasicData["score"],
        hTeamLogo=hTeamBasicData["triCode"],
        nbaurl=nbaUrl,
        yahoourl=yahooUrl
    )

    body += """|**Team**|**Q1**|**Q2**|**Q3**|**Q4**|**"""
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
""".format(
        vTeamName=teamDict[vTeamBasicData["triCode"]][0],
        vpts=allStats["vTeam"]["totals"]["points"],
        vfgm=allStats["vTeam"]["totals"]["fgm"],
        vfga=allStats["vTeam"]["totals"]["fga"],
        vfgp=allStats["vTeam"]["totals"]["fgp"],
        vtpm=allStats["vTeam"]["totals"]["tpm"],
        vtpa=allStats["vTeam"]["totals"]["tpa"],
        vtpp=allStats["vTeam"]["totals"]["tpp"],
        vftm=allStats["vTeam"]["totals"]["ftm"],
        vfta=allStats["vTeam"]["totals"]["fta"],
        vftp=allStats["vTeam"]["totals"]["ftp"],
        voreb=allStats["vTeam"]["totals"]["offReb"],
        vtreb=allStats["vTeam"]["totals"]["totReb"],
        vast=allStats["vTeam"]["totals"]["assists"],
        vpf=allStats["vTeam"]["totals"]["pFouls"],
        vstl=allStats["vTeam"]["totals"]["steals"],
        vto=allStats["vTeam"]["totals"]["turnovers"],
        vblk=allStats["vTeam"]["totals"]["blocks"],
        hTeamName=teamDict[hTeamBasicData["triCode"]][0],
        hpts=allStats["hTeam"]["totals"]["points"],
        hfgm=allStats["hTeam"]["totals"]["fgm"],
        hfga=allStats["hTeam"]["totals"]["fga"],
        hfgp=allStats["hTeam"]["totals"]["fgp"],
        htpm=allStats["hTeam"]["totals"]["tpm"],
        htpa=allStats["hTeam"]["totals"]["tpa"],
        htpp=allStats["hTeam"]["totals"]["tpp"],
        hftm=allStats["hTeam"]["totals"]["ftm"],
        hfta=allStats["hTeam"]["totals"]["fta"],
        hftp=allStats["hTeam"]["totals"]["ftp"],
        horeb=allStats["hTeam"]["totals"]["offReb"],
        htreb=allStats["hTeam"]["totals"]["totReb"],
        hast=allStats["hTeam"]["totals"]["assists"],
        hpf=allStats["hTeam"]["totals"]["pFouls"],
        hstl=allStats["hTeam"]["totals"]["steals"],
        hto=allStats["hTeam"]["totals"]["turnovers"],
        hblk=allStats["hTeam"]["totals"]["blocks"]
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
        vTeam=teamDict[vTeamBasicData["triCode"]][0],
        vpts=allStats["vTeam"]["leaders"]["points"]["value"],
        vply1=allStats["vTeam"]["leaders"]["points"]["players"][0]["firstName"] + " " +
              allStats["vTeam"]["leaders"]["points"]["players"][0]["lastName"],
        vreb=allStats["vTeam"]["leaders"]["rebounds"]["value"],
        vply2=allStats["vTeam"]["leaders"]["rebounds"]["players"][0]["firstName"] + " " +
              allStats["vTeam"]["leaders"]["rebounds"]["players"][0]["lastName"],
        vast=allStats["vTeam"]["leaders"]["assists"]["value"],
        vply3=allStats["vTeam"]["leaders"]["assists"]["players"][0]["firstName"] + " " +
              allStats["vTeam"]["leaders"]["assists"]["players"][0]["lastName"],
        hTeam=teamDict[hTeamBasicData["triCode"]][0],
        hpts=allStats["hTeam"]["leaders"]["points"]["value"],
        hply1=allStats["hTeam"]["leaders"]["points"]["players"][0]["firstName"] + " " +
              allStats["hTeam"]["leaders"]["points"]["players"][0]["lastName"],
        hreb=allStats["hTeam"]["leaders"]["rebounds"]["value"],
        hply2=allStats["hTeam"]["leaders"]["rebounds"]["players"][0]["firstName"] + " " +
              allStats["hTeam"]["leaders"]["rebounds"]["players"][0]["lastName"],
        hast=allStats["hTeam"]["leaders"]["assists"]["value"],
        hply3=allStats["hTeam"]["leaders"]["assists"]["players"][0]["firstName"] + " " +
              allStats["hTeam"]["leaders"]["assists"]["players"][0]["lastName"]
    )
    response.reply(body).disable_inbox_replies()


def processNextDayThread():
    # finding date of game
    print("inside the function")
    now = datetime.utcnow() - timedelta(1)
    dateToday = now.strftime("%Y%m%d")  # Check the date before using script
    dateTitle = now.strftime("%B %d, %Y")
    # print(date)

    # getting today's game
    data = requestApi("http://data.nba.net/prod/v1/" + dateToday + "/scoreboard.json")
    games = data["games"]
    # Posting thread
    response = postNextDayThread(games, dateTitle, teamDict)
    print("thread have been posted")
    # Replying comments
    for i in range(len(games)):
        dataBoxScore = requestApi("http://data.nba.net/prod/v1/" + dateToday
                                  + "/" + str(games[i]["gameId"])
                                  + "_boxscore.json")
        commentNextDayThread(dataBoxScore, dateToday, teamDict, response)
        print("commented one game")
    print("thread is ready")


def rotateStickyThread():
    for sticky in reddit.subreddit('nba').search("We'll repost the best submissions across our", sort="new",
                                                 time_filter="month"):
        if not sticky.stickied:
            sticky.mod.sticky()
    print("thread rotated")


#get game threads and post game threads
def get_reddit_threads(games, redditThreadList):
    """
    Variable games have games data from today's API
    Variable redditThreadList have game threads and post game threads links against each game
    return gt's and pgt's after searching in r/nba
    """
    for submission in (reddit.subreddit('nba').search("game thread", sort="new", time_filter="day")):
        for i in range(len(games)):
            if redditThreadList[i]["gameThread"] == "":
                    if f"GAME THREAD: {teamDict[games[i]['vTeam']['triCode']][0]}" in submission.title and teamDict[games[i]['hTeam']['triCode']][0] in submission.title:
                        redditThreadList[i]["gameThread"] = submission.url
    for submission in (reddit.subreddit('nba').search("post game thread", sort="new", time_filter="day")):
        for i in range(len(games)):
            if redditThreadList[i]["postGameThread"] == "" and not games[i]["isGameActivated"]:
                if ("Game Threads Index" not in submission.title and "Ranking today's game" not in submission.title and teamDict[games[i]["vTeam"]["triCode"]][0] in submission.title and teamDict[games[i]["hTeam"]["triCode"]][0] in submission.title):
                    redditThreadList[i]["postGameThread"] = submission.url
    return redditThreadList


# sidebar bot start here
def get_game_thread_bar(top_submission_markup, standing_markup, schedule_markup, redditThreadList):
    """
    Variables top_submission_markup, standing_markup, schedule_markup are self explainatory
    Variable redditThreadList have game threads and post game threads links against each game
    Returns game thread bar markup and also runs update sidebar function
    """
    game_thread_bar_markup = ""
    if 13 - datetime.utcnow().hour > 0:
        now = datetime.utcnow() - timedelta(1)
        dateToday = now.strftime("%Y%m%d")
    else:
        now = datetime.utcnow()
        dateToday = now.strftime("%Y%m%d")
    today_game_full = requestApi("http://data.nba.net/prod/v2/" + dateToday + "/scoreboard.json")
    if today_game_full["numGames"] != 0:
        games = today_game_full["games"]
    else:
        games = []
    for i in range(len(games)):
        if games[i]["isGameActivated"] == True:
            gameStatus = f"{games[i]['clock']} {games[i]['period']['current']}Q"
            gameLink = redditThreadList[i]["gameThread"]
        else:
            gameStartTime = datetime.strptime(games[i]["startTimeUTC"][:19],'%Y-%m-%dT%H:%M:%S')
            if datetime.utcnow() < gameStartTime:
                gameStatus = games[i]['startTimeEastern']
                gameLink = redditThreadList[i]["gameThread"]
            else:
                if games[i]["period"]["current"] == 5:
                    gameStatus = "FINAL-OT"
                elif games[i]["period"]["current"] > 5:
                    numOT = games[i]['period']['current']-4
                    gameStatus = f'FINAL-{numOT} OT'
                else:
                    gameStatus = "FINAL"
                gameLink = redditThreadList[i]["postGameThread"]
        if gameLink != '':
            game_thread_bar_markup += f'> * **{games[i]["vTeam"]["triCode"]}** {games[i]["vTeam"]["score"]} **{games[i]["hTeam"]["triCode"]}** {games[i]["hTeam"]["score"]} [{gameStatus}]({gameLink})\n'
        else:
            game_thread_bar_markup += f'> * **{games[i]["vTeam"]["triCode"]}** {games[i]["vTeam"]["score"]} **{games[i]["hTeam"]["triCode"]}** {games[i]["hTeam"]["score"]} {gameStatus}\n'
    print(f"exiting game thread bar block {datetime.now()}")
    update_sidebar(game_thread_bar_markup, top_submission_markup, standing_markup, schedule_markup)
    return game_thread_bar_markup

def get_top_team_posts():
    """
    Returns top team submissions markup
    """
    topSubPosts = []
    for submission in reddit.subreddit('lakers+torontoraptors+bostonceltics').hot(limit=3):
        topSubPosts.append(submission)

    for submission in reddit.subreddit('sixers+rockets+chicagobulls+NYKnicks+GoNets').hot(limit=5):
        topSubPosts.append(submission)

    for submission in reddit.subreddit('MkeBucks+Mavericks+AtlantaHawks+Thunder+NBASpurs+ripcity+timberwolves').hot(limit=5):
        topSubPosts.append(submission)

    for submission in reddit.subreddit('washingtonwizards+denvernuggets+suns+UtahJazz+kings+LAClippers+DetroitPistons').hot(limit=5):
        topSubPosts.append(submission)

    for submission in reddit.subreddit('OrlandoMagic+pacers+clevelandcavs+CharlotteHornets+heat+memphisgrizzlies').hot(limit=5):
        topSubPosts.append(submission)

    sidebarTeamPosts = random.sample(population=topSubPosts, k=5)
    top_submission_markup = f"""|Top Team Subreddit Posts|\n|:---|"""
    for i in range(len(sidebarTeamPosts)):
        top_submission_markup += f"\n|{i+1} [{sidebarTeamPosts[i].title}](https://np.reddit.com{sidebarTeamPosts[i].permalink.lower()})|"
    top_submission_markup += f"\n\n"
    print(f"exiting top team submission block {datetime.now()}")
    return top_submission_markup

def get_conference_standings():
    """
    Returns conference standing markup
    """
    standing_markup = f"""\n\n\n|WEST|||EAST|||
|:---:|:---:|:---:|:---:|:---:|:---:|
|**TEAM**|*W/L*|*GB*|**TEAM**|*W/L*|*GB*|\n"""
    data_standing = requestApi("http://data.nba.net/prod/v1/current/standings_conference.json")
    east_standing = data_standing["league"]["standard"]["conference"]["east"]
    west_standing = data_standing["league"]["standard"]["conference"]["west"]

    for i in range(8):
        standing_markup += f'|{i+1} [](/{west_standing[i]["teamSitesOnly"]["teamTricode"]})| {west_standing[i]["win"]}-{west_standing[i]["loss"]} | {west_standing[i]["gamesBehind"]} |{i+1} [](/{east_standing[i]["teamSitesOnly"]["teamTricode"]})| {east_standing[i]["win"]}-{east_standing[i]["loss"]} | {east_standing[i]["gamesBehind"]} |\n'
    for i in range(8, len(east_standing)):
        standing_markup += f'| [](/{west_standing[i]["teamSitesOnly"]["teamTricode"]})| {west_standing[i]["win"]}-{west_standing[i]["loss"]} | {west_standing[i]["gamesBehind"]} | [](/{east_standing[i]["teamSitesOnly"]["teamTricode"]})| {east_standing[i]["win"]}-{east_standing[i]["loss"]} | {east_standing[i]["gamesBehind"]} |\n'
    print(f"exiting conference standing block {datetime.now()}")
    return standing_markup

def get_schedule():
    """
    Returns schedule markup
    """
    schedule_markup = f"""|Date|Away|Home|Time (ET)|Nat TV|
|:---|:---|:---|:---|:---|\n"""
    for i in range(4):
        schedule_date =  datetime.utcnow() + timedelta(i)
        dateToday = schedule_date.strftime("%Y%m%d")
        dateTitle = schedule_date.strftime("%b. %d")
        schedule_full = requestApi("http://data.nba.net/prod/v2/" + dateToday + "/scoreboard.json")
        for j in range(len(schedule_full["games"])):
            if j != 0:
                dateTitle = ""

            if schedule_full['games'][j]['watch']['broadcast']['broadcasters']['national'] != []:
                schedule_markup += f"|{dateTitle}|[](/{schedule_full['games'][j]['vTeam']['triCode']})|[](/{schedule_full['games'][j]['hTeam']['triCode']})|{schedule_full['games'][j]['startTimeEastern'][:-3]}|[](/{schedule_full['games'][j]['watch']['broadcast']['broadcasters']['national'][0]['shortName']})\n"
            elif schedule_full['games'][j]['watch']['broadcast']['broadcasters']['vTeam'] != []:
                schedule_markup += f"|{dateTitle}|[](/{schedule_full['games'][j]['vTeam']['triCode']})|[](/{schedule_full['games'][j]['hTeam']['triCode']})|{schedule_full['games'][j]['startTimeEastern'][:-3]}|[](/{schedule_full['games'][j]['watch']['broadcast']['broadcasters']['vTeam'][0]['shortName']})\n"
            else:
                schedule_markup += f"|{dateTitle}|[](/{schedule_full['games'][j]['vTeam']['triCode']})|[](/{schedule_full['games'][j]['hTeam']['triCode']})|{schedule_full['games'][j]['startTimeEastern'][:-3]}|[]()\n"
    print(f"exiting schedule block {datetime.now()}")
    return schedule_markup

def update_sidebar(game_thread_bar_markup, top_submission_markup, standing_markup, schedule_markup):
    """
    Reads sidebar content from wiki and replaces placeholders with markup blocks
    updates sidebar, returns nothing
    """
    sidebar_retrieved = reddit.subreddit('nba').wiki['edit_sidebar'].content_md
    sidebar_retrieved = re.sub(r'//blank table|//Sidebar image caption|//Standings blank table|//\|\|\|\|\||//\|:---:\|:---:\|:---:\|:---:\|:---:\|:---:\|:---:\|', '', sidebar_retrieved)
    sidebar_retrieved = re.sub(r'//[*][*]PLAYOFFS[*][*]|//----|//[$]playoffs', '', sidebar_retrieved)
    sidebar_retrieved = re.sub(r'[$]game_thread_bar', game_thread_bar_markup, sidebar_retrieved)
    sidebar_retrieved = re.sub(r'[$]team_subreddits', top_submission_markup, sidebar_retrieved)
    sidebar_retrieved = re.sub(r'//[$]standings', standing_markup, sidebar_retrieved)
    sidebar_retrieved = re.sub(r'[$]schedule', schedule_markup, sidebar_retrieved)
    reddit.subreddit("nba").mod.update(description=sidebar_retrieved)
    print(f"sidebar updated {datetime.now()}")


def games_inactive_update_sidebar_first_run(games, redditThreadList, endTime, startTimeTomorrow):
    """
    Variables top_submission_markup, standing_markup, schedule_markup are self explainatory
    Variable redditThreadList have game threads and post game threads links against each game
    variable endTime have the endtime for today's last game
    variable startTimeTomorrow has starting time of tomorrow's first game
    Updates sidebar and schedule job to update sidebar every 2 hours when games are inactive
    """
    redditThreadList = get_reddit_threads(games, redditThreadList)
    top_submission_markup = get_top_team_posts()
    standing_markup = get_conference_standings()
    schedule_markup = get_schedule()
    game_thread_bar_markup = get_game_thread_bar(top_submission_markup, standing_markup, schedule_markup, redditThreadList)
    sched.add_job(game_inactive_update_sidebar_in_interval, 'interval', hours=2, max_instances=15, start_date=endTime, end_date=startTimeTomorrow, args=[redditThreadList, game_thread_bar_markup])

def game_inactive_update_sidebar_in_interval(redditThreadList, game_thread_bar_markup):
    """
    Variable redditThreadList have game threads and post game threads links against each game
    Variables game_thread_vbar is self explainatory
    Updates sidebar when games are inactive
    """
    top_submission_markup = get_top_team_posts()
    standing_markup = get_conference_standings()
    schedule_markup = get_schedule()
    update_sidebar(game_thread_bar_markup, top_submission_markup, standing_markup, schedule_markup)


def update_game_thread_bar(games, redditThreadList, top_submission_markup, standing_markup, schedule_markup):
    """
    Updates sidebar when games are active in interval of 2 minutes
    """
    redditThreadList = get_reddit_threads(games, redditThreadList)
    get_game_thread_bar(top_submission_markup, standing_markup, schedule_markup, redditThreadList)


def process_sidebar():
    top_submission_markup = get_top_team_posts()
    standing_markup = get_conference_standings()
    schedule_markup = get_schedule()
    now = datetime.utcnow()
    dateToday = now.strftime("%Y%m%d")
    tomorrow = now + timedelta(days=1)
    dateTomorrow = tomorrow.strftime("%Y%m%d")
    data = requestApi(f"http://data.nba.net/prod/v1/{dateToday}/scoreboard.json")
    dataTomorrow = requestApi(f"http://data.nba.net/prod/v1/{dateTomorrow}/scoreboard.json")
    if data["numGames"] != 0:
        games = data["games"]
    else:
        games = []
    redditThreadList = []
    for game in games:
        redditThreadList.append({"id": game["gameId"], "gameThread": "", "postGameThread": ""})
    if data["numGames"] != 0:
        startTime = datetime.strptime(games[0]["startTimeUTC"][:19],'%Y-%m-%dT%H:%M:%S') - timedelta(minutes=45)
        endTime = datetime.strptime(games[-1]["startTimeUTC"][:19],'%Y-%m-%dT%H:%M:%S') + timedelta(hours=4)
    else:
        startTime = datetime.utcnow()
        endTime = startTime + timedelta(hours=1)
    if dataTomorrow["numGames"] != 0:
        startTimeTomorrow = datetime.strptime(dataTomorrow["games"][0]["startTimeUTC"][:19],'%Y-%m-%dT%H:%M:%S') - timedelta(hours=2)
    else:
        startTimeTomorrow = datetime.utcnow() + timedelta(days=1)
    sched.add_job(update_game_thread_bar, 'interval', minutes=2, max_instances=15, start_date=startTime, end_date=endTime, args=[games, redditThreadList, top_submission_markup, standing_markup, schedule_markup])
    sched.add_job(games_inactive_update_sidebar_first_run, 'date', run_date=endTime, args=[games, redditThreadList, endTime, startTimeTomorrow])
    sched.add_job(process_sidebar, 'date', run_date=startTimeTomorrow)


def get_index_markup(index_bottom_markup, redditThreadList, dateTitle, dateToday):
    """
    Variable index_bottom_markup have markup for bottom part of post body
    Variable games have all games information from todays' API
    Variable redditThreadList have reddit gameThreads and postGameThreads
    Returns game thread index markup
    """

    data = requestApi(f"http://data.nba.net/prod/v1/{dateToday}/scoreboard.json")
    if data["numGames"] != 0:
        games = data["games"]
    else:
        games = []
    index_markup = f"""# Game Threads Index ({dateTitle}):

|Tip-off|Away||Home|Status|GDT|PGT|
|:--|:--|:-:|:--|--:|:-:|:-:|\n"""
    for i in range(len(games)):
        if games[i]["isGameActivated"]:
            gameStatus = f"{games[i]['clock']} {games[i]['period']['current']}Q"
            score = f">!{games[i]['vTeam']['score']} at {games[i]['hTeam']['score']}!<"
        else:
            gameStartTime = datetime.strptime(games[i]["startTimeUTC"][:19],'%Y-%m-%dT%H:%M:%S')
            if datetime.utcnow() < gameStartTime:
                gameStatus = "PRE-GAME"
                score = ""
            else:
                score = f">!{games[i]['vTeam']['score']} at {games[i]['hTeam']['score']}!<"
                if games[i]["period"]["current"] == 5:
                    gameStatus = "FINAL-OT"
                elif games[i]["period"]["current"] > 5:
                    numOT = games[i]['period']['current']-4
                    gameStatus = f'FINAL-{numOT} OT'
                else:
                    gameStatus = "FINAL"
        if redditThreadList[i]['postGameThread'] == "" and redditThreadList[i]['gameThread'] == "":
            index_markup += f"|{games[i]['startTimeEastern']}|[{teamDict[games[i]['vTeam']['triCode']][0]}]({teamDict[games[i]['vTeam']['triCode']][3]})|{score}|[{teamDict[games[i]['hTeam']['triCode']][0]}]({teamDict[games[i]['hTeam']['triCode']][3]})|{gameStatus}|||\n"
        elif redditThreadList[i]['postGameThread'] == "":
            index_markup += f"|{games[i]['startTimeEastern']}|[{teamDict[games[i]['vTeam']['triCode']][0]}]({teamDict[games[i]['vTeam']['triCode']][3]})|{score}|[{teamDict[games[i]['hTeam']['triCode']][0]}]({teamDict[games[i]['hTeam']['triCode']][3]})|{gameStatus}|[Link]({redditThreadList[i]['gameThread']})||\n"
        elif redditThreadList[i]['gameThread'] == "":
            index_markup += f"|{games[i]['startTimeEastern']}|[{teamDict[games[i]['vTeam']['triCode']][0]}]({teamDict[games[i]['vTeam']['triCode']][3]})|{score}|[{teamDict[games[i]['hTeam']['triCode']][0]}]({teamDict[games[i]['hTeam']['triCode']][3]})|{gameStatus}||[Link]({redditThreadList[i]['postGameThread']})|\n"
        else:
            index_markup += f"|{games[i]['startTimeEastern']}|[{teamDict[games[i]['vTeam']['triCode']][0]}]({teamDict[games[i]['vTeam']['triCode']][3]})|{score}|[{teamDict[games[i]['hTeam']['triCode']][0]}]({teamDict[games[i]['hTeam']['triCode']][3]})|{gameStatus}|[Link]({redditThreadList[i]['gameThread']})|[Link]({redditThreadList[i]['postGameThread']})|\n"
    index_markup += index_bottom_markup
    return index_markup

def get_index_bottom_markup():
    """
    Returns markup for bottom part of index thread
    """
    dateTitleToday = datetime.utcnow().strftime("%B %d, %Y")
    yesterdayIndexLink = ""
    yesterday = datetime.utcnow() - timedelta(1)
    dateTitle = yesterday.strftime("%B %d, %Y")
    for submission in (reddit.subreddit('nba').search("Game Thread Index " + dateTitle, sort="new", time_filter="week")):
        if f"Game Thread Index" in submission.title:
            yesterdayIndexLink = submission.url
    index_markup = f"# [Yesterday's Game Thread Index]({yesterdayIndexLink})\n\n# Top Highlights:\n\n"
    for submission in reddit.subreddit('nba').search("highlight", sort="top", time_filter="week", limit=5):
        index_markup += f"0. [{submission.title}]({submission.url}) | [(Comments)]({submission.permalink})\n\n"
    soup = requestSoup("https://www.basketball-reference.com/friv/on_this_date.fcgi")
    index_markup += "# Day in the history:\n\n"
    eventContainer = soup.find("ul", {'class':'page_index'})
    eventList = eventContainer.find_all('li')
    if len(eventList) > 2:
        for i in range(3):
            index_markup += f"### {eventList[i].div.text}\n\n"
            index_markup += f"{eventList[i].p.text}\n\n"
    else:
        for i in range(len(eventList)):
            index_markup += f"### {eventList[i].div.text}\n\n"
            index_markup += f"{eventList[i].p.text}\n\n"
    index_markup += "Daily Discussion Thread : [Rules](https://www.reddit.com/r/nba/wiki/rules#wiki_daily_discussion_thread)"
    return index_markup

def updateGameThreadIndex(index_bottom_markup, response, games, redditThreadList, dateTitle, dateToday):
    """
    Variable index_bottom_markup have markup for bottom part of post body
    Variable response have reddit submission for todays game thread index
    Variable games have all games information from todays' API
    Variable redditThreadList have reddit gameThreads and postGameThreads
    Edits/updates game thread index
    """
    redditThreadList = get_reddit_threads(games, redditThreadList)
    try:
        response.edit(get_index_markup(index_bottom_markup, redditThreadList, dateTitle, dateToday))
    except Exception:
        traceback.print_exc()


def processGameThreadIndex():
    now = datetime.utcnow()
    dateToday = now.strftime("%Y%m%d")
    dateTitle = now.strftime("%B %d, %Y")
    data = requestApi(f"http://data.nba.net/prod/v1/{dateToday}/scoreboard.json")
    if data["numGames"] != 0:
        games = data["games"]
    else:
        games = []
    index_bottom_markup = get_index_bottom_markup()
    redditThreadList = []
    for game in games:
        redditThreadList.append({"id": game["gameId"], "gameThread": "", "postGameThread": ""})
    index_markup = get_index_markup(index_bottom_markup, redditThreadList, dateTitle, dateToday)
    if now.weekday() == 0:
        title = "Mock Draft Monday"
    elif now.weekday() == 1:
        title = "Trade Talk Tuesday"
    elif now.weekday() == 2:
        title = "Vintage Wednesday Thread"
    elif now.weekday() == 3:
        title = "Trash Talk Thursday"
    elif now.weekday() == 4:
        title = "Free Talk Friday"
    elif now.weekday() == 5:
        title = "Shitpost Saturday"
    else:
        title = "Sunday Stats Thread"
    title +=" + Game Thread Index"
    response = reddit.subreddit('nba').submit(title,  selftext=index_markup, send_replies=False)
    response.mod.sticky(bottom=False)
    response.mod.flair(text='Index Thread', css_class='index')
    response.mod.suggested_sort(sort='new')
    if data["numGames"] != 0:
        startTime = datetime.strptime(games[0]["startTimeUTC"][:19],'%Y-%m-%dT%H:%M:%S') - timedelta(minutes=45)
        endTime = datetime.strptime(games[-1]["startTimeUTC"][:19],'%Y-%m-%dT%H:%M:%S') + timedelta(hours=4)
    else:
        startTime = datetime.utcnow()+ timedelta(minutes=30)
        endTime = startTime + timedelta(hours=1)
    sched.add_job(updateGameThreadIndex, 'interval', minutes=10, max_instances=15, start_date=startTime, end_date=endTime, args=[index_bottom_markup, response, games, redditThreadList, dateTitle, dateToday])


# sched.add_job(rotateStickyThread, 'interval', minutes=60, max_instances=15)
sched.add_job(processNextDayThread, trigger='cron', hour=12)
sched.add_job(processGameThreads)
sched.add_job(process_sidebar)
sched.add_job(processGameThreadIndex, trigger='cron', hour=13)
sched.start()
