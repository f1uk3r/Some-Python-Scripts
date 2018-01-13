# python3
# nba-box-score.py -- reads the table from nbaboxscoregenerator.com and print them on command line
# pip install requests, bs4, tabulate

import requests, bs4
from tabulate import tabulate

res = requests.get("http://www.nbaboxscoregenerator.com/")
soup = bs4.BeautifulSoup(res.text, 'html.parser')

allGamesContainer = soup.findAll('option')

for i in range(len(allGamesContainer)):
	print(str(i+1) + ". " + allGamesContainer[i].text)
game = 1
while game != 0 :
	print("Enter 0 to exit")
	game = int(input("Choose one of the games mentioned above with their indexes: "))

	if game > 0 and game < (len(allGamesContainer) + 1):
		resGame = requests.get("http://www.nbaboxscoregenerator.com/?gameID=" + str(game - 1))
		soupGame = bs4.BeautifulSoup(resGame.text, 'html.parser')																																																										
		tableContainer = soupGame.findAll('table')
		for table in tableContainer:
			tabulateList = []
			header = []
			trContainer = table.findAll('tr')
			headerContainer = trContainer[0].findAll('th')
			for each in headerContainer:
				header.append(each.text)
			for i in range(1, len(trContainer)):
				row = []
				rowContainer = trContainer[i].findAll('td')
				if len(rowContainer) > 3:
					for each in rowContainer:
						row.append(each.text.replace('(', '\n('))
					tabulateList.append(row)
			print(tabulate((tabulateList), header, tablefmt="grid"))
	elif game == 0:
		print("Thank You")
	else:
		print("Please choose a number from the index or press 0 to exit") 

