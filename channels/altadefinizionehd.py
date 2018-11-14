# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canale per http://altadefinizionehd.com/
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# By MrTruth
# ------------------------------------------------------------

import re

from core import logger, httptools
from core.httptools import urllib
from core import servertools
from core import scrapertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "altadefinizionehd"
__category__ = "F"
__type__ = "generic"
__title__ = "AltadefinizioneHD"
__language__ = "IT"

host = "http://altadefinizionehd.com"

headers = [
    ['User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:52.0) Gecko/20100101 Firefox/52.0'],
    ['Accept-Encoding', 'gzip, deflate'],
    ['Referer', host]
]

def isGeneric():
    return True

# ----------------------------------------------------------------------------------------------------------------
def mainlist(item):
    logger.info("[AltadefinizioneHD.py]==> mainlist")
    itemlist = [
        Item(channel=__channel__,
                     action="ultimifilm",
                     title=color("Ultimi film", "azure"),
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/popcorn_cinema_P.png",),
        Item(channel=__channel__,
                     action="pergenere",
                     title=color("Per Genere", "azure"),
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genres_P.png",),
        Item(channel=__channel__,
                     action="peranno",
                     title=color("Per Anno", "azure"),
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/movie_year_P.png",),
        Item(channel=__channel__,
                     action="perqualita",
                     title=color("Per Qualità", "azure"),
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/blueray_P.png",),
        Item(channel=__channel__,
                     action="search",
                     title=color("Cerca", "yellow"),
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png",)
        ]

    return itemlist

# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def search(item, texto):
    logger.info("[AltadefinizioneHD.py]==> search")
    item.url = host + "/?s=" + texto
    item.extra = "movie"
    try:
        return film(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def pergenere(item):
    logger.info("[AltadefinizioneHD.py]==> pergenere")
    itemlist = []
    
    data = scrapertools.anti_cloudflare(item.url, headers=headers)

    patron = '<li class="cat-item cat-item-\d+"><a href="([^"]+)"(?: title=".*?"|\s)>([^<]+)</a>\s<span>\d+</span>\s</li>'
    blocco = scrapertools.get_match(data, '<ul class="scrolling cat">(.*?)</ul>')

    matches = re.compile(patron, re.DOTALL).findall(blocco)
    for scrapedurl, scrapedtitle in matches:
         itemlist.append(
             Item(channel=__channel__,
                 action="film",
                 title=color(scrapedtitle, "azure"),
                 url=scrapedurl,
                 extra="movie",
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genre_P.png",
                 folder=True))

    return itemlist

# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def peranno(item):
    logger.info("[AltadefinizioneHD.py]==> peranno")
    itemlist = []
    
    data = scrapertools.anti_cloudflare(item.url, headers=headers)

    patron = '<li><a href="([^"]+)">([^<]+)</a></li>'
    blocco = scrapertools.get_match(data, '<ul class="scrolling">(.*?)<div class="filtro_y">')

    matches = re.compile(patron, re.DOTALL).findall(blocco)
    for scrapedurl, scrapedtitle in matches:
         itemlist.append(
             Item(channel=__channel__,
                 action="film",
                 title=color(scrapedtitle, "azure"),
                 url=scrapedurl,
                 extra="movie",
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/movie_year_P.png",
                 folder=True))

    return itemlist

# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def perqualita(item):
    logger.info("[AltadefinizioneHD.py]==> perqualità")
    itemlist = []
    
    data = scrapertools.anti_cloudflare(item.url, headers=headers)

    patron = '<li><a href="([^"]+)">([^<]+)</a></li>'
    blocco = scrapertools.get_match(data, '<ul class="scrolling" style="max-height: 87px;">(.*?)</ul>')

    matches = re.compile(patron, re.DOTALL).findall(blocco)
    for scrapedurl, scrapedtitle in matches:
         itemlist.append(
             Item(channel=__channel__,
                 action="film",
                 title=color(scrapedtitle, "azure"),
                 url=scrapedurl,
                 extra="movie",
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/movies_P.png",
                 folder=True))

    return itemlist

# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def ultimifilm(item):
    logger.info("[AltadefinizioneHD.py]==> ultimifilm")
    itemlist = []

    data = scrapertools.cache_page(item.url, headers=headers)
    blocco = scrapertools.get_match(data, '<div class="item_1 items">([^+]+)<div id="paginador">')
    patron = '<a href="([^"]+)">[^>]+>\s*<img src="([^"]+)" alt="([^"]+)".*?/>'
    matches = re.compile(patron, re.DOTALL).findall(blocco)

    for scrapedurl, scrapedimg, scrapedtitle in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle).strip()
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 title=scrapedtitle,
                 fulltitle=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedimg,
                 extra=item.extra,
                 folder=True), tipo=item.extra))

    patron = '<div class="pag_b"><a href="([^"]+)" >Successivo</a></div>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = matches[0]
        itemlist.append(
            Item(channel=__channel__,
                 action="HomePage",
                 title=color("Torna Home", "yellow"),
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/return_home_P.png",
                 folder=True))
        itemlist.append(
            Item(channel=__channel__,
                action="ultimifilm",
                title=color("Successivo >>", "yellow"),
                url=scrapedurl,
                thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/vari/successivo_P.png",
                folder=True))

    return itemlist

# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def film(item):
    logger.info("[AltadefinizioneHD.py]==> film")
    itemlist = []

    item.url = urllib.unquote_plus(item.url).replace("\\", "")

    data = scrapertools.anti_cloudflare(item.url, headers=headers)
    patron = '<a href="([^"]+)">[^>]+>\s*<img src="([^"]+)" alt="([^"]+)".*?/>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedimg, scrapedtitle in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle).strip()
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 title=scrapedtitle,
                 fulltitle=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedimg,
                 extra=item.extra,
                 folder=True), tipo=item.extra))

    patron = '<div class="pag_b"><a href="([^"]+)" >Next</a></div>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = matches[0]
        itemlist.append(
            Item(channel=__channel__,
                 action="HomePage",
                 title=color("Torna Home", "yellow"),
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/return_home_P.png",
                 folder=True))
        itemlist.append(
            Item(channel=__channel__,
                action="film",
                title=color("Successivo >>", "yellow"),
                url=scrapedurl,
                thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/successivo_P.png",
                folder=True))

    return itemlist

# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def findvideos(item):
    logger.info("[AltadefinizioneHD.py]==> findvideos")

    data = scrapertools.anti_cloudflare(item.url, headers=headers)
    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        videoitem.title = "".join([item.title, color(videoitem.title, "orange")])
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__

    return itemlist

# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def color(text, color):
    return "[COLOR "+color+"]"+text+"[/COLOR]"

def HomePage(item):
    import xbmc
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.streamondemand-pureita-master)")

# ================================================================================================================
