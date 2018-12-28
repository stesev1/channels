# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# TheGroove360 - XBMC Plugin
# Canale cinetecadibologna
# ------------------------------------------------------------

import re
import urlparse

from core import config, httptools, scrapertools
from core.item import Item
from platformcode import logger


__channel__ = "cinetecadibologna"

host = "http://cinestore.cinetecadibologna.it"

headers = [['Referer', host]]

def mainlist(item):
    logger.info("[thegroove360.cinetecadibologna] mainlist")
    itemlist = [Item(channel=__channel__, 
                     title="[COLOR azure]Elenco Film - Cineteca di Bologna[/COLOR]", 
                     action="peliculas",
                     url="%s/video/alfabetico_completo" % host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/cinetecabologna.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Epoche - Cineteca di Bologna[/COLOR]",
                     action="epoche",
                     url="%s/video/epoche" % host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/cinetecabologna.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Percorsi Tematici - Cineteca di Bologna[/COLOR]",
                     action="percorsi",
                     url="%s/video/percorsi" % host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/cinetecabologna.png")]

    return itemlist


def peliculas(item):
    logger.info("[thegroove360.cinetecadibologna] peliculas")
    itemlist = []

    # Carica la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data

    # Estrae i contenuti 
    patron = '<img src="([^"]+)"[^>]+>\s*[^>]+>\s*<div[^>]+>\s*<div[^>]+>[^>]+>\s*<a href="([^"]+)"[^>]+>(.*?)<'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedthumbnail, scrapedurl, scrapedtitle in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedthumbnail = host + scrapedthumbnail
        scrapedurl = host + scrapedurl
        if not "/video/" in scrapedurl:
            continue
        html = scrapertools.cache_page(scrapedurl)
        start = html.find("Sinossi:")
        end = html.find('<div class="sx_col">', start)
        scrapedplot = html[start:end]
        scrapedplot = re.sub(r'<[^>]*>', '', scrapedplot)
        scrapedplot = scrapertools.decodeHtmlentities(scrapedplot)
        itemlist.append(Item(channel=__channel__, action="findvideos", fulltitle=scrapedtitle, show=scrapedtitle,
                             title=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot,
                             folder=True))

    # Paginazione 
    patronvideos = '<div class="footerList clearfix">\s*<div class="sx">\s*[^>]+>[^g]+gina[^>]+>\s*[^>]+>\s*<div class="dx">\s*<a href="(.*?)">pagina suc'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url= scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/next_1.png",
                 folder=True))

    return itemlist

def epoche(item):
    logger.info("[thegroove360.cinetecadibologna] categorias")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data

    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data, '<h1 class="pagetitle">Epoche</h1>(.*?)</ul>')

    # The categories are the options for the combo
    patron = '<a href="([^"]+)">(.*?)<'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        scrapedurl = host + scrapedurl
        scrapedplot = ""
        if scrapedtitle.startswith(("'")):
           scrapedtitle = scrapedtitle.replace("'", "Anni '")
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail="http://www.cinetecadibologna.it/pics/cinema-ritrovato-alcinema.png",
                 plot=scrapedplot))

    return itemlist

def percorsi(item):
    logger.info("[thegroove360.cinetecadibologna] categorias")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data

    patron = '<div class="cover_percorso">\s*<a href="([^"]+)">\s*<img src="([^"]+)"[^>]+>\s*[^>]+>(.*?)<'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        scrapedurl = host + scrapedurl
        scrapedplot = ""
        scrapedthumbnail = host + scrapedthumbnail
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot))

    return itemlist

def findvideos(item):
    logger.info("[thegroove360.cinetecadibologna] findvideos")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data

    patron = 'filename: "(.*?)"'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for video in matches:
        video = host + video
        itemlist.append(
            Item(
                channel=__channel__,
                action="play",
                title=item.title + " [[COLOR orange]Diretto[/COLOR]]",
                url=video,
                folder=False))

    return itemlist

