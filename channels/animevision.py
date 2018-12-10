# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Thegroove360 - XBMC Plugin
# Canale  per http://animevision.altervista.org/
# ------------------------------------------------------------

import re

from core import httptools
from platformcode import logger
from core import scrapertools
from core.item import Item

__channel__ = "animevision"

host = "https://www.animevision.it"

# -----------------------------------------------------------------
def mainlist(item):
    logger.info("[thegroove360.animevision] mainlist")

    itemlist = [Item(channel=__channel__,
                     action="lista_anime",
                     title="[COLOR azure]Anime [/COLOR]- [COLOR orange]Lista Completa[/COLOR]",
                     url=host + "/elenco.php",
                     thumbnail=CategoriaThumbnail,
                     fanart=CategoriaFanart),
                Item(channel=__channel__,
                     action="search",
                     title="[COLOR yellow]Cerca...[/COLOR]",
                     url=host + "/?s=",
                     thumbnail=CategoriaThumbnail,
                     fanart=CategoriaFanart)]

    return itemlist


# =================================================================

# -----------------------------------------------------------------
def search(item, texto):
    logger.info("[thegroove360.animevision] search")
    item.url = host + "/?search=" + texto
    try:
        return lista_anime_src(item)
    # Continua la ricerca in caso di errore 
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

# =================================================================

# -----------------------------------------------------------------
def lista_anime_src(item):
    logger.info("[thegroove360.animevision] lista_anime_src")

    itemlist = []

    data = httptools.downloadpage(item.url).data

    patron = r"<a class=\'false[Ll]ink\'\s*href=\'([^\']+)\'[^>]+>[^>]+>[^<]+<img\s*style=\'[^\']+\'\s*class=\'[^\']+\'\s*src=\'[^\']+\'\s*data-src=\'([^\']+)\'\s*alt=\'([^\']+)\'[^>]*>"
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedimg, scrapedtitle in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedimg = host + "/" + scrapedimg
        scrapedurl = host + "/" + scrapedurl

        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 title=scrapedtitle,
                 url=scrapedurl,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 thumbnail=scrapedimg,
                 fanart=scrapedimg,
                 viewmode="movie"))

    return itemlist


# =================================================================

# -----------------------------------------------------------------
def lista_anime(item):
    logger.info("[thegroove360.animevision] lista_anime")

    itemlist = []

    data = httptools.downloadpage(item.url).data

    patron = "<div class='epContainer' ><a class='falseLink' href='(.*?)'><div[^=]+=[^=]+=[^=]+=[^=]+='(.*?)'[^=]+=[^=]+=[^=]+=[^=]+=[^=]+=[^=]+=[^=]+=[^=]+=[^=]+=[^=]+=[^=]+=[^=]+=[^=]+=[^>]+><b>(.*?)<"
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedimg, scrapedtitle in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedimg = host + "/" + scrapedimg
        scrapedurl = host + "/" + scrapedurl

        itemlist.append(
            Item(channel=__channel__,
                 action="episodi",
                 title=scrapedtitle,
                 url=scrapedurl,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 thumbnail=scrapedimg,
                 fanart=scrapedimg,
                 viewmode="movie"))

    return itemlist


# =================================================================

# -----------------------------------------------------------------
def episodi(item):
    logger.info("[thegroove360.animevision] episodi")
    itemlist = []

    data = httptools.downloadpage(item.url).data

    patron = "<a class='nodecoration text-white' href='(.*?)'>(.+?)<"
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        scrapedtitle = scrapedtitle.split(';')[1]
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedurl = host + "/" + scrapedurl

        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 title=scrapedtitle,
                 url=scrapedurl,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 thumbnail=item.thumbnail,
                 fanart=item.fanart))

    return itemlist


# =================================================================

# =================================================================
# riferimenti di servizio
# -----------------------------------------------------------------
CategoriaThumbnail = "http://static.europosters.cz/image/750/poster/street-fighter-anime-i4817.jpg"
CategoriaFanart = "https://i.ytimg.com/vi/IAlbvyBdYdY/maxresdefault.jpg"
