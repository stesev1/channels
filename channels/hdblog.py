# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# TheGroov360 - XBMC Plugin
# Canale hdblog
# ------------------------------------------------------------

import re
import urlparse

from core import httptools
from platformcode import logger
from core import scrapertools
from core.item import Item

__channel__ = "hdblog"

host = "https://www.hdblog.it"


def mainlist(item):
    logger.info("[thegroove360.hdblog] mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Video recensioni tecnologiche[/COLOR]",
                     action="peliculas",
                     url=host + "/video/",
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/devices.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Categorie[/COLOR]",
                     action="categorias",
                     url=host + "/video/",
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/category.png")]

    return itemlist


def categorias(item):
    logger.info("[thegroove360.hdblog] categorias")
    itemlist = []

    data = httptools.downloadpage(item.url).data
    logger.info(data)

    # Narrow search by selecting only the combo
    start = data.find('<section class="left_toolbar" style="float: left;width: 125px;margin-right: 18px;">')
    end = data.find('</section>', start)
    bloque = data[start:end]

    # The categories are the options for the combo  
    patron = '<a href="([^"]+)"[^>]+><span>(.*?)</span>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedtitle in matches:
        scrapedthumbnail = ""
        scrapedplot = ""
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl + "video/",
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot))

    return itemlist


def peliculas(item):
    logger.info("[thegroove360.hdblog] peliculas")
    itemlist = []

    # Carica la pagina 
    data = httptools.downloadpage(item.url).data

    # Estrae i contenuti 
    patron = '<a class="thumb_new_image" href="([^"]+)">\s*<img[^s]+src="([^"]+)"[^>]+>\s*</a>\s*[^>]+>\s*(.*?)\s*<'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedplot = ""
        itemlist.append(Item(channel=__channel__, action="findvideos", fulltitle=scrapedtitle, show=scrapedtitle,
                             title=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot,
                             folder=True))

    # Paginazione 
    patronvideos = '<span class="attiva">[^>]+>[^=]+="next" href="(.*?)" class="inattiva">'
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
