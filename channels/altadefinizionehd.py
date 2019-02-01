# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Thegroove360 - XBMC Plugin
# Canale altadefinizionehd
# ------------------------------------------------------------

import re
import urlparse

from core import config
from core import httptools
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "altadefinizionehd"
host = "https://altadefinizionehd.org/"
headers = [['Referer', host]]



def mainlist(item):
    logger.info("[thegroove360.altadefinizionehd] mainlist")

    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Film - [COLOR orange]Al Cinema[/COLOR]",
                     action="peliculas",
                     url="%s/genere/cinema/" % host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/popcorn_serie_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film - [COLOR orange]Novita'[/COLOR]",
                     action="peliculas",
                     url="%s/film/" % host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/movie_new_P.png"),
                # Item(channel=__channel__,
                #      title="[COLOR azure]Film - [COLOR orange]Top Imdb[/COLOR]",
                #      action="peliculas_imdb",
                #      url="%s/top-imdb/" % host,
                #      extra="movie",
                #      thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/movies_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film - [COLOR orange]Categorie[/COLOR]",
                     action="genere",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/genres_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film - [COLOR orange]Popolari[/COLOR]",
                     action="peliculas",
                     url="%s/trending/?get=movies" % host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/hd_movies_P.png"),
                Item(channel=__channel__,
                     title="[COLOR orange]Cerca...[/COLOR]",
                     action="search",
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/search_P.png")]

    return itemlist


# ========================================================================================================================================================

def search(item, texto):
    logger.info("[thegroove360.altadefinizionehd] " + item.url + " search " + texto)

    item.url = host + "/?s=" + texto

    try:
        return peliculas_search(item)

    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


# ========================================================================================================================================================

def peliculas_search(item):
    logger.info("[thegroove360.altadefinizione] peliculas_search")
    itemlist = []

    # Carica la pagina
    data = httptools.downloadpage(item.url).data

    # Estrae i contenuti
    patron = r'<article.*?<a href=\"([^\"]+)\"><img src=\"([^\"]+)\".*?><a.*?>(.*?)<'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        scrapedplot = ""

        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 contentType="movie",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR] ",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 extra=item.extra,
                 folder=True))

    # Paginazione
    patronvideos = r'<a class=\'arrow_pag\' href=\"([^\"]+)\">'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = matches[0]
        itemlist.append(
            Item(channel=__channel__,
                 action="HomePage",
                 title="[COLOR yellow]Torna Home[/COLOR]",
                 folder=True)),
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png",
                 extra=item.extra,
                 folder=True))

    return itemlist


# ========================================================================================================================================================

def genere(item):
    logger.info("[thegroove360.altadefinizionehd] genere")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data
    bloque = scrapertools.get_match(data, '<h2>Categorie</h2>(.*?)</ul>')
    # Extrae las entradas (carpetas)
    patron = '<a href="([^"]+)[^>]+>([^<]+)<\/a>\s*<i>([^<]+)<'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle, quantity in matches:
        scrapedtitle = scrapedtitle.replace("televisione film", "Film TV")
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR] ",
                 url=scrapedurl,
                 plot="[COLOR orange]Numero di Film presenti in %s[/COLOR][B] (%s)[/B]" % (scrapedtitle, quantity),
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/genre_P.png",
                 folder=True))

    return itemlist


# ========================================================================================================================================================

def year(item):
    logger.info("[thegroove360.altadefinizionehd] year")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data
    bloque = scrapertools.get_match(data, 'Anno</a>(.*?)</ul>')

    # Extrae las entradas (carpetas)
    patron = '<a href="([^"]+)">([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        scrapedurl = host + scrapedurl
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/movie_year_P.png",
                 folder=True))

    return itemlist


# ========================================================================================================================================================

def peliculas(item):
    logger.info("[thegroove360.altadefinizionehd] peliculas")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    patron = '<div class="poster">\s*<img\s*src="([^"]+)"\s*alt="([^"]+)">\s*<div class="rating">'
    patron += '<span class="icon-star2"><\/span>\s*([^<]+)<\/div>\s*<div class="mepo">\s*'
    patron += '<span class="quality">([^<]+)<\/span>\s*<\/div>\s*<a href="([^"]+)">'
    # patron += '<div class="texto">([^<]+)</div>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedthumbnail, scrapedtitle, rating, quality, scrapedurl in matches:
        if rating:
            rating = " ([COLOR yellow]" + rating.strip() + "[/COLOR])"
        if quality:
            quality = quality.replace("1080p", "Full HD").replace("720P", "HD")
            quality = " ([COLOR yellow]" + quality.strip() + "[/COLOR])"

        scrapedtitle = scrapedtitle.replace("&#8217;", "'").replace("&#8211;", "-")
        scrapedplot = ""
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]" + quality + rating,
                 thumbnail=scrapedthumbnail,
                 url=scrapedurl,
                 fulltitle=scrapedtitle,
                 plot=scrapedplot,
                 show=scrapedtitle))

    # Extrae el paginador
    paginador = scrapertools.find_single_match(data,
                                               '<a class=\'arrow_pag\' href="([^"]+)"><i id=\'nextpagination\' class=\'icon-caret-right\'>')
    if paginador != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=paginador,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/next_1.png"))

    return itemlist


# ========================================================================================================================================================

def peliculas_imdb(item):
    logger.info("[thegroove360.altadefinizionehd] peliculas_imdb")
    itemlist = []
    minpage = 10

    p = 1
    if '{}' in item.url:
        item.url, p = item.url.split('{}')
        p = int(p)

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    patron = '<img\s*src="([^"]+)" \/><\/a><\/div><\/div>\s*<div class="puesto">(.*?)<\/div>\s*'
    patron += '<div class="rating">(.*?)<\/div>\s*<div class="title"><a href="([^"]+)">([^<]+)<\/a>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for i, (scrapedthumbnail, position, rating, scrapedurl, scrapedtitle) in enumerate(matches):
        if (p - 1) * minpage > i: continue
        if i >= p * minpage: break
        position = "[COLOR red]" + position.strip() + "[/COLOR] - "
        rating = " ([COLOR yellow]" + rating.strip() + "[/COLOR])"

        scrapedtitle = scrapedtitle.replace("&#8217;", "'").replace("&#8211;", "-")
        scrapedplot = ""
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 title=position + "[COLOR azure]" + scrapedtitle + "[/COLOR]" + rating,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle))

    # Extrae el paginador
    if len(matches) >= p * minpage:
        scrapedurl = item.url + '{}' + str(p + 1)
        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="peliculas_imdb",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/next_1.png",
                 folder=True))

    return itemlist


# ========================================================================================================================================================


def findvideos(item):
    data = httptools.downloadpage(item.url).data
    patron = r"<li id='player-.*?'.*?class='dooplay_player_option'\sdata-type='(.*?)'\sdata-post='(.*?)'\sdata-nume='(.*?)'>.*?'title'>(.*?)</"
    matches = re.compile(patron, re.IGNORECASE).findall(data)

    itemlist = []

    for scrapedtype, scrapedpost, scrapednume, scrapedtitle in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 fulltitle=item.title + " [" + scrapedtitle + "]",
                 show=scrapedtitle,
                 title="[COLOR azure]" + item.title + "[/COLOR] " + " [" + scrapedtitle + "]",
                 url="%swp-admin/admin-ajax.php" % host,
                 post=scrapedpost,
                 nume=scrapednume,
                 type=scrapedtype,
                 extra=item.extra,
                 folder=True))

    return itemlist


# ========================================================================================================================================================


def play(item):
    import urllib
    payload = urllib.urlencode({'action': 'doo_player_ajax', 'post': item.post, 'nume': item.nume, 'type': item.type})
    data = httptools.downloadpage(item.url, post=payload).data

    patron = r"<iframe.*src='(([^']+))'\s"
    matches = re.compile(patron, re.IGNORECASE).findall(data)

    url = matches[0][0]
    url = url.strip()
    data = httptools.downloadpage(url, headers=headers).data

    itemlist = servertools.find_video_items(data=data)

    return itemlist

# ========================================================================================================================================================
