import requests, bs4
from tabulate import tabulate

res = requests.get("https://money.rediff.com/indices/nse/nifty-50")
soup = bs4.BeautifulSoup(res.text, 'html.parser')

tableContainer = soup.findAll('table')
#len(tableContainer)  == 2

trContainer = tableContainer[0].findAll('tr')
#len(trContainer) == 51

headerContainer = trContainer[0].findAll('th')
temp = []
data = []

for each in headerContainer:
    temp.append(each.text)
data.append(temp)

for i in range(1, len(trContainer)):
    company = []
    companyContainer = trContainer[i].findAll('td')
    for each in companyContainer:
        company.append(each.text.strip())
    data.append(company)

for each in data:
    print(str(each))
