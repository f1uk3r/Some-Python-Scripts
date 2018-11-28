import config
import requests
import json
from datetime import date, timedelta
from tabulate import tabulate

#finding player's name when player's ID is given, dataPlayersLeague is a list of all players
def findPlayerName(dataPlayersLeague, playerId):
  for each in dataPlayersLeague:
    if each["personId"] == playerId:
      return each["firstName"] + " " + each["lastName"]

def requestApi(url):
  req = requests.get(url)
  return req.json()

def playerDataList(dataPlayersLeague, playerId):
  playerData = requestApi("http://data.nba.net/prod/v1/2018/players/" + str(playerId) + "_profile.json")
  playerCurrentData = playerData["league"]["standard"]["stats"]["latest"]
  playerRequiredData = []
  playerRequiredData.append(findPlayerName(dataPlayersLeague, playerId))
  playerRequiredData.append(playerCurrentData["ppg"])
  playerRequiredData.append(playerCurrentData["rpg"])
  playerRequiredData.append(playerCurrentData["apg"])
  playerRequiredData.append(playerCurrentData["spg"])
  playerRequiredData.append(playerCurrentData["bpg"])
  return playerRequiredData

#getting informations of players through API since the boxscore API lacks name of players
dataPlayers = requestApi("http://data.nba.net/prod/v1/2018/players.json")
dataPlayersLeague = dataPlayers["league"]["standard"] + dataPlayers["league"]["africa"] + dataPlayers["league"]["sacramento"] + dataPlayers["league"]["vegas"] + dataPlayers["league"]["utah"]

teamData = requestApi("http://data.nba.net/prod/v1/2018/teams/1610612759/roster.json")
teamPlayers = teamData["league"]["standard"]["players"]
header = ["PLAYER", "PTS", "REB", "AST", "STL", "BLK"]
tabulateData = []

for each in teamPlayers:
  tabulateData.append(playerDataList(dataPlayersLeague, each["personId"]))

print(tabulate((tabulateData), header, tablefmt="grid"))