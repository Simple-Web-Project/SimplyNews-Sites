from bs4 import BeautifulSoup
import requests
import json
from datetime import timedelta
from .helpers import rss

identifier = "theguardian"
cache_refresh_time_delta = timedelta(hours=12)
base_url = "https://www.theguardian.com"

site_title = "The Guardian"

rss_feed = f"{base_url}/international/rss"


def get_page(url):
    full_url = f"{base_url}/{url}.json"
    page_data = json.loads(requests.get(full_url).text)
    soup = BeautifulSoup(page_data["html"], "lxml")

    data = {
        "title": page_data["config"]["page"]["headline"],
        "author": page_data["config"]["page"]["author"] or "Reuters",
        "last_updated": soup.select_one(".content__dateline time").text.strip("\n").strip(),
    }

    c = []

    assoc_media = soup.select_one("figure[itemprop='associatedMedia image']")
    if assoc_media:
        img = assoc_media.select_one("picture img")
        if img:
            c.append({"type": "image", "src": img["src"], "alt": img["alt"]})

    for element in soup.find("div", class_="content__article-body"):
        el = {}

        if element.name == "p":
            el["type"] = "paragraph"
            el["value"] = element.text
        elif element.name == "figure":
            image = element.find("img")
            if image:
                el["type"] = "image"
                el["src"] = image["src"]
                el["alt"] = image["alt"]
        elif element.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            el["type"] = "header"
            el["size"] = element.name
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
    print(get_recent_articles())
    #get_page(
    #    "https://www.theguardian.com/world/2021/jan/31/uk-help-eu-not-affect-vaccine-timetable-liz-truss"
    #)
