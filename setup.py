import os
from setuptools import setup

setup(
    name = "simplynews_sites",
    version = "0.0.2",
    url = "https://codeberg.org/SimpleWeb/SimplyNews-Sites",

    license = "AGPLv3 or later",
    keywords = "scraper news simple web",
    packages = ["simplynews_sites", "simplynews_sites/helpers"],
    install_requires = [
        "requests",
        "feedparser",
        "bs4",
        "selenium",
        "lxml",
        "pyvirtualdisplay",
        "colorama",
    ]
)
