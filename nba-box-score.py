import requests, bs4
from tabulate import tabulate

res = requests.get("http://www.nbaboxscoregenerator.com/")
soup = bs4.BeautifulSoup(res.text, 'html.parser')

allGamesContainer = soup.findAll('option')

for i in range(len(allGamesContainer)):
	print(str(i+1) + ". " + allGamesContainer[i].text)
game = int(input("Choose one of the games mentioned above with their indexes: "))

if 0 < game and game < len(allGamesContainer)+1:
	resGame = requests.get("http://www.nbaboxscoregenerator.com/?gameID=" + str(game - 1))
	soupGame = bs4.BeautifulSoup(res.text, 'html.parser')
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
					row.append(each.text)
				tabulateList.append(row)
		print(tabulate((tabulateList), header, tablefmt="grid"))