# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand-pureita.- XBMC Plugin
# Canale italiaserie
# http://www.mimediacenter.info/foro/viewtopic.php?f=36&t=7808
# ------------------------------------------------------------

import re

from core import httptools
from core import logger
from core import config
from core import servertools
from core import scrapertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "italiaserie"
host = "https://italiaserie.org"
headers = [['Referer', host]]

def isGeneric():
    return True

def mainlist(item):
    logger.info("streamondemand-pureita -[italiaserie mainlist]")
    itemlist = [Item(channel=__channel__,
                     action="peliculas",
                     title="[COLOR azure]Serie TV - [COLOR orange]Ultime Aggiunte[/COLOR]",
                     url="%s/category/serie-tv/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/popcorn_serie_P.png"),
               Item(channel=__channel__,
                     action="peliculas",
                     title="[COLOR azure]Serie TV - [COLOR orange]Aggiornamenti[/COLOR]",
                     url="%s/ultimi-episodi/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/tv_series_P.png"),
                Item(channel=__channel__,
                     action="categorie",
                     title="[COLOR azure]Serie TV - [COLOR orange]Categorie[/COLOR]",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genres_P.png"),   
               Item(channel=__channel__,
                     action="peliculas",
                     title="[COLOR azure]Serie TV - [COLOR orange]Animazione[/COLOR]",
                     url="%s/category/serie-tv/animazione-e-bambini/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/animation2_P.png"),
               Item(channel=__channel__,
                     action="peliculas",
                     title="[COLOR azure]Serie TV - [COLOR orange]TV Show[/COLOR]",
                     url="%s/category/serie-tv/tv-show/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/new_tvshows_P.png"),             
                Item(channel=__channel__,
                     action="search",
                     title="[COLOR orange]Search ...[/COLOR]",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png")]

    return itemlist

# ==================================================================================================================================================

def search(item, texto):
    logger.info("streamondemand-pureita - [italiaserie search]")
    item.url = host + "/?s=" + texto
    try:
        return peliculas(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

# ==================================================================================================================================================

def categorie(item):
    logger.info("streamondemand-pureita -[italiaserie categorie]")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data
    blocco = scrapertools.get_match(data, r'<h3 class="title">Categorie</h3>(.*?)</ul>')
	
    patron = r'<li class=".*?"><a href="([^"]+)" >([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(blocco)

    for scrapedurl, scrapedtitle in matches:
        if "Serie TV"  in scrapedtitle or "Tv Show" in scrapedtitle or "Animazione e Bambini" in scrapedtitle:
	    continue
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail='https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genre_P.png',
                 folder=True))

    return itemlist

# ==================================================================================================================================================

def peliculas(item):
    logger.info("streamondemand-pureita -[serietvonline_co peliculas]")
    itemlist = []
    
    data = httptools.downloadpage(item.url, headers=headers).data

    patron = r'<a href="([^"]+)"\s*title="([^"]+)">\s*<img src="([^<]+)"\s*alt[^>]+>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    
    for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle).strip()
        scrapedplot=""
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodes",
                 title=scrapedtitle,
                 fulltitle=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 show=scrapedtitle,
                 folder=True), tipo="tv"))

    next_page = scrapertools.find_single_match(data, '<a class="next page-numbers" href="([^"]+)">Next &raquo;</a>')
    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=next_page,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png"))

    return itemlist

# ==================================================================================================================================================

def episodes(item):
    logger.info("streamondemand-pureita -[italiaserie episodes]")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data

    patron = '<a rel="nofollow"\s*target="_blank" act=".*?"\s*href="([^"]+)"\s*class="green-link">\s*<strong>([^<]+)</strong>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedtitle in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 title=scrapedtitle,
                 fulltitle=item.fulltitle + " - " + scrapedtitle,
                 show=item.show + " - " + scrapedtitle,
                 url=scrapedurl,
                 plot="[COLOR orange]" + item.title + "[/COLOR]" + item.plot,
                 thumbnail=item.thumbnail,
                 folder=True))
    
    return itemlist

# ==================================================================================================================================================

def findvideos(item):
    logger.info()
    data = httptools.downloadpage(item.url).data
    
    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        servername = re.sub(r'[-\[\]\s]+', '', videoitem.title)
        videoitem.title = "".join(['[COLOR azure][[COLOR orange]' + servername.capitalize() + '[/COLOR]] - ', item.title])
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.plot = item.plot
        videoitem.channel = __channel__
    return itemlist

