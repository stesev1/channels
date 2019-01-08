# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# TheGroove360 - XBMC Plugin
# Canale per http://www.filmstreaminggratis.org/
# ------------------------------------------------------------

import re

from core import httptools, scrapertools, servertools
from core.item import Item
from core.tmdb import infoSod
from platformcode import logger

__channel__ = "filmstreaminggratis"

host = "https://www.filmstreaminggratis.org"


# ----------------------------------------------------------------------------------------------------------------
def mainlist(item):
    logger.info("[thegroove360.filmstreaminggratis] mainlist")
    itemlist = [Item(channel=__channel__,
                     action="loadfilms",
                     title=color("Ultimi Film", "azure"),
                     url="%s/nuovi/" % host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/popcorn_new.png"),
                Item(channel=__channel__,
                     action="loadfilms",
                     title=color("Nuovi Film", "azure"),
                     url="%s/blog/" % host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/popcorn_new.png"),
                Item(channel=__channel__,
                     action="categorie",
                     title=color("Categorie", "azure"),
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/popcorn_new.png"),
                Item(channel=__channel__,
                     action="search",
                     title=color("Cerca film ...", "yellow"),
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/search_P.png"),
                Item(channel=__channel__,
                     action="loadfilms",
                     title=color("Serie TV", "azure"),
                     url="%s/serie-tv/" % host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/popcorn_new.png"),
                Item(channel=__channel__,
                     action="search",
                     title=color("Cerca Serie TV...", "orange"),
                     extra="serie",
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/search_P.png")
                ]

    return itemlist


# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def newest(categoria):
    logger.info("[thegroove360.filmstreaminggratis] newest" + categoria)
    itemlist = []
    item = Item()
    try:
        if categoria == "peliculas":
            item.url = host
            item.action = "ultimifilm"
            itemlist = ultimifilm(item)

            if itemlist[-1].action == "ultimifilm":
                itemlist.pop()

    # Continua la ricerca in caso di errore 
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist


# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def search(item, texto):
    logger.info("[thegroove360.filmstreaminggratis] search")
    item.url = host + "/?s=" + texto
    try:
        return loadfilms(item)
    # Continua la ricerca in caso di errore 
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def ultimifilm(item):
    logger.info("[thegroove360.filmstreaminggratis] ultimifilm")
    itemlist = []

    data = httptools.downloadpage(item.url).data
    blocco = scrapertools.get_match(data, '<div class="es-carousel">(.*?)</div></li></ul>')
    patron = '<h5><a href="([^"]+)"[^>]+>([^<]+)</a></h5>'
    matches = re.compile(patron, re.DOTALL).findall(blocco)

    for scrapedurl, scrapedtitle in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 contentType="movie",
                 title=scrapedtitle,
                 fulltitle=scrapedtitle,
                 url=scrapedurl,
                 extra="movie",
                 thumbnail=item.thumbnail,
                 folder=True), tipo="movie"))

    return itemlist


# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def categorie(item):
    logger.info("[thegroove360.filmstreaminggratis] categorie")
    itemlist = []

    data = httptools.downloadpage(item.url).data
    blocco = scrapertools.get_match(data, '<div class="list styled custom-list"><ul>(.*?)</ul></div>')
    patron = '<li><a href="([^"]+)" title="[^"]+" >([^<]+)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(blocco)

    for scrapedurl, scrapedtitle in matches:
        if "Serie TV" not in scrapedtitle:  # Il sito non ha una buona gestione per le Serie TV
            itemlist.append(
                Item(channel=__channel__,
                     action="loadfilms",
                     title=scrapedtitle,
                     url=scrapedurl,
                     extra="movie",
                     thumbnail=item.thumbnail,
                     folder=True))

    return itemlist


# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def loadfilms(item):
    logger.info("[thegroove360.filmstreaminggratis] loadfilms")
    itemlist = []

    data = httptools.downloadpage(item.url).data

    patron = '<h2 class="post-title"><a href="([^"]+)" title="[^"]+">'
    patron += '([^<]+)</a></h2>[^>]+>[^>]+>[^>]+><.*?data-src="([^"]+)"'
    patron += '[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>\s+?([^<]+)</div>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, scrapedthumbnail, scrapedplot in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedplot = scrapertools.decodeHtmlentities(scrapedplot.strip())
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 title=scrapedtitle,
                 fulltitle=scrapedtitle,
                 url=scrapedurl,
                 plot=scrapedplot,
                 thumbnail=scrapedthumbnail,
                 folder=True), tipo=item.extra))

    patronvideos = '<link rel="next" href="([^"]+)"\s*/>'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = matches[0]
        itemlist.append(
            Item(channel=__channel__,
                 action="HomePage",
                 title=color("Torna Home", "yellow"),
                 folder=True)),
        itemlist.append(
            Item(channel=__channel__,
                 action="loadfilms",
                 title=color("Successivo >>", "orange"),
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/next_1.png",
                 folder=True))

    return itemlist


# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def findvideos(item):
    logger.info("[thegroove360.filmstreaminggratis] findvideos")

    data = httptools.downloadpage(item.url).data

    if '%s/go/' % host in data:
        urls = scrapertools.find_multiple_matches(data, r'%s/go/[0-9\-]{6}' % host) # Multiple matches con go/9575-2/
        data = ""
        for url in urls:
            data += httptools.downloadpage(url).url

    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        server = re.sub(r'[-\[\]\s]+', '', videoitem.title)
        videoitem.title = "".join(["[%s] " % color(server.capitalize(), 'orange'), item.title])
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__
    return itemlist


# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def color(text, color):
    return "[COLOR " + color + "]" + text + "[/COLOR]"


def HomePage(item):
    import xbmc
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.Stefano)")

# ================================================================================================================
