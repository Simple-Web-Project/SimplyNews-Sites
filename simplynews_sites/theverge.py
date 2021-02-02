from bs4 import BeautifulSoup
import requests
from datetime import timedelta
from simplynews_sites.helpers import rss

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
    return rss.default_feed_parser(rss_feed)

if __name__ == "__main__":
    #get_page("2021/1/30/22257721/whatsapp-status-privacy-facebook-signal-telegram/")
    print(get_recent_articles())
