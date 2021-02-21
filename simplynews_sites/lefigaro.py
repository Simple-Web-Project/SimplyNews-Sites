from .helpers import rss
from datetime import timedelta
from bs4 import BeautifulSoup
import requests

import feedparser
import urllib

cache_refresh_time_delta = timedelta(hours=3)
identifier = "lefigaro"
site_title = "Le Figaro"

base_url = "https://www.lefigaro.fr"
rss_feed = f"{base_url}/rss/figaro_actualites.xml"


def get_image(img):
    return {
        "type": "image",
        "src": img["data-srcset"].split()[0],
        "alt": img["alt"]
    }


def get_page(url):
    full_url = f"{base_url}/{url}"

    response = requests.get(full_url)

    # handle bad response - see #4
    if response.status_code >= 400:
        error = "Error - HTTP {} : {}".format(
            response.status_code, response.reason)

        return {
            "title": error,
            "author": site_title,
            "last_updated": "Unknown",
            "article": [
                {
                    "type": "paragraph",
                    "value": error
                }
            ]
        }

    soup = BeautifulSoup(response.text, "lxml")

    title = soup.select_one("title").text
    subtitle = soup.select_one("meta[name=description]")["content"]

    post = soup.select_one("article")

    if subtitle.endswith("..."):
        standfirst = post.select_one("p.fig-standfirst")
        if standfirst is not None:
            subtitle = standfirst.text

    meta_info = post.select_one("div.fig-content-metas-info")
    author = meta_info.select_one("span.fig-content-metas__authors").text
    last_updated = meta_info.select_one(
        "span.fig-content-metas__pub-maj-date > time")

    if last_updated is None:  # It hasn't been updated, then we get published date
        last_updated = meta_info.select_one(
            "span.fig-content-metas__pub-date > time")

    last_updated = last_updated.text

    data = {
        "title": title,
        "subtitle": subtitle,
        "author": author,
        "last_updated": last_updated
    }

    article = []

    heading_image = post.select_one("article > figure.fig-media img")
    if heading_image is not None:
        article.append(get_image(heading_image))

    post_content = post.select_one("div.fig-body")

    if post_content is None:  # not an article
        poll_element = post.select_one("div.fig-poll")
        if poll_element is not None:
            entries = []
            results = poll_element.select("div.fig-poll__result")
            for result in results:
                percentage = result.get("data-percentage")
                label = result.select_one("span.fig-poll__label").text

                entries.append({"value": "{} : {}%".format(label, percentage)})

            el = {
                "type": "unsorted list",
                "entries": entries
            }

            article.append(el)

        data["article"] = article
        return data

    for element in post_content:
        el = {}
        if element.name == "p" and 'fig-paragraph' in element.attrs.get("class"):
            strong = element.select_one("strong")
            if strong is None or not strong.text.startswith("À voir aussi"):
                el["type"] = "paragraph"
                el["value"] = element.text
        elif element.name == "div" and "fig-premium-paywall" in element.attrs.get("class"):
            # paywall. Display info (% left) without info encouraging to subscribe
            info = element.select_one("p.fig-premium-paywall__infos")
            if info is not None:
                el["type"] = "paragraph"
                el["value"] = info.text
        elif element.name == "figure":
            img = element.select_one("img")
            if img is not None:
                article.append(get_image(img))
        elif element.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            el["type"] = "header"
            el["size"] = element.name
            el["value"] = element.text

        if el is not None and el != {}:
            article.append(el)

    data["article"] = article
    return data


def get_recent_articles():
    feed = feedparser.parse(rss_feed)
    feed_ = []
    for entry in feed["entries"]:
        url = urllib.parse.urlparse(entry["link"])

        if url.hostname == "www.lefigaro.fr":  # ignore subdomains
            local_link = url.path.strip("/")  # Kill annoying slashes
            feed_.append({
                "title": entry["title"],
                "link": local_link,
            })

    return feed_


if __name__ == "__main__":
    page_url = "politique/menu-sans-viande-dans-les-cantines-de-lyon-darmanin-denonce-la-mesure-doucet-lui-repond-20210221"

    # page_url = "flash-actu/libye-le-ministre-de-l-interieur-echappe-a-une-tentative-d-assassinat-20210221"
    # not updated (yet)

    # page_url = "actualite-france/approuvez-vous-la-decision-du-maire-de-lyon-d-imposer-un-menu-sans-viande-dans-les-ecoles-20210221"
    # poll

    # page_url = "finances-perso/transmission-de-votre-patrimoine-immobilier-les-solutions-pour-alleger-la-facture-20210219"
    # paywall

    # page_url = "culture/les-mysteres-du-coffre-cache-depuis-le-xixe-siecle-dans-le-socle-d-une-statue-de-napoleon-a-rouen-20210221"
    # image, headers…

    # page_url = "vox/societe/didier-lemaire-a-trappes-nous-ne-sommes-plus-en-france-20210219"
    # subtitle cut

    page = get_page(page_url)
    print(page)
