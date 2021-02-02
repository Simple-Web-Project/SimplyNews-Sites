from bs4 import BeautifulSoup
import feedparser
import urllib
import requests
from datetime import timedelta

cache_refresh_time_delta = timedelta(hours=12)
identifier = "nytimes"
base_url = "https://nytimes.com"

site_title = "New York Times"

rss_feed = "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"

def get_page(url):
    full_url = f"{base_url}/{url}"
    soup = BeautifulSoup(requests.get(full_url).text, "lxml")
    print(soup)

def get_recent_articles():
    feed = feedparser.parse(rss_feed)
    feed_ = []
    for entry in feed["entries"]:
        url = urllib.parse.urlparse(entry["link"])
        local_link = url.path.strip("/")  # Kill annoying slashes

        feed_.append({"title": entry["title"], "link": local_link})

    return feed_

if __name__ == "__main__":
    #print(get_recent_articles())
    get_page("2021/01/31/us/gene-allmond-john-brooks-hamilton-georgia.html")
