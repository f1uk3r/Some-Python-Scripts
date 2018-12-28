import requests
import json
from datetime import date, timedelta
from tabulate import tabulate

#getting json data from requsted url
def requestApi(url):
  req = requests.get(url)
  return req.json()

#getting whole NBA Schedule
nbaSchedule = requestApi("http://data.nba.net/prod/v1/2018/schedule.json")
allGames = nbaSchedule["league"]["standard"]
allSunsSeasonGames = []
for each in allGames:
  if (each["gameUrlCode"][9:12] == "PHX" or each["gameUrlCode"][-3:] == "PHX") and 'tags' not in each and each["hTeam"]["score"] != "":
    allSunsSeasonGames.append(each)

biggestLeadList = []
for each in allSunsSeasonGames:
  gameData = requestApi("http://data.nba.net/prod/v1/" + each["startDateEastern"] + "/" + each["gameId"] + "_boxscore.json")
  if each["gameUrlCode"][9:12] == "PHX":
    phxIsAwayTeam = True
  else:
    phxIsAwayTeam = False
  if phxIsAwayTeam == True:
    biggestLeadList.append(gameData["stats"]["vTeam"]["biggestLead"])
  else:
    biggestLeadList.append(gameData["stats"]["hTeam"]["biggestLead"])
print(biggestLeadList)