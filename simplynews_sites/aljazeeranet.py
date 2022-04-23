from bs4 import BeautifulSoup
import requests
import json
from datetime import timedelta
import urllib
import feedparser
import re
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from colorama import Fore, Back, Style
from pyvirtualdisplay import Display

identifier = "aljazeera.net"
cache_refresh_time_delta = timedelta(hours=12)
base_url = "https://www.aljazeera.net"

site_title = "الجزيرة نت"
site_logo = "aljazeera.webp"
site_dir = "rtl"

rss_feed = f"{base_url}/aljazeerarss/a7c186be-1baa-4bd4-9d80-a84db769f779/73d0e1b4-532f-45ef-b135-bfdff8b8cab9"

profile = webdriver.FirefoxProfile()

profile.set_preference("general.useragent.override",
                       "Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/537.36 (KHTML, like Gecko; Mediapartners-Google) Chrome/89.0.4389.130 Mobile Safari/537.36")

display = Display(visible=0, size=(800, 600))
display.start()
driver = webdriver.Firefox(profile, executable_path='./drivers/geckodriver')

# https://www.aljazeera.net/aljazeerarss/a7c186be-1baa-4bd4-9d80-a84db769f779/73d0e1b4-532f-45ef-b135-bfdff8b8cab9


def get_page(url):
    driver.get(f"{base_url}/{url}")
    time.sleep(3)

    title = driver.find_element(
        By.CLASS_NAME, 'article-header').find_element(By.TAG_NAME, 'h1').text

    article = []

    try:
        video = driver.find_element(
            By.CLASS_NAME, 'article-featured-video'
        ).find_element(
            By.XPATH,
            '//video[@class="vjs-tech"]')
        article.append({
            "type": "video",
            "src": video.get_attribute("src"),
        })
    except:
        try:
            video = driver.find_element(
                By.CLASS_NAME, 'article__featured-video'
            ).find_element(
                By.XPATH,
                '//video[@class="vjs-tech"]')
            article.append({
                "type": "video",
                "src": video.get_attribute("src"),
            })
        except:
            pass

    for figure in driver.find_elements(By.XPATH, '//figure[@class="article-featured-image"]'):
        image = figure.find_element(By.TAG_NAME, 'img')
        article.append({
            'type': 'image',
            'src': image.get_attribute('src'),
            'alt': image.get_attribute('alt')
        })
        break

    _article_excerpt = driver.find_elements(By.CLASS_NAME, 'article-excerpt')
    if len(_article_excerpt) > 0 and _article_excerpt[0].text.strip() != '':
        article.append({
            "type": "paragraph",
            "value": _article_excerpt[0].text
        })

    for element in driver.find_element(By.CLASS_NAME, 'wysiwyg').find_elements(By.XPATH, ".//*"):
        if element.tag_name == "p" and len(element.find_elements(By.TAG_NAME, 'img')) > 0:
            image = element.find_elements(By.TAG_NAME, 'img')[0]
            article.append({
                'type': 'image',
                'src': base_url + image.get_attribute('src'),
                'alt': image.get_attribute('alt')
            })
        elif element.tag_name == 'figure':
            images = element.find_elements(By.TAG_NAME, 'img')
            if len(images) > 0:
                article.append({
                    'type': 'image',
                    'src': images[0].get_attribute('src'),
                    'alt': images[0].get_attribute('alt')
                })
            video = element.find_elements(By.CLASS_NAME, 'vjs-tech')
            if len(video) > 0:
                article.append({
                    'type': 'video',
                    "src": video[0].get_attribute("src"),
                })
        elif element.tag_name == "p":
            if len(element.find_elements(By.TAG_NAME, 'a')) > 0:
                # "".join([str(x) for x in element.contents]))
                myList = re.findall(
                    r"(?:(.*)<a.*href=\"(.*)\">(.*)<\/a>(.*)){1,}",
                    element.get_attribute('innerHTML')
                )
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
        elif element.tag_name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            article.append({
                "type": "header",
                "size": element.tag_name,
                "value": element.text
            })
        elif element.tag_name == 'div' and 'twitter-tweet' in element.get_attribute("class").split():
            article.append({
                "type": "iframe",
                "src":  element.find_element(By.TAG_NAME, 'iframe').get_attribute('src').replace('platform.twitter.com', 'nitter.pussthecat.org'),
                "width": 500,
                "height": 500
            })
        elif element.tag_name == 'div' and 'jetpack-video-wrapper' in element.get_attribute("class").split():
            article.append({
                "type": "iframe",
                "src":  element.find_element(By.TAG_NAME, 'iframe').get_attribute('src'),
                "width": 770,
                "height": 434,
            })
        elif element.tag_name == 'blockquote':
            article.append({
                "type": "blockquote",
                "value":  element.text,
            })

    source = None
    _source_elements = driver.find_elements(By.CLASS_NAME, 'article-source')
    if len(_source_elements) > 0:
        source = _source_elements[0].text

    published = driver.find_element(
        By.CLASS_NAME, 'article-dates__published').text

    data = {
        "title": title,
        "author": source,
        "last_updated": published,
        "article": article
    }
    print(Fore.GREEN + 'Fetched ' + Style.RESET_ALL +
          f"{base_url}/{urllib.parse.unquote(url)}")

    return data


def get_recent_articles():
    feed = feedparser.parse(rss_feed)
    feed_ = []
    for entry in feed["entries"]:
        url = urllib.parse.urlparse(entry["link"])

        local_link = url.path.strip("/")  # Kill annoying slashes

        r = requests.get(entry['link'])
        soup = BeautifulSoup(r.text, "lxml")

        choosenImage = None
        for figure in soup.findAll('figure'):
            if (re.search(r'class=".*article-featured-image.*?"', str(figure))):
                image = figure.findAll('img')[0]
                choosenImage = base_url + image['src']
                break

        article_video = soup.findAll(
            class_='article-featured-video')
        if len(article_video) > 0:
            vjs_tech = article_video[0].findAll(class_='vjs-tech')
            if len(vjs_tech) > 0:
                chosenImage = vjs_tech[0].get_attribute("poster")
        else:
            article_video = soup.findAll(
                class_='article__featured-video')
            if len(article_video) > 0:
                vjs_tech = article_video[0].findAll(class_='vjs-tech')
                if len(vjs_tech) > 0:
                    chosenImage = vjs_tech[0].get_attribute("poster")

        feed_.append({
            "title": entry["title"],
            "link": local_link,
            "image": choosenImage,
            "date": entry['published'],
        })
    print(Fore.GREEN + 'Fetched ' + Style.RESET_ALL +
          f'{base_url}/{urllib.parse.unquote(rss_feed)}')
    return feed_


if __name__ == "__main__":

    # page = get_recent_articles()
    # https://www.aljazeera.net/midan/reality/politics/2022/4/20/%D8%B9%D9%88%D8%AF%D8%A9-%D8%A7%D9%84%D8%BA%D8%B2%D9%88-%D8%A7%D9%84%D8%AA%D9%88%D8%B3%D9%91%D9%8F%D8%B9%D9%8A-%D9%87%D9%84-%D8%AA%D8%AA%D9%81%D8%AC%D9%91%D9%8E%D8%B1-%D8%AD%D8%B1%D9%88%D8%A8
    page_url = "videos/2022/4/21/%D8%AA%D8%B9%D8%B1%D9%81-%D8%B9%D9%84%D9%89-%D8%AE%D8%B1%D9%8A%D8%B7%D8%A9-%D8%A7%D9%84%D9%85%D9%88%D8%A7%D9%82%D8%B9-%D8%A7%D9%84%D9%86%D9%88%D9%88%D9%8A%D8%A9"
    page = json.dumps(get_page(page_url), ensure_ascii=False, indent=2)
    # https://www.aljazeera.net/wp-content/uploads/2022/04/RTXKARMC.jpg?resize=770%2C513
    # print(page)
