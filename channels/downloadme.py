# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# TheGroove360 - XBMC Plugin
# Canale downloadme
# ------------------------------------------------------------

import re

from core import httptools, scrapertools
from core.item import Item
from platformcode import logger
from core import servertools
from core.tmdb import infoSod
from servers.decrypters import expurl

__channel__ = "downloadme"

host = "https://downloadme.gratis"

headers = [['Referer', host]]


def mainlist(item):
    logger.info("[thegroove360.downloadme] mainlist")

    # Main options
    itemlist = [Item(channel=__channel__,
                     action="peliculas",
                     title="[COLOR azure]Film[/COLOR]",
                     url="%s/category/film/" % host,
                     extra="movie",
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     action="categorie",
                     title="[COLOR azure]Categorie[/COLOR]",
                     url="%s/" % host,
                     extra="movie",
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca...[/COLOR]",
                     action="search",
                     extra="movie",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search")
                ]

    return itemlist

def peliculas(item):
    logger.info("[thegroove360.downloadme] peliculas")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data
    patron = r'<figure class=[^<]+.*\s.*?data-background=\"([^\"]+)\".*?href=\"([^\"]+)\"></a>.*?<h3.*?\/\">(.*?)</a>'
    matches = re.compile(patron, re.IGNORECASE).findall(data)

    for scrapedthumbnail, scrapedurl, scrapedtitle in matches:
        scrapedtitle = scrapedtitle.split("&#8211;")[0]
        scrapedtitle = scrapedtitle.split(" Download")[0]
        scrapedtitle = scrapedtitle.split(" sub ITA")[0]
        scrapedtitle = scrapedtitle.split(" Streaming")[0]
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title=scrapedtitle,
                 url=scrapedurl,
                 viewmode="movie_with_plot",
                 thumbnail=scrapedthumbnail), tipo="movie"))

    nextpage_regex = '<a class="next page-numbers" href="([^"]+)">'
    next_page = scrapertools.find_single_match(data, nextpage_regex)
    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url="%s" % next_page,
                 extra=item.extra,
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png"))
    return itemlist


def categorie(item):
    logger.info("[thegroove360.downloadme] peliculas")
    itemlist = []

    if item.url == "":
        item.url = host

    data = httptools.downloadpage(item.url, headers=headers).data
    patron = '<li .*? menu-item-type-taxonomy menu-item-object-category menu-item-.*?"><a href="([^"]+)">([^<]+)<\/a><\/li>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title=scrapedtitle,
                 url=scrapedurl,
                 extra=item.extra,
                 viewmode="movie_with_plot",
                 Folder=True))

    return itemlist

def findvideos(item):
    logger.info("[thegroove360.downloadme] findvideos")

    # Carica la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data
    patron = r'<a\s?href=\"([^\"]+)\">LINK DOWNLOAD E STREAMING'
    matches = re.compile(patron, re.IGNORECASE).findall(data)

    from lib.unshortenit import unshorten_only
    urls = ""
    for url in matches:

        resp = httptools.downloadpage(url, follow_redirects=False)
        url = resp.headers.get("location", "")

        uri, status = unshorten_only(url, "adfly")

        if status < 400:
            urls += uri.encode('utf8') + "\n"
        else:
            urls += url.encode('utf8') + "\n"

    itemlist = servertools.find_video_items(data=urls)

    for videoitem in itemlist:
        videoitem.title = item.title + videoitem.title
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.show = item.show
        videoitem.plot = item.plot
        videoitem.channel = __channel__

    return itemlist

def search(item, texto):
    logger.info("[thegroove360.downloadme] " + item.url + " search " + texto)
    item.url = host + "/?s=" + texto
    try:
        if item.extra == "movie":
            return peliculas(item)
    # Continua la ricerca in caso di errore
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []