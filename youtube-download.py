import bs4, requests
from pytube import YouTube
import sys
from tabulate import tabulate
import pafy

#Save the name of Channel and link as a dictionary here
allChannels = [['Zack Lee', 'https://www.youtube.com/channel/UCn3-IBtTKq8ZTV5hiZT-7bQ'], 
			   ['Every Frame a Painting', 'https://www.youtube.com/user/everyframeapainting'], 
			   ['Nerdwriter', 'https://www.youtube.com/user/Nerdwriter1'],
			   ['Aleczandxr', 'https://www.youtube.com/channel/UCUUYiPd9TKE62mUn-lJ29AQ'],
			   ['Kurzgesagt - In a Nutshell', 'https://www.youtube.com/user/Kurzgesagt'],
			   ]
#Number of videos to list; Keep it less than 30
listVid = 5
#Dictionary for non bmp characters
non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)

print("List of Channels:")

for i in range(len(allChannels)):
	print(str(i+1) + ". " + str(allChannels[i][0]))


channelIndex = int(input("Choose one of the channel by index number: "))
res = requests.get(str(allChannels[channelIndex - 1][1]) + '/videos')
soup = bs4.BeautifulSoup(res.text, 'html.parser')
allVids = soup.findAll('div', {'class':'yt-lockup-content'})
wantedVids = allVids[:listVid]
vidTitles = []
vidLinks = []
vidDuration = []
vidViews = []
vidUploaded = []
for each in wantedVids:
	vidATag = each.find('a')
	vidSpanTag = each.find('span')
	vidLiTag = each.findAll('li')
	vidTitles.append(str(vidATag.text).translate(non_bmp_map))
	vidLinks.append("https://youtube.com" + str(vidATag['href']))
	vidDuration.append(str(vidSpanTag.text).replace("- Duration: ", ""))
	vidViews.append(str(vidLiTag[0].text).replace("views", ""))
	vidUploaded.append(vidLiTag[1].text)
vidIndex = range(1, listVid + 1)
header = ["Index", "Title", "Duration", "Views", "Uploaded"]
table = zip(vidIndex, vidTitles, vidDuration, vidViews, vidUploaded)
print(tabulate((table), header, tablefmt="grid"))
choosenVids = list(map(int, input("Enter index of all videos you want to download(Space seperated values: ").split()))
for each in choosenVids:
	if int(each)>listVid or int(each)<1:
		print("Index out of bound")
	url = str(vidLinks[int(each-1)])
	video = pafy.new(url)
	best = video.getbest()
	best.download(quiet=False)






'''>>> import csv
>>> table = []
>>> with open("Math-Grade-6.csv", "r") as csvfile:
...     csvreader = csv.reader(csvfile, skipinitialspace=True)
...     for row in csvreader:
...             table.append(row)
...             print(row)
... 
 '''