# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# TheGroove360 / XBMC Plugin
# Canale 
# ------------------------------------------------------------
import re
import urlparse

from core import httptools
from platformcode import logger
from core import scrapertools
from core.item import Item

__channel__ = "ricettevideo"

host = "http://ricettevideo.net"


def mainlist(item):
    logger.info("Stefano.ricettevideo mainlist")
    itemlist = [Item(channel=__channel__, title="[COLOR azure]Videoricette[/COLOR]", action="peliculas",
                     url=host,
                     thumbnail="http://www.brinkmanscountrycorner.com/images/Recipies.png")]

    return itemlist


def peliculas(item):
    logger.info("Stefano.ricettevideo peliculas")
    itemlist = []

    # Carica la pagina 
    data = httptools.downloadpage(item.url).data

    # Estrae i contenuti 
    patron = '<div class="post-item-small">\s*<a href="([^"]+)"[^t]+title="Permanent Link: ([^"]+)"><img[^s]+src="([^"]+)"[^>]+>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedplot = ""
        itemlist.append(Item(channel=__channel__, action="findvideos", fulltitle=scrapedtitle, show=scrapedtitle,
                             title=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot,
                             folder=True))

    # Paginazione 
    patronvideos = '<link rel=\'next\' href=\'([^\']+)\' />'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__, action="HomePage", title="[COLOR yellow]Torna Home[/COLOR]", folder=True))
        itemlist.append(
            Item(channel=__channel__, action="peliculas", title="[COLOR orange]Avanti >>[/COLOR]", url=scrapedurl,
                 folder=True))

    return itemlist


def HomePage(item):
    import xbmc
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.Stefano)")

# test update
