from bs4 import BeautifulSoup
import requests
import json
from datetime import timedelta
import urllib
import feedparser

r = requests.get('https://www.aljazeera.net/news/politics/2022/4/20/%D9%81%D9%84%D8%B3%D8%B7%D9%8A%D9%86-24')
soup = soup = BeautifulSoup(r.text, "lxml")
content =  soup.findAll(class_='wysiwyg')[0]
title =  soup.findAll(class_='article-header')[0].findAll('h1')[0].text
print(title)
# print(content)
