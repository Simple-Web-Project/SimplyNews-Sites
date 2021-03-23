from .helpers import rss, utils
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

    # ignore The Conversation's pixel tracking
    if "count.gif" in src:
        return None

    return {
        "type": "image",
        "src": src,
        "alt": img.get("alt") or img.get("title")
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
    response = requests.get(f"{base_url}/{url}")
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")

    title = soup.select_one("title").text
    subtitle = soup.select_one("meta[name=description]")["content"]
    subtitle = unescape(subtitle)

    json_element = soup.find("script", type="application/ld+json")
    if json_element:
        info_json = json.loads(json_element.next)

    post = soup.select_one("article")

    authors = []
    author_group = None

    aside = post.select_one("aside")

    if aside:
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
        # last in the list
        last_updated = dates[-1].text

        author_list = post.select_one("div.c-signature__authors")
        for author in author_list.select(".c-signature__names"):
            authors.append(author.text)

        author_group = author_list.select_one(
            ".c-signature__group-team-wrapper").text

        heading_image = post.select_one("div.c-cover figure img")

        post_content = post.select_one("div.c-body")

    author = ", ".join(authors)
    if author_group:
        author = "{} ({})".format(author, author_group.strip(" \n"))

    data = {
        "title": title,
        "subtitle": subtitle,
        "author": author,
        "last_updated": last_updated
    }

    article = []

    if heading_image:
        article.append(get_image(heading_image))

    heading_video = post.select_one("figure.video")
    if heading_video:
        iframe_element = heading_video.select_one("iframe")
        iframe = get_iframe(iframe_element)
        if iframe:
            article.append(iframe)

    heading_video = post.select_one("figure.player-video")
    if heading_video:
        if info_json and "video" in info_json:
            video = info_json["video"]

            if isinstance(video, list):
                video = video[0]

            article.append({
                "type": "iframe",
                "src": video["embedURL"],
                "width": video["width"]["value"],
                "height": video["height"]["value"]
            })

        # else: embedded live stream, but it's not using iframe and blob src url for <video> then hard to extract

    for element in post_content:
        el = {}

        if element.name == "p":
            iframe = element.select_one("iframe")
            img = element.select_one("img")
            if iframe:
                el["type"] = "iframe"
                el["src"] = iframe["src"]
                style = iframe.get("style")
                if style:
                    styles = style.split(";")
                    for value in styles:
                        stripped = value.strip(" ;")
                        if stripped.startswith("height:"):
                            el["height"] = stripped.replace("height: ", "")
            elif img:
                el = get_image(img)

            elif ">>" not in element.text:  # ignore related article links
                el["type"] = "paragraph"
                el["value"] = element.text

        elif element.name == "blockquote":
            el["type"] = "blockquote"
            el["value"] = element.text
            if utils.value_in_element_attr(element, "twitter-tweet"):
                article.append(el)
                links = element.select("a")
                for link in links:
                    el = {
                        "type": "link",
                        "href": link["href"],
                        "value": link.text
                    }
                    article.append(el)

                el = {}

        elif element.name == "span":
            el["type"] = "paragraph"
            el["value"] = element.text

        elif element.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            el["type"] = "header"
            el["size"] = element.name
            el["value"] = element.text

        elif element.name == "figure":
            iframe = get_iframe(element.select_one("iframe"))
            if iframe:
                el = iframe

        elif element.name == "ul":
            el["type"] = "unsorted list"
            entries = []
            for entry in element:
                if entry.name == "li":
                    entries.append({"value": entry.text})
            el["entries"] = entries

        if el:
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

    # page_url = "sante/maladie/coronavirus/confinement/alpes-maritimes-les-mesures-envisagees-par-le-gouvernement-face-a-l-envolee-des-cas-decovid-19_4305859.html"
    # heading_video, akamaidh iframe

    # page_url = "sciences/mars-curiosity/premier-son-capte-sur-mars-le-concepteur-d-un-des-micros-de-perseverance-explique-pourquoi-il-est-important-d-ecouter-la-planete-rouge_4308091.html"
    # twitter blockquote

    # Franceinfo (tv) livestream embedded (endend and shows replay now)
    # page_url = "sante/maladie/coronavirus/direct-covid-19-jean-castex-va-s-exprimer-a-18-heures-au-sujet-de-la-dizaine-de-departements-juges-preoccupants_4310813.html"

    # page_url = "sante/maladie/coronavirus/carte-covid-19-decouvrez-les-20-departements-places-en-surveillance-renforcee_4310887.html"
    # iframe

    # page_url = "sante/maladie/coronavirus/infographies-covid-19-cinq-graphiques-pour-comprendre-la-situation-epidemique-en-france_4310757.html"
    # infographies

    # page_url = "sante/maladie/coronavirus/vaccin/video-covid-19-les-plus-de-65-ans-pourront-se-faire-vacciner-a-partir-de-debut-avril-assure-jean-castex_4310939.html"
    # multiple videos in json

    # page_url = "sante/maladie/coronavirus/covid-19-le-passeport-vaccinal-evoque-par-la-commission-europeenne-est-il-juridiquement-possible_4317149.html"
    # The Conversation pixel tracking

    page_url = "sante/maladie/coronavirus/confinement/dedans-avec-les-miens-dehors-en-citoyen-la-campagne-de-communication-du-gouvernement-sur-les-gestes-barrieres-devoilee-par-jean-castex_4343313.html"
    # ul

    page = get_page(page_url)

    print(page)
