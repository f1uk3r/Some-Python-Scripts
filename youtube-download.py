# python3
# youtube-download.py - Download latest videos from youtube channels given their urls in the file
# pip install bs4, requests, tabulate, pafy
# If you don't want to download video but want to play it on vlc, set vidOrUrl to "2", it will
# give you url for the video, copy the url, go to vlc, press Ctrl+S, 
# go to network, paste the url to text field, click the down arrow on the right of Stream button
# and choose play

import bs4, requests
import sys
from tabulate import tabulate
import pafy

#Save the name of Channel and link in the list here
allChannels = [['Zack Lee', 'https://www.youtube.com/channel/UCn3-IBtTKq8ZTV5hiZT-7bQ'], 
			   ['Every Frame a Painting', 'https://www.youtube.com/user/everyframeapainting'], 
			   ['Nerdwriter', 'https://www.youtube.com/user/Nerdwriter1'],
			   ['Aleczandxr', 'https://www.youtube.com/channel/UCUUYiPd9TKE62mUn-lJ29AQ'],
			   ['Kurzgesagt - In a Nutshell', 'https://www.youtube.com/user/Kurzgesagt'],

			   ]
#Number of videos to list; Keep it less than 30
listVid = 5
#Choose 1 to download video, 2 to get url
vidOrUrl = 2
#If vidOrUrl is set to 1, Specify resolution here; Choose from 1080, 720, 480, 360, 240 and 144
quality = 480
#Dictionary for non bmp characters
non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)

print("List of Channels:")

for i in range(len(allChannels)):
	print(str(i+1) + ". " + str(allChannels[i][0]))
channelIndex = 1
while channelIndex != 0:
	channelIndex = int(input("Choose one of the channel by index number(Press 0 to exit): "))
	if channelIndex > 0 and channelIndex < (len(allChannels) + 1):
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
		# this will make a list of space seperated value (for eg. 5 4 2 1) and download in that order
		choosenVids = list(map(int, input("Enter index of all videos you want to download(Space seperated values): ").split()))
		for each in choosenVids:
			if int(each)>listVid or int(each)<1:
				print("Index out of bound")
			else:
				url = str(vidLinks[int(each-1)])
				if vidOrUrl == 1:
					video = pafy.new(url)
					streams = video.allstreams
					for s in streams:
						if quality == 1080:
							if s.extension == "webm" and s.quality == "1920x1080":
								print(video.title + " is downloading ...")
								s.download(quiet=False)
								print("Download complete.")
						elif quality == 720:
							if s.extension == "mp4" and s.quality == "1280x720":
								print(video.title + " is downloading ...")
								s.download(quiet=False)
								print("Download complete.")
						elif quality == 480:
							if s.extension == "webm" and s.quality == "720x480":
								print(video.title + " is downloading ...")
								s.download(quiet=False)
								print("Download complete.")
						elif quality == 360:
							if s.extension == "mp4" and s.quality == "640x360":
								print(video.title + " is downloading ...")
								s.download(quiet=False)
								print("Download complete.")
						elif quality == 240:
							if s.extension == "webm" and s.quality == "360x240":
								print(video.title + " is downloading ...")
								s.download(quiet=False)
								print("Download complete.")
						elif quality == 144:
							if s.extension == "webm" and s.quality == "256x144":
								print(video.title + " is downloading ...")
								s.download(quiet=False)
								print("Download complete.")
						else:
							print("Sorry this resolution for " + video.title + " not found.")
							break
				elif vidOrUrl == 2:
					print(url)
				else:
					print("Sorry, you can choose from either video or url")			
	elif channelIndex == 0:
		print("Thanks")
	else:
		print("Please choose a number from the index or press 0 to exit") 


# possible upgrades
# - play video in vlc or other media player without downloading 
# - video downloads in the folder provided the correct path
