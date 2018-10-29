import praw
import config
import requests
import json
import datetime
from tabulate import tabulate

teamDict = {
  "ATL": "Atlanta Hawks",
  "BKN": "Brooklyn Nets",
  "BOS": "Boston Celtics",
  "CHA": "Charlotte Hornets",
  "CHI": "Chicago Bulls",
  "CLE": "Cleveland Cavaliers",
  "DAL": "Dallas Mavericks",
  "DEN": "Denver Nuggets",
  "DET": "Detroit Pistons",
  "GSW": "Golden State Warriors",
  "HOU": "Houston Rockets",
  "IND": "Indiana Pacers",
  "LAC": "Los Angles Clippers",
  "LAL": "Los Angles Lakers",
  "MEM": "Memphis Grizzlies",
  "MIA": "Miami Heat",
  "MIL": "Milwaukee Bucks",
  "MIN": "Minnesota Timberwolves",
  "NOP": "New Orleans Pelicans",
  "NYK": "New York Knicks",
  "OKC": "Oklahoma City Thunder",
  "ORL": "Orlando Magic",
  "PHI": "Philadelphia 76ers",
  "PHX": "Phoenix Suns",
  "POR": "Portland Trail Blazers",
  "SAC": "Sacramento Kings",
  "SAS": "San Antonio Spurs",
  "TOR": "Toronto Raptors",
  "UTA": "Utah Jazz",
  "WAS": "Washington Wizards"
}

reddit = praw.Reddit(username = config.username, 
                    password = config.password,
                    client_id = config.client_id, 
                    client_secret = config.client_secret,
                    user_agent = "script:reddit-boxscore-test:v0.1 (by /u/f1uk3r)")

now = datetime.datetime.now()
date = str(now.year) + str(now.month) + str(now.day-1)
req = requests.get("http://data.nba.net/prod/v1/" + date + "/scoreboard.json")
data = req.json()
gamesToday = data["numGames"]
games = data["games"]
print("Showing finished games")

header = ["index","gameId", "title", "gameDuration"]
tabulateList = []
index = 1
for each in games:
  if each["isGameActivated"] == False and each["endTimeUTC"] != "":
    gameId = each["gameId"]
    gameDuration = each["gameDuration"]["hours"] + ":" + each["gameDuration"]["minutes"]
    visitorTeam = teamDict[each["vTeam"]["triCode"]] + " (" + each["vTeam"]["win"] + "-" + each["vTeam"]["loss"] + ")"
    visitorTeamScore = each["vTeam"]["score"]
    homeTeam = teamDict[each["hTeam"]["triCode"]] + "(" + each["hTeam"]["win"] + "-" + each["hTeam"]["loss"] + ")"
    homeTeamScore = each["hTeam"]["score"]
    if (int(visitorTeamScore) > int(homeTeamScore)):
      title = "[Post Game Thread] The " + visitorTeam + " defeats the @" + homeTeam + ", " + visitorTeamScore + " - " + homeTeamScore
    else:
      title = "[Post Game Thread] The " + homeTeam + " defeats the v" + visitorTeam + ", " + homeTeamScore + " - " + visitorTeamScore
    row = [index, gameId, title, gameDuration]
    tabulateList.append(row)
    index += 1
print(tabulate((tabulateList), header, tablefmt="grid"))
game = int(input("Choose the game (by index) you want to make Post Game Thread of: ")) -1
reqBox = requests.get("http://data.nba.net/prod/v1/" + date + "/" + str(tabulateList[game][1]) + "_boxscore.json")
dataBoxScore = reqBox.json()


