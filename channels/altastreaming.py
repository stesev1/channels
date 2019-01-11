# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# TheGroove360 - XBMC Plugin
# Canale per Dexter Channel
# ------------------------------------------------------------

import re

from core import httptools
from platformcode import logger
from core import scrapertools
from core import servertools
from core.item import Item

__channel__ = "altastreaming"


def mainlist(item):
    logger.info("[thegroove360.altastreaming] mainlist")

    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Dexter Channel - [/COLOR][COLOR orange]I Film[/COLOR]",
                     action="lista",
                     url="https://raw.githubusercontent.com/32Dexter/DexterRepo/master/Dexter%20Channel/Dexter%20Channel.txt",
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/popcorn_cinema_movie_.png",
                     fanart="https://raw.githubusercontent.com/32Dexter/DexterRepo/master/Dexter%20Channel/dexter_wallpaper.jpg")]

    return itemlist


def lista(item):
    logger.info("[thegroove360.altastreaming] lista")

    itemlist = []

    # Scarica la pagina
    data = httptools.downloadpage(item.url).data

    # Estrae i contenuti
    patron = '<a href="(.*?)".*<h1>(.*?)<.*?"(.*?)"'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 title=scrapedtitle,
                 thumbnail=scrapedthumbnail,
                 url=scrapedurl))

    return itemlist


def findvideos(item):
    logger.info("[thegroove360.altastreaming] findvideos")

    # Downloads page
    data = item.url

    itemlist = servertools.find_video_items(data=data)
    for videoitem in itemlist:
        videoitem.title = item.title + "[COLOR orange]" + videoitem.title + "[/COLOR]"
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__

    return itemlist
