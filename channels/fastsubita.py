# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# TheGroove360 - XBMC Plugin
# Canale  per fastsubita
# ------------------------------------------------------------

import re
import urlparse

from core import config
from core import httptools
from core import scrapertools
from core import servertools
from core.item import Item
from core.tmdb import infoSod
from platformcode import logger

__channel__ = "fastsubita"

host = "http://fastsubita.gq"

headers = [
    ['Host', 'fastsubita.gq'],
    ['User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0'],
    ['Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'],
    ['Accept-Language', 'en-US,en;q=0.5'],
    ['Accept-Encoding', 'gzip, deflate'],
    ['Referer', host],
    ['DNT', '1'],
    ['Connection', 'keep-alive'],
    ['Upgrade-Insecure-Requests', '1'],
    ['Cache-Control', 'max-age=0']
]

PERPAGE = 14


def mainlist(item):
    logger.info("[thegroove360.fastsubita] mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Aggiornamenti[/COLOR]",
                     action="serietv",
                     extra='serie',
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/movie_new_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Tutte le Serie TV[/COLOR]",
                     action="all_quick",
                     extra='serie',
                     url="%s/tutte-le-serie-tv/" % host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/movie_new_P.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca...[/COLOR]",
                     action="search",
                     extra='serie',
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/search_P.png")]

    return itemlist


def newest(categoria):
    logger.info("[thegroove360.fastsubita]==> newest" + categoria)
    itemlist = []
    item = Item()
    try:
        if categoria == "series":
            item.url = host
            item.action = "serietv"
            itemlist = serietv(item)

            if itemlist[-1].action == "serietv":
                itemlist.pop()

    # Continua la ricerca in caso di errore 
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist


def serietv(item):
    logger.info("[thegroove360.fastsubita] peliculas")
    itemlist = []

    # Carica la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data

    # Estrae i contenuti 
    patron = '<h3 class="entry-title title-font"><a href="([^"]+)" rel="bookmark">(.*?)<'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        scrapedplot = ""
        scrapedthumbnail = ""
        scraped_1 = scrapedtitle.split("&#215;")[0][:-2]
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedtitle = scrapedtitle.replace(scraped_1, "")

        if "http:" in scrapedurl:
            scrapedurl = scrapedurl
        else:
            scrapedurl = "http:" + scrapedurl

        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 contentSerieName=scraped_1 + scrapedtitle,
                 fulltitle=scraped_1,
                 show=scraped_1,
                 title="[COLOR azure]" + scraped_1 + "[/COLOR]" + " " + scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 extra=item.extra,
                 folder=True), tipo='tv'))

    # Paginazione 
    patronvideos = '<a class="next page-numbers" href="(.*?)">Successivi'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="HomePage",
                 title="[COLOR yellow]Torna Home[/COLOR]",
                 folder=True)),
        itemlist.append(
            Item(channel=__channel__,
                 action="serietv",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/next_1.png",
                 extra=item.extra,
                 folder=True))

    return itemlist


def all_quick(item):
    logger.info("[thegroove360.fastsubita] peliculas")
    itemlist = []

    p = 1
    if '{}' in item.url:
        item.url, p = item.url.split('{}')
        p = int(p)

    # Carica la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data

    # Estrae i contenuti 
    patron = '<a href="([^"]+)"[^>]+>[^<]+<\/a>\s*<\/li>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for i, (scrapedurl) in enumerate(matches):
        if (p - 1) * PERPAGE > i: continue
        if i >= p * PERPAGE: break
        scrapedplot = ""
        scrapedthumbnail = ""
        scrapedtitle = scrapedurl
        scrapedtitle = scrapedtitle.replace("%s/serietv/" % host, "")
        scrapedtitle = scrapedtitle.replace("/", "")
        scrapedtitle = scrapedtitle.replace("-", " ")
        scrapedtitle = scrapedtitle.title()

        if "http:" in scrapedurl:
            scrapedurl = scrapedurl
        else:
            scrapedurl = "http:" + scrapedurl

        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="serietv",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 extra=item.extra,
                 folder=True), tipo='tv'))

    if len(matches) >= p * PERPAGE:
        scrapedurl = item.url + '{}' + str(p + 1)
        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="all_quick",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/next_1.png",
                 folder=True))

    return itemlist

def findvideos(item):
    logger.info("[thegroove360.fastsubita] findvideos")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data
    bloque = scrapertools.get_match(data, '<div class="entry-content">(.*?)<footer class="entry-footer">')

    patron = '<a href="([^"]+)">'
    matches = re.compile(patron, re.DOTALL).findall(bloque)
    for scrapedurl in matches:
        if 'is.gd' in scrapedurl:
            resp = httptools.downloadpage(
                 scrapedurl, follow_redirects=False)
            data += resp.headers.get("location", "")


    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        videoitem.title = item.title + videoitem.title
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.show = item.show
        videoitem.plot = item.plot
        videoitem.channel = __channel__

    return itemlist


def search(item, texto):
    logger.info("[thegroove360.fastsubita] " + item.url + " search " + texto)
    item.url = "%s/?s=%s" % (host, texto)
    try:
        return serietv(item)
    # Continua la ricerca in caso di errore 
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

def HomePage(item):
    import xbmc
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.stefano)")
