import urllib.request
from bs4 import BeautifulSoup
fhand=urllib.request.urlopen('http://data.pr4e.org/romeo.txt')
for i in fhand:
    print(i.decode().strip())
