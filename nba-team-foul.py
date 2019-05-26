
    import requests, bs4
    from tabulate import tabulate
    from selenium import webdriver


    #Team Dictionary helps to make urls for boxscore and for full-forms of abbrevation of teams
    teamDict = {
      "ATL": ["Atlanta Hawks","01", "atlanta-hawks-", "/r/atlantahawks", "1610612737", "Hawks"],
      "NJN": ["Brooklyn Nets", "02", "boston-celtics-", "/r/bostonceltics", "1610612738", "Nets"],
      "BOS": ["Boston Celtics", "17", "brooklyn-nets-","/r/gonets", "1610612751", "Celtics"],
      "CHA": ["Charlotte Hornets", "30", "charlotte-hornets-","/r/charlottehornets", "1610612766", "Hornets"],
      "CHI": ["Chicago Bulls", "04", "chicago-bulls-","/r/chicagobulls", "1610612741", "Bulls"],
      "CLE": ["Cleveland Cavaliers", "05", "cleveland-cavaliers-","/r/clevelandcavs", "1610612739", "Cavaliers"],
      "DAL": ["Dallas Mavericks", "06", "dallas-mavericks-","/r/mavericks", "1610612742", "Mavericks"],
      "DEN": ["Denver Nuggets", "07", "denver-nuggets-","/r/denvernuggets", "1610612743", "Nuggets"],
      "DET": ["Detroit Pistons", "08", "detroit-pistons-", "/r/detroitpistons", "1610612765", "Pistons"],
      "GSW": ["Golden State Warriors", "09", "golden-state-warriors-", "/r/warriors", "1610612744", "Warriors"],
      "HOU": ["Houston Rockets", "10", "houston-rockets-", "/r/rockets", "1610612745", "Rockets"],
      "IND": ["Indiana Pacers", "11", "indiana-pacers-", "/r/pacers", "1610612754", "Pacers"],
      "LAC": ["Los Angeles Clippers", "12", "los-angeles-clippers-", "/r/laclippers", "1610612746", "Clippers"],
      "LAL": ["Los Angeles Lakers", "13", "los-angeles-lakers-", "/r/lakers", "1610612747", "Lakers"],
      "MEM": ["Memphis Grizzlies", "29", "memphis-grizzlies-", "/r/memphisgrizzlies", "1610612763", "Grizzlies"],
      "MIA": ["Miami Heat", "14", "miami-heat-", "/r/heat", "1610612748", "Heat"],
      "MIL": ["Milwaukee Bucks", "15", "milwaukee-bucks-", "/r/mkebucks", "1610612749", "Bucks"],
      "MIN": ["Minnesota Timberwolves", "16", "minnesota-timberwolves-", "/r/timberwolves", "1610612750", "Timberwolves"],
      "NOH": ["New Orleans Pelicans", "03", "new-orleans-pelicans-", "/r/nolapelicans", "1610612740", "Pelicans"],
      "NYK": ["New York Knicks", "18", "new-york-knicks-", "/r/nyknicks", "1610612752", "Knicks"],
      "OKC": ["Oklahoma City Thunder", "25", "oklahoma-city-thunder-", "/r/thunder", "1610612760", "Thunder"],
      "ORL": ["Orlando Magic", "19", "orlando-magic-", "/r/orlandomagic", "1610612753", "Magic"],
      "PHI": ["Philadelphia 76ers", "20", "philadelphia-76ers-", "/r/sixers", "1610612755", "76ers"],
      "PHX": ["Phoenix Suns", "21", "phoenix-suns-", "/r/suns", "1610612756", "Suns"],
      "POR": ["Portland Trail Blazers", "22", "portland-trail-blazers-", "/r/ripcity", "1610612757", "Trail Blazers"],
      "SAC": ["Sacramento Kings", "23", "sacramento-kings-", "/r/kings", "1610612758", "Kings"],
      "SAS": ["San Antonio Spurs", "24", "san-antonio-spurs-", "/r/nbaspurs", "1610612759", "Spurs"],
      "TOR": ["Toronto Raptors", "28", "toronto-raptors-", "/r/torontoraptors", "1610612761", "Raptors"],
      "UTA": ["Utah Jazz", "26", "utah-jazz-", "/r/utahjazz", "1610612762", "Jazz"],
      "WAS": ["Washington Wizards", "27", "washington-wizards-", "/r/washingtonwizards", "1610612764, ", "Wizards"]
    }

    teamShort = []
    baseUrl = "https://www.basketball-reference.com"
    allData = {}

    def requestSoup(url):
      res = requests.get(url)
      return bs4.BeautifulSoup(res.text, 'html.parser')

    for each in teamDict.keys():
      teamShort.append(each)

    driver = webdriver.Chrome()

    driver.get("https://www.basketball-reference.com/leagues/NBA_2019.html")
    thisYearStatsPage = bs4.BeautifulSoup(driver.page_source, "html.parser")
    tableContainer = thisYearStatsPage.find("table", {"id":"team-stats-per_game"})
    personalFoulTbodyContainer = tableContainer.find("tbody")
    dataRow = personalFoulTbodyContainer.findAll("tr")
    for eachRow in dataRow:
      allData[str(eachRow.find("a").text)] = [eachRow.find("td", {"data-stat":"pf"}).text]

    tableContainer = thisYearStatsPage.find("table", {"id":"opponent-stats-per_game"})
    opponentFoulTbodyContainer = tableContainer.find("tbody")
    dataRow = opponentFoulTbodyContainer.findAll("tr")
    for eachRow in dataRow:
      allData[str(eachRow.find("a").text)].append(eachRow.find("td", {"data-stat":"opp_pf"}).text)



    print(allData)
    driver.quit()
