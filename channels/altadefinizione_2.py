# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Thegroove360 - XBMC Plugin
# Canale altadefinizione.im
# ------------------------------------------------------------

import base64
import re
import urlparse

from core import httptools
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "altadefinizione_2"
__category__ = "F,S,A"
__type__ = "generic"
__title__ = "AltaDefinizione"
__language__ = "IT"

host = "https://altadefinizione.im"

headers = [
    ['User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:44.0) Gecko/20100101 Firefox/44.0'],
    ['Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'],
    ['Accept-Encoding', 'gzip, deflate'],
    ['Referer', host],
    ['Cache-Control', 'max-age=0']
]


def isGeneric():
    return True

# ==============================================================================================================================================

def mainlist(item):
    logger.info("[thegroove360.altadefinizione_2] mainlist")

    itemlist = [
        Item(channel=__channel__,
             title="[COLOR azure]Film - [COLOR orange]Al Cinema[/COLOR]",
             action="peliculas",
             url=host + "/al-cinema/",
             thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/popcorn_serie_P.png"),
        Item(channel=__channel__,
             title="[COLOR azure]Film - [COLOR orange]Novita'[/COLOR]",
             action="peliculas",
             url=host + "/nuove-uscite/",
             thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/movie_new_P.png"),
        Item(channel=__channel__,
             title="[COLOR azure]Film - [COLOR orange]Per Genere[/COLOR]",
             action="genere",
             url=host,
             thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/genres_P.png"),
        Item(channel=__channel__,
             title="[COLOR azure]Film - [COLOR orange]Per Anno[/COLOR]",
             action="anno",
             url=host,
             thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/movie_year_P.png"),
        Item(channel=__channel__,
             title="[COLOR azure]Film - [COLOR orange]Sottotitolati[/COLOR]",
             action="peliculas",
             url=host + "/sub-ita/",
             thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/movie_sub_P.png"),
        Item(channel=__channel__,
             title="[COLOR orange]Cerca...[/COLOR]",
             action="search",
             extra="movie",
             thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/search_P.png")]

    return itemlist

# ==============================================================================================================================================

def search(item, texto):
    logger.info("[thegroove360.altadefinizione_2] " + item.url + " search " + texto)

    item.url = host + "/?search=" + texto

    try:
        return fichas(item)

    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


# ==============================================================================================================================================

def genere(item):
    logger.info("[thegroove360.altadefinizione_2] genere")
    itemlist = []

    data = scrapertools.anti_cloudflare(item.url, headers)

    patron = '<ul class="listSubCat" id="Film">(.*?)</ul>'
    data = scrapertools.find_single_match(data, patron)

    patron = '<li><a href="(.*?)">(.*?)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedtitle in matches:
        scrapedurl = host + scrapedurl
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/genre_P.png",
                 folder=True))

    return itemlist

# ==============================================================================================================================================

def anno(item):
    logger.info("[thegroove360.altadefinizione_2] genere")
    itemlist = []

    data = scrapertools.anti_cloudflare(item.url, headers)

    patron = '<ul class="listSubCat" id="Anno">(.*?)</div>'
    data = scrapertools.find_single_match(data, patron)

    patron = '<li><a href="([^"]+)">([^<]+)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedtitle in matches:
        scrapedurl = host + scrapedurl
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/movie_year_P.png",
                 folder=True))

    return itemlist

# ==============================================================================================================================================

def peliculas(item):
    logger.info("[thegroove360.altadefinzione_2] peliculas")
    itemlist = []

    # Carica la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    #Estrae il contenuto
    patron = r'<div class="col-lg-3 col-md-3 col-xs-3">.*?<div class="wrapperImage">.*?<span class=.*?<span class=.*?<a href="(.*?)".*?src="(.*?)".*?<a href=.*?">.*?(\S[^\"]+?)\s\s'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail,scrapedtitle in matches:
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findlink",
                 contentType="movie",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=host + scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle), tipo='movie'))

    # Paginación
    next_page = scrapertools.find_single_match(data, '<span aria-current="page" class="page-numbers current">(.*?)</span></li><li>')
    if next_page != "":
        next_page = int(next_page) + 1
        next_page = host + "/page/" + str(next_page) + "/"
        itemlist.append(
            Item(channel=__channel__,
                action="peliculas",
                title="[COLOR orange]Successivo >>[/COLOR]",
                url=next_page,
                thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/next_1.png"))

    return itemlist

# ==============================================================================================================================================

def findlink(item):
    logger.info("[thegroove360.altadefinzione_2] findlink")
    itemlist = []

    #Carica la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    #Estrae il contenuto
    patron = r'<div class="col-lg-12 frameDown">.*?src="(.*?)"'
    matches = re.compile(patron, re.DOTALL).findall(data)

    #Ricarico la pagina
    url = host + matches[0]
    data = httptools.downloadpage(url).data

    #Estrae il contenuto
    patron = r'class="dwnMob linkDown" href="(.*?)".*?alt="(.*?)\s'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedserver in matches:
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 contentType="movie",
                 title="[COLOR orange][" + scrapedserver + "] - [/COLOR]" + "[COLOR azure]" + item.title + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=item.thumbnail,
                 fulltitle="[COLOR orange][" + scrapedserver + "] - [/COLOR]" + "[COLOR azure]" + item.title + "[/COLOR]",
                 show="[COLOR orange][" + scrapedserver + "] - [/COLOR]" + "[COLOR azure]" + item.title + "[/COLOR]"), tipo='movie'))

    return itemlist

# ==============================================================================================================================================

def url_decode(url_enc):
    lenght = len(url_enc)
    if lenght % 2 == 0:
        len2 = lenght / 2
        first = url_enc[0:len2]
        last = url_enc[len2:lenght]
        url_enc = last + first
        reverse = url_enc[::-1]
        return base64.b64decode(reverse)

    last_car = url_enc[lenght - 1]
    url_enc[lenght - 1] = ' '
    url_enc = url_enc.strip()
    len1 = len(url_enc)
    len2 = len1 / 2
    first = url_enc[0:len2]
    last = url_enc[len2:len1]
    url_enc = last + first
    reverse = url_enc[::-1]
    reverse = reverse + last_car
    return base64.b64decode(reverse)

# ==============================================================================================================================================