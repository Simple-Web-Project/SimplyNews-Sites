from .helpers import rss
from datetime import timedelta
from bs4 import BeautifulSoup
from html import unescape
import requests
import json

cache_refresh_time_delta = timedelta(hours=3)
identifier = "franceinfo"
site_title = "Franceinfo"

base_url = "https://www.francetvinfo.fr"

rss_feed = f"{base_url}/titres.rss"


def get_image(img):
    if img is None:
        return None

    if "data-src" in img.attrs:
        src = "{}{}".format(base_url, img["data-src"])
    else:
        src = img["src"]

    return {
        "type": "image",
        "src": src,
        "alt": img["alt"]
    }


def get_iframe(iframe):
    if iframe is None:
        return None

    el = {}

    if "data-src" in iframe.attrs:
        src = iframe["data-src"]
    else:
        src = iframe["src"]

    el["type"] = "iframe"
    el["src"] = src
    el["width"] = iframe.get("width")
    el["height"] = iframe.get("height")
    return el


def get_page(url):
    full_url = f"{base_url}/{url}"

    response = requests.get(full_url)

    soup = BeautifulSoup(response.text, "lxml")

    title = soup.select_one("title").text
    subtitle = soup.select_one("meta[name=description]")["content"]
    subtitle = unescape(subtitle)

    json_element = soup.find("script", type="application/ld+json")
    if json_element is not None:
        info_json = json.loads(json_element.next)

    post = soup.select_one("article")

    authors = []
    author_group = None

    aside = post.select_one("aside")

    if aside is not None:
        aside = post.select_one("aside")

        publish_date = aside.select_one("p.publish-date")
        # there are two <time> in this object, the first one is last_updated, the second one is the original publish date
        last_updated = publish_date.select_one("time").text

        author_list = aside.select_one("div.authors-list")
        for author in author_list.select(".author"):
            authors.append(author.text)

        author_group = author_list.select_one(".group").text

        heading_image = post.select_one("div.left-wrapper > figure img")

        post_content = post.select_one("div.text")

    else:
        publish_date = post.select_one("div.publication-date")
        # there are two dates in this object, the first one is the publish date, the second one is the last_updated
        dates = publish_date.select("time")
        if len(dates) == 1:
            last_updated = dates.text
        else:
            last_updated = dates[1].text

        author_list = post.select_one("div.c-signature__authors")
        for author in author_list.select(".c-signature__names"):
            authors.append(author.text)

        author_group = author_list.select_one(
            ".c-signature__group-team-wrapper").text

        heading_image = post.select_one("div.c-cover figure img")

        post_content = post.select_one("div.c-body")

    author = ", ".join(authors)
    if author_group is not None:
        author = "{} ({})".format(author, author_group)

    data = {
        "title": title,
        "subtitle": subtitle,
        "author": author,
        "last_updated": last_updated
    }

    article = []

    if heading_image is not None:
        article.append(get_image(heading_image))

    heading_video = post.select_one("figure.video")
    if heading_video is not None:
        iframe_element = heading_video.select_one("iframe")
        iframe = get_iframe(iframe_element)
        if iframe is not None:
            article.append(iframe)

    heading_video = post.select_one("figure.player-video")
    if heading_video is not None and info_json is not None:
        video = info_json["video"]

        article.append({
            "type": "iframe",
            "src": video["embedURL"],
            "width": video["width"]["value"],
            "height": video["height"]["value"]
        })

    for element in post_content:
        el = {}

        if element.name == "p":
            if ">>" not in element.text:  # ignore related article links
                el["type"] = "paragraph"
                el["value"] = element.text

        elif element.name == "blockquote":
            el["type"] = "blockquote"
            el["value"] = element.text

        elif element.name == "span":
            el["type"] = "paragraph"
            el["value"] = element.text

        elif element.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            el["type"] = "header"
            el["size"] = element.name
            el["value"] = element.text

        elif element.name == "figure":
            iframe = get_iframe(element.select_one("iframe"))
            if iframe is not None:
                el = iframe

        if el is not None and el != {}:
            article.append(el)

    data["article"] = article
    return data


def get_recent_articles():
    return rss.default_feed_parser(rss_feed)


if __name__ == "__main__":
    # page = get_recent_articles()

    # page_url = "sante/maladie/coronavirus/vaccin/direct-covid-19-la-vaccination-accelere-mais-reste-inegale-entre-les-pays-riches-et-pauvres_4305451.html"
    # "live" article, multiple authors

    # page_url = "sante/maladie/coronavirus/covid-19-le-medecin-jerome-marty-appelle-a-des-frappes-chirurgicales-contre-lepidemie-avec-des-mesures-localisees_4305769.html"
    # blockquote

    # page_url = "sante/maladie/coronavirus/video-covid-19-ne-venez-pas-ce-n-est-pas-le-moment-lance-aux-touristes-christian-estrosi-le-maire-de-nice_4305491.html"
    # heading_video, dailymotion iframe

    # page_url = "sante/maladie/coronavirus/covid-19-le-masque-en-creche-gene-t-il-la-sociabilisation-des-tout-petits_4303509.html"
    # YouTube iframe

    page_url = "sante/maladie/coronavirus/confinement/alpes-maritimes-les-mesures-envisagees-par-le-gouvernement-face-a-l-envolee-des-cas-decovid-19_4305859.html"
    # heading_video, akamaidh iframe

    page = get_page(page_url)

    print(page)
