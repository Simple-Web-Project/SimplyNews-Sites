from bs4 import BeautifulSoup
import requests
from datetime import timedelta
from .helpers import rss

cache_refresh_time_delta = timedelta(hours=12)
identifier = "shacknews"
base_url = "https://shacknews.com"

site_title = "Shack News"

rss_feed = f"{base_url}/feed/rss"


def get_page(url):
    full_url = f"{base_url}/" + url
    soup = BeautifulSoup(requests.get(full_url).text, "lxml")

    data = {
        'title': soup.find('h1', class_='article-title').text,
        'subtitle': soup.find('div', class_='article-lead-bottom-content').find('description').text,
        'author': soup.find('div', class_='article-lead-bottom').find('div', class_='by-line').find('a').text,
        'last_updated': soup.find('div', class_='time-stamp').text
    }

    c = []

    for element in soup.find('section', class_='article-content').find('main'):
        el = {}
        if element.name == 'p':
            vid = element.find('iframe')
            if vid is not None:
                print()
                el['type'] = 'iframe'
                el['src'] = vid['src']
            else:
                el['type'] = 'paragraph'
                el['value'] = element.text
        elif element.name == 'blockquote':
            el["type"] = "blockquote"
            el['value'] = element.text
        elif element.name in ("h1", 'h2', 'h3', 'h4', 'h5', 'h6'):
            el['type'] = 'header'
            el['size'] = element.name
            el['value'] = element.text
        else:
            if element.name is not None:
                print("Ignoring:", element.name)
            el = None

        if el is not None:
            c.append(el)
            
    data['article'] = c

    return data


def get_recent_articles():
    return rss.default_feed_parser(rss_feed)


if __name__ == "__main__":
    print(get_recent_articles())
    #get_page("2021/01/30/john-chaneys-kindness-wont-be-forgotten/")
