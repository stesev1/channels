# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Thegroove360 - XBMC Plugin
# Canale altadefinizione.center
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

host = "https://altadefinizione.center"

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
             action="fichas",
             url=host + "/al-cinema/",
             thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/popcorn_serie_P.png"),
        Item(channel=__channel__,
             title="[COLOR azure]Film - [COLOR orange]Novita'[/COLOR]",
             action="fichas",
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
             action="fichas",
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

    item.url = host + "/?s=" + texto

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

    data = httptools.downloadpage(item.url, headers=headers).data

    patron = r'<option value=\"([^\"]+)\">(.*?)</'
    matches = re.compile(patron, re.MULTILINE).findall(data)

    for scrapedurl, scrapedtitle in matches:
        if scrapedurl == host:
            continue
        itemlist.append(
            Item(channel=__channel__,
                 action="fichas",
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/genre_P.png",
                 folder=True))

    return itemlist


# ==============================================================================================================================================

def anno(item):
    logger.info("[thegroove360.altadefinizione_2] genere")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data

    patron = '<ul class="listSubCat" id="Anno">(.*?)</div>'
    data = scrapertools.find_single_match(data, patron)

    patron = '<li><a href="([^"]+)">([^<]+)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedtitle in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="fichas",
                 title=scrapedtitle,
                 url=scrapedurl,
                 extra="nospace",
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/movie_year_P.png",
                 folder=True))

    return itemlist


# ==============================================================================================================================================


def fichas(item):
    logger.info("[thegroove360.altadefinizione_2] fichas")

    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    if item.extra == "nospace":
        patron = r'<div class=\"wrapperImage\">(<a|<span.*?>(.*?)<.*?<a) href=\"([^\"]+)\".*?<img width=.*?src=\"([^\"]+)\".*?\s.*?<h2.*?<a.*?>(.*)</a>.*?<div.*?/>(.*?)<'
    elif item.action == "search":
        patron = r'<a href=\"([^\"]+)\">\s<div class=\"wrapperImage\">?(<img|<span.*?>(.*?)<.*?<img) width=.*?src=\"([^\"]+)\".*?\s.*?<h5.*?>(.*?)</h5>.*?<div.*?/>(.*?)<'
    else:
        patron = r'<div class=\"wrapperImage\">?(\s|\s<span.*?>(.*?)</.*?\s)<a href=\"([^\"]+)\"><img width=.*?src=\"([^\"]+)\".*?\s.*?<h2.*?<a.*?>(.*)</a>.*?\s<div.*?/>(.*)<'
    matches = re.finditer(patron, data, re.MULTILINE)

    for matchNum, match in enumerate(matches, start=1):

        scrapedq = "SD"
        if match.group(2):
            scrapedq = match.group(2)

        scrapedurl = match.group(3)

        if item.action == "search":
            scrapedurl = match.group(1)

            scrapedq = "SD"
            if match.group(3):
                scrapedq = match.group(3)

        scrapedthumbnail = match.group(4)
        scrapedtitle = match.group(5)
        scrapedvote = match.group(6).strip()

        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 contentType="movie",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR] [" + scrapedq + "] " + scrapedvote,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle))

    # Paginación
    next_page = scrapertools.find_single_match(data, '<a class=\"next page-numbers\" href=\"([^\"]+)\">')
    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="cinema",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=next_page,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/next_1.png"))

    return itemlist


# ==============================================================================================================================================

def findvideos(item):
    logger.info("[thegroove360.altadefinizione_2] findvideos")

    itemlist = []

    # Descarga la página
    data = httptools.downloadpage(item.url, headers=headers).data.replace('\n', '')
    patron = r'<iframe width=".+?" height=".+?" src="([^"]+)"></iframe>'
    url = scrapertools.find_single_match(data, patron).replace("?alta", "")
    url = url.replace("&download=1", "")

    if 'hdpass' in url:
        data = scrapertools.cache_page(url, headers=headers)

        start = data.find('<div class="row mobileRes">')
        end = data.find('<div id="playerFront">', start)
        data = data[start:end]

        patron_res = '<div class="row mobileRes">(.*?)</div>'
        patron_mir = '<div class="row mobileMirrs">(.*?)</div>'
        patron_media = r'<input type="hidden" name="urlEmbed" data-mirror="([^"]+)" id="urlEmbed" value="([^"]+)" />'

        res = scrapertools.find_single_match(data, patron_res)

        urls = []
        for res_url, res_video in scrapertools.find_multiple_matches(res,
                                                                     '<option.*?value="([^"]+?)">([^<]+?)</option>'):

            data = scrapertools.cache_page(urlparse.urljoin(url, res_url), headers=headers).replace('\n', '')

            mir = scrapertools.find_single_match(data, patron_mir)

            for mir_url in scrapertools.find_multiple_matches(mir, '<option.*?value="([^"]+?)">[^<]+?</value>'):

                data = scrapertools.cache_page(urlparse.urljoin(url, mir_url), headers=headers).replace('\n', '')

                for media_label, media_url in re.compile(patron_media).findall(data):
                    urls.append(url_decode(media_url))

        itemlist = servertools.find_video_items(data='\n'.join(urls))
        for videoitem in itemlist:
            videoitem.title = item.title + videoitem.title
            videoitem.fulltitle = item.fulltitle
            videoitem.thumbnail = item.thumbnail
            videoitem.show = item.show
            videoitem.plot = item.plot
            videoitem.channel = __channel__

    return itemlist


# -----------------------------------------------
# -----------------------------------------------

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