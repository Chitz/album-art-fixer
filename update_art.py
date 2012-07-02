import sys,re
from mutagen.mp3 import MP3 
from mutagen.id3 import ID3,APIC,error
from mutagen.easyid3 import EasyID3 
from bs4 import BeautifulSoup
from os import listdir,getcwd
import urllib2,urllib
import Image
bPage = urllib2.urlopen("http://b-imdb.com/movies/")
bSoup = BeautifulSoup(bPage)
path = sys.argv[1]
files = []
fil = []
workingDir = getcwd()
for filename in listdir(path):
	files.append(filename)
for f in files:
	audio = MP3(path+"/"+f,ID3= EasyID3)
	if 'website' in audio.keys():
		if 'www.Songs.PK' in audio['website']:
			fil.append(f)

def check_art(movie):
	for i in listdir(workingDir+"/"):
		if movie in i:
			return True
	return False

def resize_image(image_path):
	image = Image.open(image_path)
	image = image.resize((500,500),Image.ANTIALIAS)
	image.save(image_path)

def get_art(year,movie):
	movieList = bSoup.findAll('a',text=re.compile("^"+movie+"$", re.I))
	if len(movieList) == 0:
		params = {"t":movie}
		xmlLink = "http://www.imdbapi.com/?i=&r=XML&"+urllib.urlencode(params)
		xPage = urllib2.urlopen(xmlLink)
		xSoup = BeautifulSoup(xPage)
		xMovie = xSoup.find_all('movie')
		if len(xMovie) == 0:
			print "Can't find album art for the movie"
		else:	
			artLink = xMovie[0]['poster'].encode('utf-8')
			a = urllib.urlretrieve(artLink,movie+'.jpg')
			resize_image(movie+'.jpg')
			print "Album art for the movie ", movie, " is found ", movie,".jpg created"
	else:
		movieLink = movieList[0]['href'].encode('utf-8')
		movieLink = urllib2.urlparse.urljoin('http://b-imdb.com/movies/',movieLink)
		mPage = urllib2.urlopen(movieLink)
		mSoup = BeautifulSoup(mPage)
		movieLink = mSoup.findAll('img',alt=movie)[0]['src'].encode('utf-8')
		artLink = urllib2.urlparse.urljoin("http://b-imdb.com/some/path",movieLink)
		a = urllib.urlretrieve(artLink,movie+'.jpg')
		resize_image(movie+'.jpg')
		print "Album art for the movie ", movie, " is found ", movie,".jpg created"

def edit_tags(files):
	count = 0
	for f in files:
		audio = MP3(path+"/"+f,ID3= EasyID3)
		for key in audio.keys():
			for j in audio[key]:
				if 'www.Songs.PK' in j:
					audio[key] = audio[key][0].encode('utf-8').replace('www.Songs.PK','')

		album_year = int(audio['date'][0])
		movie_name = str(audio['album'][0])
		audio.save()
		if not check_art(movie_name):
			get_art(album_year,movie_name)
		audio = MP3(path+"/"+f,ID3=ID3)
		if 'APIC:' in audio.keys():
			audio.pop('APIC:') 	
		audio.tags.add(
   			APIC(
        		encoding=3, # 3 is for utf-8
        		mime='image/png', # image/jpeg or image/png
        		type=3, # 3 is for the cover image
        		desc=u'Cover',
        		data=open(movie_name+".jpg").read()
    			)
			)
		print "Album art for the song ", f, "from the movie ", movie_name, " is updated"
		audio.save()

edit_tags(fil)

