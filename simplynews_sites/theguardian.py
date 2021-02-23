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
        "subtitle": soup.select_one("meta[itemprop=description]")["content"],
        "author": page_data["config"]["page"]["author"] or "Reuters",
        "last_updated": soup.select_one(".content__dateline time").text.strip("\n").strip(),
    }

    c = []

    heading_video = soup.select_one(
        "div.media-primary div.youtube-media-atom__iframe")
    if heading_video:
        video_id = heading_video.get("id")
        if video_id:
            video_id = video_id.replace("youtube-", "")
            c.append({
                "type": "iframe",
                "src": "https://www.youtube.com/embed/{}".format(video_id)
            })

    assoc_media = soup.select_one("figure[itemprop='associatedMedia image']")
    if assoc_media and not heading_video:
        image = get_image(assoc_media)
        if image:
            c.append(image)

    for element in soup.find("div", class_="content__article-body"):
        el = {}

        if element.name == "p":
            el["type"] = "paragraph"
            el["value"] = element.text
        elif element.name == "figure":
            image = get_image(element)
            if image is not None:
                c.append(image)
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


def get_image(figure):
    if figure is None:
        return None

    figure_type = figure.get("data-component")
    img = figure.select_one("img")

    src = None
    alt = None

    if figure_type is not None and figure_type == "image":
        src = figure.select_one("meta[itemprop=url]")
        alt = figure.select_one("figcaption")
    elif img is None:
        return None

    if src is not None:
        src = src["content"]  # better quality
    else:
        src = img["src"]

    alt = img.get("alt")

    return {
        "type": "image",
        "src": src,
        "alt": alt
    }


if __name__ == "__main__":

    # page = get_recent_articles()

    # page_url = "world/2021/jan/31/uk-help-eu-not-affect-vaccine-timetable-liz-truss"
    # youtube iframe heading_video

    # page_url = "world/datablog/2021/feb/22/covid-4-million-family-members-grieving-us-study-finds"
    # heading image

    page_url = "global-development/2021/feb/23/revealed-migrant-worker-deaths-qatar-fifa-world-cup-2022"

    page = get_page(page_url)

    print(page)
