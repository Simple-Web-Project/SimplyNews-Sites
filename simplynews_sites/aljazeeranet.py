from bs4 import BeautifulSoup
import requests
import json
from datetime import timedelta
import urllib
import feedparser
import re

identifier = "aljazeeranet"
cache_refresh_time_delta = timedelta(hours=12)
base_url = "https://www.aljazeera.net"

site_title = "الجزيرة نت"
site_logo = "aljazeera.svg"
site_dir = "rtl"

rss_feed = f"{base_url}/aljazeerarss/a7c186be-1baa-4bd4-9d80-a84db769f779/73d0e1b4-532f-45ef-b135-bfdff8b8cab9"

# https://www.aljazeera.net/aljazeerarss/a7c186be-1baa-4bd4-9d80-a84db769f779/73d0e1b4-532f-45ef-b135-bfdff8b8cab9


def get_page(url):
    response = requests.get(f"{base_url}/{url}")
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")

    title = soup.findAll(class_='article-header')[0].findAll('h1')[0].text

    content = soup.findAll(class_='wysiwyg')[0]

    article = []

    for figure in soup.findAll('figure'):
        if (re.search(r'class=".*article-featured-image.*?"', str(figure))):
            image = figure.findAll('img')[0]
            article.append({
                'type': 'image',
                'src': base_url + image['src'],
                'alt': image['alt']
            })
            break

    for element in soup.find("div", class_="wysiwyg"):

        if element.name == "p" and len(element.findAll('img')) > 0:
            image = element.findAll('img')[0]
            article.append({
                'type': 'image',
                'src': base_url + image['src'],
                'alt': image['alt']
            })
        elif element.name == 'figure' and len(element.findAll('img')) > 0:
            image = element.findAll('img')[0]
            article.append({
                'type': 'image',
                'src': base_url + image['src'],
                'alt': image['alt']
            })
        elif element.name == "p":
            if len(element.findAll('a')) > 0:
                myList = re.findall(
                    r"(?:(.*)<a.*href=\"(.*)\">(.*)<\/a>(.*)){1,}", "".join([str(x) for x in element.contents]))
                children = []
                for i in range(0, len(myList[0])):
                    if i % 3 == 0:
                        children.append({
                            "type": "paragraph",
                            "value": myList[0][i]
                        })
                    elif i % 3 == 1:
                        children.append({
                            "type": "link",
                            "href": myList[0][i],
                            "value": myList[0][i+1],
                        })
                article.append({
                    "type": "paragraph_advanced",
                    "children": children
                })
            else:
                article.append({
                    "type": "paragraph",
                    "value": element.text,
                })
        elif element.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            article.append({
                "type": "header",
                "size": element.name,
                "value": element.text
            })
            #
        elif element.name == 'blockquote' and not re.search('class=".*twitter-tweet.*?"', str(element)):
            article.append({
                "type": "blockquote",
                "value":  element.text,
            })
        else:
            if element.name is not None:
                print("Ignoring:", element.name)

    source = None
    _source_elements = soup.findAll(class_='article-source')
    if len(_source_elements) > 0:
        source = _source_elements[0].text

    published = soup.findAll(class_='article-dates__published')[0].text

    data = {
        "title": title,
        "author": source,
        "last_updated": published,
        "article": article
    }

    return data

# URL Template:

# players.brightcove.net/665001584001/O36LJRDCG_default/index.html?videoId=6304440613001

# XXXX = Account ID       YYYY = Player ID    ZZZZ = Video ID


def get_recent_articles():
    feed = feedparser.parse(rss_feed)
    feed_ = []
    for entry in feed["entries"][:10]:
        url = urllib.parse.urlparse(entry["link"])

        local_link = url.path.strip("/")  # Kill annoying slashes

        r = requests.get(entry['link'])
        soup = soup = BeautifulSoup(r.text, "lxml")

        choosenImage = None
        for figure in soup.findAll('figure'):
            if (re.search(r'class=".*article-featured-image.*?"', str(figure))):
                image = figure.findAll('img')[0]
                choosenImage = base_url + image['src']
                break

        feed_.append({
            "title": entry["title"],
            "link": local_link,
            "image": choosenImage,
            "date": entry['published'],
        })
    return feed_


if __name__ == "__main__":

    page = get_recent_articles()
    # https://www.aljazeera.net/midan/reality/politics/2022/4/20/%D8%B9%D9%88%D8%AF%D8%A9-%D8%A7%D9%84%D8%BA%D8%B2%D9%88-%D8%A7%D9%84%D8%AA%D9%88%D8%B3%D9%91%D9%8F%D8%B9%D9%8A-%D9%87%D9%84-%D8%AA%D8%AA%D9%81%D8%AC%D9%91%D9%8E%D8%B1-%D8%AD%D8%B1%D9%88%D8%A8
    # page_url = "videos/2022/4/20/%D8%A3%D8%AC%D9%88%D8%A7%D8%A1-%D8%B4%D9%87%D8%B1-%D8%B1%D9%85%D8%B6%D8%A7%D9%86-%D9%81%D9%8A-%D9%85%D8%AF%D9%8A%D9%86%D8%A9-%D8%A3%D8%B1%D8%A8%D9%8A%D9%84-%D8%A8%D8%A5%D9%82%D9%84%D9%8A%D9%85"
    # page = json.dumps(get_page(page_url), ensure_ascii=False, indent=2)

    # https://www.aljazeera.net/wp-content/uploads/2022/04/RTXKARMC.jpg?resize=770%2C513
    # print(page)
