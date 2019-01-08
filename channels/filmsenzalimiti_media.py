# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# TheGroove360 - XBMC Plugin
# Canale filmsenzalimiti_media
# ------------------------------------------------------------

import base64
import re
import urlparse

from core import config
from core import httptools
from core import logger
from core import scrapertools
from core.item import Item
from core.tmdb import infoSod
from servers import servertools

__channel__ = "filmsenzalimiti_media"
host = "https://filmsenzalimiti.media"

headers = [['User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:44.0) Gecko/20100101 Firefox/44.0'],
           ['Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'],
           ['Accept-Encoding', 'gzip, deflate'],
           ['Referer', host],
           ['Cache-Control', 'max-age=0']]


def mainlist(item):
    logger.info("[thegroove360.filmsenzalimiti_media] mainlist")

    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Film[COLOR orange] - Al Cinema[/COLOR]",
                     action="peliculas",
                     url="%s/category/in-sala/" % host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/popcorn_cinema_movie.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film[COLOR orange] - Novita'[/COLOR]",
                     action="peliculas",
                     url="%s/category/nuove-uscite/" % host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/movie_new_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film[COLOR orange] - Ultimi Inseriti[/COLOR]",
                     action="peliculas",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/movie_new_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film[COLOR orange] - Sub-ITA[/COLOR]",
                     action="peliculas",
                     url="%s/category/sub-ita/" % host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/movie_sub_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film[COLOR orange] - Cetegorie[/COLOR]",
                     action="categorie",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/genres_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film[COLOR orange] - Lista A-Z[/COLOR]",
                     action="peliculas_list",
                     url="%s/lista-film-streaming/" % host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/a-z_P.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca ...[/COLOR]",
                     action="search",
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/search_P.png")]

    return itemlist


# ==================================================================================================================================================

def search(item, texto):
    logger.info("[thegroove360.filmsenzalimiti_media] " + item.url + " search " + texto)

    item.url = host + "/?s=" + texto

    try:
        return peliculas_search(item)

    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


# ==================================================================================================================================================

def categorie(item):
    logger.info("[thegroove360.filmsenzalimiti_media] categorie")
    itemlist = []

    data = scrapertools.cache_page(item.url)
    blocco = scrapertools.get_match(data, r'<li class="cat-item cat-item-1"><a href="[^"]+">Film</a>(.*?)</ul>')
    patron = r'<li class=".*?"><a href="([^"]+)">([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(blocco)

    for scrapedurl, scrapedtitle in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/genre_P.png",
                 folder=True))

    return itemlist


# ==================================================================================================================================================

def peliculas(item):
    logger.info("[thegroove360.filmsenzalimiti_media] peliculas")

    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)

    patron = '<div class="col-mt-5 postsh">\s*<div class="poster-media-card">\s*'
    patron += '<a href="([^"]+)" title="([^"]+)">\s*<div class="poster">\s*<span class="rating">\s*'
    patron += '<i class=".*?"></i><span class="rating-number">(.*?)</span>.*?'
    patron += '<img src="([^"]+)" title=".*?" />\s*</div>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, rating, scrapedthumbnail in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle).strip()
        if rating == "":
            rating = "N/A"
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 title=scrapedtitle + " ([COLOR yellow]" + rating + "[/COLOR])",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle), tipo="movie"))

    next_page = scrapertools.find_single_match(data,
                                               '<a href="([^"]+)"><i class="glyphicon glyphicon-chevron-right" aria-hidden="true')
    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=next_page,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/next_1.png"))

    return itemlist


# ==================================================================================================================================================

def peliculas_list(item):
    logger.info("[thegroove360.filmsenzalimiti_media] peliculas_list")

    itemlist = []
    PERPAGE = 42

    p = 1
    if '{}' in item.url:
        item.url, p = item.url.split('{}')
        p = int(p)

    # Descarga la pagina
    data = httptools.downloadpage(item.url).data

    # Extrae las entradas
    patron = '<img src=".*?" title=".*?" />\s*'
    patron += '<a href="([^"]+)"\s*title="([^<]+)">'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapedplot = ""
    scrapedthumbnail = ""
    for i, (scrapedurl, scrapedtitle) in enumerate(matches):
        if (p - 1) * PERPAGE > i: continue
        if i >= p * PERPAGE: break
        title = scrapertools.decodeHtmlentities(scrapedtitle).strip()
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="findvideos",
                 contentType="movie",
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=title,
                 show=title,
                 plot=scrapedplot,
                 folder=True), tipo="movie"))

    # Extrae el paginador
    if len(matches) >= p * PERPAGE:
        scrapedurl = item.url + '{}' + str(p + 1)
        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="peliculas_list",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/next_1.png",
                 folder=True))

    return itemlist


# ==================================================================================================================================================

def peliculas_search(item):
    logger.info("[thegroove360.filmsenzalimiti_media] peliculas_search")

    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)

    patron = '<div class="list-score">(.*?)</div>\s*<div class=".*?">\s*'
    patron += '<div class="row">\s*<a href="([^"]+)" title="([^"]+)">\s*'
    patron += '<img src="([^"]+)" title="[^<]+" />\s*</a>.*?'
    patron += '<p class="text-list">(.*?)</p>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for rating, scrapedurl, scrapedtitle, scrapedthumbnail, scrapedplot in matches:
        if rating == "":
            rating = "N/A"
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 title=scrapedtitle + " ([COLOR yellow]" + rating + "[/COLOR])",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=scrapedtitle,
                 plot=scrapedplot,
                 show=scrapedtitle), tipo="movie"))

    next_page = scrapertools.find_single_match(data,'<a href="([^"]+)"><i class="glyphicon glyphicon-chevron-right" aria-hidden="true')
    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=next_page,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/next_1.png"))

    return itemlist


# ==================================================================================================================================================

def findvideos(item):
    logger.info("[thegroove360.filmsenzalimiti_media] findvideos")

    itemlist = []

    # Descarga la página
    data = scrapertools.anti_cloudflare(item.url).replace('\n', '')

    patron = r'<iframe width=".+?" height=".+?" src="([^"]+)" allowfullscreen frameborder="0">'
    url = scrapertools.find_single_match(data, patron).replace("?italiafilm", "")

    if 'hdpass' in url:
        data = scrapertools.cache_page(url)

        start = data.find('<div class="row mobileRes">')
        end = data.find('<div id="playerFront">', start)
        data = data[start:end]

        patron_res = r'<div class="row mobileRes">([\s\S]*)<\/div>'
        patron_mir = r'<div class="row mobileMirrs">([\s\S]*)<\/div>'
        patron_media = r'<input type="hidden" name="urlEmbed" data-mirror="([^"]+)" id="urlEmbed" value="([^"]+)"[^>]+>'

        res = scrapertools.find_single_match(data, patron_res)

        urls = []
        for res_url, res_video in scrapertools.find_multiple_matches(res,'<option.*?value="([^"]+?)">([^<]+?)</option>'):

            data = scrapertools.cache_page(urlparse.urljoin(url, res_url), headers=headers).replace('\n', '')

            mir = scrapertools.find_single_match(data, patron_mir)

            for mir_url in scrapertools.find_multiple_matches(mir,'<option.*?value="([^"]+?)">[^<]+?</value>'):

                data = scrapertools.cache_page(urlparse.urljoin(url, mir_url), headers=headers).replace('\n', '')

                for media_label, media_url in re.compile(patron_media).findall(data):
                    urls.append(url_decode(media_url))

        itemlist = servertools.find_video_items(data='\n'.join(urls))

        for videoitem in itemlist:
            servername = re.sub(r'[-\[\]\s]+', '', videoitem.title)
            videoitem.title = "".join(
                ['[COLOR azure][[COLOR orange]' + servername.capitalize() + '[/COLOR]] - ', item.title])
            videoitem.fulltitle = item.fulltitle
            videoitem.show = item.show
            videoitem.thumbnail = item.thumbnail
            videoitem.plot = item.plot
            videoitem.channel = __channel__

        return itemlist


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