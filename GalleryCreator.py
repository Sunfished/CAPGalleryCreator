from bs4 import BeautifulSoup
import requests
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
import numpy as np
import datetime

# Image Related
import PIL
from PIL import Image
import math
from PIL import ImageFont
from PIL import ImageDraw
from io import BytesIO

#imgur
import pyimgur
CLIENT_ID = "_IMGUR_CLIENT_ID_"
CLIENT_SECRET = "_IMGUR_CLIENT_SECRET_"
im = 0

# Modified using paintseagull's counter.py as a base

print("Paste first page of Art Thread:")
base_url = "https://www.smogon.com/forums/threads/cap-26-art-submissions.3648463/"#input("");

# Ask if to create Collage
print("Upload Collage to imgur? (y/n)")
canCollage = input().lower()
if canCollage == "y":
    im = pyimgur.Imgur(CLIENT_ID)
    print("Logged in using CLIENT_ID")

# Count how many pages there are
pagecount = 1;
stop = True
while(stop):

    myPage = base_url
    if pagecount > 1:
        myPage += 'page-' + str(pagecount)

    myURL = requests.get(myPage, allow_redirects=False)

    # Check if page exists
    if myURL.status_code == 200:
        print(myPage + " exists! Continuing...")
        pagecount+= 1
    else:
        print(myPage + ' does not exist, so stopping...')
        pagecount-= 1
        stop = False

print("# of Pages:" + str(pagecount))

def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors.
    This function just prints them, but you can
    make it do anything.
    """
    print(e)

#soup = BeautifulSoup(simple_get(base_url),'html.parser')
#print(soup.prettify())
#input()
#exit()

#vote_list = []
listPosts = []
listNames = []

#Iterate through pages
for i in range(1, pagecount+1):

    #Skip First 2 Posts if first page
    if i == 1:
        raw_html = simple_get(base_url)
        start_ind = 2
        print(len(raw_html))
    else:
        raw_html = simple_get(base_url+'page-'+str(i))
        start_ind = 0
        print(len(raw_html))

    # Grab Post Contents
    soup = BeautifulSoup(raw_html, 'html.parser')
    bbwrapper = soup.findAll("div", {"class": "bbWrapper"})
    for ballot in bbwrapper[start_ind::]:
        #print(ballot)
        listPosts.append(ballot)

    # Grab Names
    h4 = soup.findAll("h4", {"class": "message-name"},"span")
    for name in h4[start_ind::]:
        myName = name.text
        #print(myName)
        listNames.append(myName)

lenPosts = len(listPosts)
lenNames = len(listNames)
print("Number of Posts: " + str(lenPosts))
print("Number of Names: " + str(lenNames))
listEntries = []

# Combine Names and Posts
if lenPosts == lenNames:
    for i in range(lenPosts):
        listEntrant = []
        listEntrant.append(listNames[i])
        listEntrant.append(listPosts[i])
        listEntries.append(listEntrant)
else:
    print("There are an unequal amount of names and posts...?")
    input()
    exit()

print("\nList of Entry Names:")
for i in range(len(listEntries)):
    print(listEntries[i][0])

#Cull Names if WIP or Final Submission not in post
listCulledEntries = []
for i in range(len(listEntries)):
    myText = listEntries[i][1].get_text().lower().strip()

    if True:#myText.find("wip") != -1 or myText.find("final submission") != -1:
        mySub = "WIP"
        if myText.find("final submission") != -1:
            mySub = "Final Submission"
        newEntry = []
        newEntry.append(listEntries[i][0])
        newEntry.append(listEntries[i][1])
        newEntry.append(mySub)
        listCulledEntries.append(newEntry)
        print("Added Post #" + str(i+3) + " to entry list")

print("\nList of Culled Entry Names:")
for i in range(len(listCulledEntries)):
    print(listCulledEntries[i][0])

#Cull Names if art not in post
listArtEntries = []
for i in range(len(listCulledEntries)):
    links = []
    #links = listCulledEntries[i][1].find_all('a', {"class": "link link--external"})
    links = listCulledEntries[i][1].find('img')
    
    print()
    #print(listCulledEntries[i][1])
    print(listCulledEntries[i][0] + "'s links:")
    #for i in links:
    print(links)
    if links:
        myURL = links["src"]
        print("Using Link: " + myURL)
        myEntrant = []
        myEntrant.append(listCulledEntries[i][0])
        if "https://" not in myURL:
            myURL = "https://smogon.com" + myURL
        myEntrant.append(myURL)
        myEntrant.append(listCulledEntries[i][2])
        listArtEntries.append(myEntrant)
    else:
        print("Ignored Entrant since no Link")

print("\nList of Art Entry Names:")
for i in range(len(listArtEntries)):
    print(listArtEntries[i][0] + " using " + listArtEntries[i][1])

# Cull Duplicates
listFinal = []
listArtEntries.reverse()
for i in range(len(listArtEntries)):

    # Add the first entry
    if i == 0:
        listFinal.append(listArtEntries[i])
    else:
        passed = True
        for ii in range(len(listFinal)):
            if listArtEntries[i][0] in listFinal[ii][0]:
                passed = False
        if passed:
            print("Added " + listArtEntries[i][2] + " Entry for " + listArtEntries[i][0] + " using link: " + listArtEntries[i][1])
            listFinal.append(listArtEntries[i])
        else:
            print("Removed older entry for " + listArtEntries[i][0])

# Sort Names
print("\nList of Sorted Final Entry Names:")
listFinal.sort()
for i in range(len(listFinal)):
    print(listFinal[i][0] + " using " + listFinal[i][1])
print("Total Final Entrants: " + str(len(listFinal)))

# Create Collage
cellSize = 250
maxCells = 6
topBuffer = 50
cWidth = cellSize*maxCells
rows = math.ceil(len(listFinal)/maxCells)
cHeight = (rows*cellSize) + (rows*topBuffer)
collage = Image.new('RGB',(cWidth,cHeight),(255,255,255))
draw = ImageDraw.Draw(collage)
font = ImageFont.truetype("arial.ttf", 16)
print("Collage Size: " + str(collage.width) + " / " + str(collage.height))

#Paste Images in
myX = 0
myY = 0#topBuffer
for i in range(len(listFinal)):
    print()
    print("Reading " + listFinal[i][1] + "...")
    
    response = requests.get(listFinal[i][1])
    img = Image.open(BytesIO(response.content))

    #Thumbnail and adjust offsets
    img.thumbnail((cellSize,cellSize))
    xOff = math.floor(myX + ((cellSize-img.width)/2))
    yOff = math.floor(myY + ((cellSize-img.height)/2))

    print("Pasting at " + str(xOff) + " / " + str(yOff))

    # Paste if Alpha is good
    try:
        collage.paste(img,(xOff,yOff), img)
    except ValueError:
        collage.paste(img,(xOff,yOff))

    # Draw Name / Progress
    w, h = draw.textsize(listFinal[i][0])
    tx = myX + ((cellSize-w)/2)
    ty = myY + cellSize + 2
    draw.text((tx,ty), listFinal[i][0], fill="black", font=font)

    w, h = draw.textsize(listFinal[i][2])
    tx = myX + ((cellSize-w)/2)
    ty = myY + cellSize + 2 + (h*2)
    draw.text((tx,ty), listFinal[i][2], fill="black", font=font)

    # Move to next cells
    myX += cellSize
    if myX >= cellSize*maxCells:
        myX = 0
        myY += cellSize+topBuffer

collage.save("collage.png")
print("Saved collage.png")

# Upload to imgur
collageLink = ""
if canCollage == "y":
    path = "collage.png"
    date = datetime.datetime.today()
    uploaded = im.upload_image(path, title= "CAP Collage " + date.strftime("%d-%B-%Y %H:%M:%S"))
    collageLink = "Collage Link: " + uploaded.link + "\n\n"
    print("Uploaded to imgur: " + collageLink)

# Create Paste-able
myPaste = ""
for i in range(len(listFinal)):
    myName = "[b]" + listFinal[i][0] + "[/b]"
    myPost = "[hide][img]" + listFinal[i][1] + "[/img][/hide]"
    myPaste += myName + "\n" + myPost + "\n"

# Finalize Post
myDisclaimer = open("disclaimer.txt", 'r').read()
myPaste = myDisclaimer + "\n\n" + collageLink + myPaste

print()
print(myPaste)

myFile = open("post.txt","w+")
myFile.write(myPaste)
myFile.close()

print("Successfully saved post.txt!")
print("Total Entries: " + str(len(listFinal)))




            
