# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# TheGroove360 / XBMC Plugin
# Canale 
# ------------------------------------------------------------

import re

from core import httptools, scrapertools, servertools
from core.item import Item
from platformcode import logger

__channel__ = "occhiodelwrestling"

host = "http://www.occhiodelwrestling.netsons.org"


# ----------------------------------------------------------------------------------------------------------------
def mainlist(item):
    logger.info("[OcchioDelWrestling.py]==> mainlist")
    itemlist = [
        Item(
            channel=__channel__,
            action="categorie",
            title=color("Lista categorie", "azure"),
            url=host,
            thumbnail=
            "http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"
        )
    ]

    return itemlist


# ================================================================================================================


# ----------------------------------------------------------------------------------------------------------------
def categorie(item):
    logger.info()
    itemlist = []

    data = data = httptools.downloadpage(item.url).data

    blocco = scrapertools.get_match(
        data, '<div class="menu-main-container">(.*?)</div>')

    patron = r'<li.*?menu-item-\d+"><a href="([^"]+)">([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(blocco)

    for scrapedurl, scrapedtitle in matches:
        itemlist.append(
            Item(
                channel=__channel__,
                action="loaditems",
                title=scrapedtitle,
                url=scrapedurl,
                thumbnail=item.thumbnail,
                folder=True))

    return itemlist


# ================================================================================================================


# ----------------------------------------------------------------------------------------------------------------
def loaditems(item):
    logger.info()
    itemlist = []

    data = data = httptools.downloadpage(item.url).data

    patron = r'<img[^s]+src="([^"]+)" class="[^"]+" alt="([^"]+)"[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+><a href="([^"]+)"[^>]+>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedimg, scrapedtitle, scrapedurl in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(
            Item(
                channel=__channel__,
                action="findvideos",
                title=scrapedtitle,
                fulltitle=scrapedtitle,
                url=scrapedurl,
                thumbnail=scrapedimg,
                folder=True))

    return itemlist


# ================================================================================================================


# ----------------------------------------------------------------------------------------------------------------
def findvideos(item):
    logger.info()
    itemlist = []

    data = data = httptools.downloadpage(item.url).data
    blocco = scrapertools.find_single_match(data, r'<div class="entry-content">(.*?)</div>')
    patron = r'<li><a href="([^"]+)">([^<]+)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    index = 1
    for scrapedurl, scrapedtitle in matches:
        itemlist.append(
            Item(
                channel=__channel__,
                action="play",
                title="Link %s: %s" % (index, scrapedtitle),
                fulltitle=scrapedtitle,
                url=scrapedurl,
                thumbnail=item.thumbnail))
        index += 1
    return itemlist


# ================================================================================================================


# ----------------------------------------------------------------------------------------------------------------
def play(item):
    logger.info()

    itemlist = servertools.find_video_items(data=item.url)

    for videoitem in itemlist:
        videoitem.title = item.show
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__

    return itemlist


# ================================================================================================================


# ----------------------------------------------------------------------------------------------------------------
def color(text, color):
    return "[COLOR " + color + "]" + text + "[/COLOR]"


# ================================================================================================================
