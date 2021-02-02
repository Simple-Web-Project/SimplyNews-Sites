from bs4 import BeautifulSoup
import feedparser
import urllib
import requests
from datetime import timedelta

cache_refresh_time_delta = timedelta(hours=12)
identifier = "makeuseof"
base_url = "https://makeuseof.com"

site_title = "Make Use Of"

rss_feed = f"{base_url}/feed/"

def get_page(url):
    full_url = f"{base_url}/{url}"
    soup = BeautifulSoup(requests.get(full_url).text, "lxml")

    data = {
        'title': soup.find('h1', class_='heading_title').text,
        'subtitle': soup.find('p', class_='heading_excerpt').text,
        'author': soup.find('a', class_='meta_txt author').text[3:], # Kill the 'By '
        'last_updated': soup.find('span', class_='meta_txt date').find('time')["datetime"]
    }

    c = []
    heading_image = soup.find('div', class_='heading_image').find('picture')
    c.append({
        'type': 'image',
        'alt': heading_image.find('img')['alt'],
        'src': heading_image.find('source')['srcset']
    })

    for element in soup.find('section', class_='article-body'):
        el = {}

        if element.name == 'p':
            el["type"] = 'paragraph'
            el['value'] = element.text
        elif element.name == 'a':
            el["type"] = 'link'
            el['href'] = element['href']
            el['value'] = element.tex
        elif element.name == 'strong':
            el['type'] = 'strong'
            el['value'] = element.text
        elif element.name == 'img':
            el['type'] = 'image'
            print(element)
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
        pass

    data['article'] = c

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
    get_page("turn-tiktok-sound-into-android-ringtone")
