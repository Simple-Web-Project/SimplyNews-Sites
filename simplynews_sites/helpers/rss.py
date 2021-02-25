import feedparser
import urllib
from .. import links


def default_feed_parser(feed_link):
    feed = feedparser.parse(feed_link)
    feed_ = []
    for entry in feed["entries"]:
        url = urllib.parse.urlparse(entry["link"])
        if url.hostname in links.sites:
            local_link = url.path.strip("/")  # Kill annoying slashes

            feed_.append({
                "title": entry["title"],
                "link": local_link,
            })
    return feed_
