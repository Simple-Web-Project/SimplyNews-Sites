from bs4 import BeautifulSoup
import requests
import urllib
import feedparser
from datetime import timedelta

cache_refresh_time_delta = timedelta(hours=12)
identifier = "theverge"
site_title = "TheVerge"

rss_feed = "https://theverge.com/rss/full.xml"


def get_page(url):
    full_url = "https://theverge.com/" + url
    soup = BeautifulSoup(requests.get(full_url).text, "lxml")

    data = {
        "title": soup.find("h1", class_="c-page-title").text,
        "author": soup.find("span", class_="c-byline__author-name").text,
        "last_updated": soup.find("time", class_="c-byline__item").text,
    }

    title_image = soup.find("picture", class_="c-picture").find("img")
    c = []
    c.append({"type": "image", "src": title_image["src"]})

    for element in soup.find("div", class_="c-entry-content"):
        el = {}
        if element.name == "p":
            el["type"] = "paragraph"
            el["value"] = element.text
        elif element.name == "blockquote":
            el["type"] = "blockquote"
            el["value"] = element.text
        else:
            if element.name is not None:
                print("Ignoring:", element.name)
            el = None

        if el is not None:
            c.append(el)
    data["article"] = c

    return data


def get_recent_articles():
    feed = feedparser.parse(rss_feed)
    feed_ = []
    for entry in feed["entries"]:
        url = urllib.parse.urlparse(entry["link"])
        local_link = url.path.strip("/")  # Kill annoying slashes

        feed_.append({"title": entry["title"], "link": local_link})

    return feed_


if __name__ == "__main__":
    get_page("2021/1/30/22257721/whatsapp-status-privacy-facebook-signal-telegram/")
    # get_recent_articles()
