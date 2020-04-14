import sys
import os

from bs4 import BeautifulSoup
import requests

from zipfile import ZipFile
import shutil

headers = {'User-Agent': 'Mozilla/5.0'}

def convert_movie_name_to_search_term(movieName):
  titleEnd = movieName.index("(")
  title = movieName[0:titleEnd].strip()

  title = title.replace("\ ", "+")
  return title

def is_my_language(language):
  return language in ["3","4","7"]

def download_subtitle(subtitle):
  downloadUrl = "https://titlovi.com/download/?type=1&mediaid=" + subtitle["id"]
  print (downloadUrl)
  file = requests.get(downloadUrl, allow_redirects=True)
  open(subtitle["id"] + ".zip", "wb").write(file.content)

def extract_subtitle(subtitle, rating):
    with ZipFile(subtitle["id"] + ".zip", 'r') as zipfile:
      files = zipfile.namelist()
      for file in files:
          if file.endswith("srt"):
            # subtitleFile = movieName + "/" + movieName + "." + str(rating) + ".srt"
            zipfile.extract(file, movieName)

def delete(subtitle):
    filename = subtitle["id"] + ".zip"
    os.remove(filename)

movieName = sys.argv[1]
searchUrl = 'https://titlovi.com/titlovi/?prijevod=' + convert_movie_name_to_search_term(movieName)
print (searchUrl)
response = requests.get(searchUrl, headers=headers, timeout=5)
content = BeautifulSoup(response.content, "html.parser")

results = content.findAll('li', attrs={"class": "subtitleContainer"})

subtitles = []
for result in results:
    id = result.find('h3')
    language = result.find('img', attrs={"class": "lang"})
    downloads = result.find('span', attrs={"class": "downloads"})
    year = result.find('i')
    if id is None or language is None or downloads is None or year is None:
        print ("result not parsable:")
        print (result)
        continue

    subtitle = {
        "id": id['data-id'],
        "language": language['alt'],
        "downloads": int(downloads.text),
        "year": year.text[1:5]
    }
    subtitles.append(subtitle)

subtitles = list(filter(lambda subtitle: is_my_language(subtitle["language"]), subtitles))

subtitles.sort(key= lambda subtitle: subtitle['downloads'], reverse= True)

rating = 0
for subtitle in subtitles:
    rating = rating + 1
    download_subtitle(subtitle)
    extract_subtitle(subtitle, rating)
    delete(subtitle)
