# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# TheGroove360 - XBMC Plugin
# Canale filmsenzalimiti
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

__channel__ = "filmsenzalimiti"
host = "https://filmsenzalimiti.pink"
headers = [['Referer', host]]


def mainlist(item):
    logger.info("[thegroove360.filmsenzalimiti] mainlist")

    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Film - [COLOR orange]Al Cinema[/COLOR]",
                     action="novedades",
                     extra="movie",
                     url="%s/prime-visioni/" % host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/popcorn_cinema_movie.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film - [COLOR orange]Novita[/COLOR]",
                     action="novedades",
                     extra="movie",
                     url="%s/genere/film/" % host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/all_movies_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film - [COLOR orange]Categorie[/COLOR]",
                     action="categorias",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/genre_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film - [COLOR orange]HD[/COLOR]",
                     action="novedades",
                     extra="movie",
                     url="%s/?s=HD" % host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/hd_movies_P.png"),
                Item(channel=__channel__,
                     action="search",
                     extra="movie",
                     title="[COLOR yellow]Cerca Film...[/COLOR]",
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/search_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV - [COLOR orange]Novita'[/COLOR]",
                     extra="tvshow",
                     action="novedades_tv",
                     url="%s/genere/serie-tv/" % host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/tv_series_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV - [COLOR orange]Aggiornate[/COLOR]",
                     extra="tvshow",
                     action="peliculas_update",
                     url="%s/aggiornamenti-serie-tv/" % host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/tv_series_P.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca Serie TV...[/COLOR]",
                     action="search",
                     extra="tvshow",
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/search_P.png")]
    return itemlist


# ==================================================================================================================================================

def categorias(item):
    logger.info("[thegroove360.filmsenzalimiti] categorias")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data

    # Narrow search by selecting only the combo
    patron = 'ULTIME SERIE TV</a></li>(.*?)</ul>'
    bloque = scrapertools.get_match(data, patron)

    # The categories are the options for the combo
    patron = '<li><a href="([^"]+)">([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        scrapedurl = urlparse.urljoin(item.url, scrapedurl)
        if "Anime" in scrapedtitle or "Cartoni" in scrapedtitle:
            continue
        scrapedthumbnail = ""
        scrapedplot = ""
        itemlist.append(
            Item(channel=__channel__,
                 action="novedades",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/genre_P.png",
                 extra=item.extra,
                 plot=scrapedplot))

    return itemlist


# ==================================================================================================================================================

def search(item, texto):
    logger.info("[thegroove360.filmsenzalimiti] " + item.url + " search " + texto)
    item.url = host + "/?s=" + texto
    try:
        if item.extra == "movie":
            return peliculas_src(item)
        else:
            return peliculas_tvsrc(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


# ==================================================================================================================================================

def novedades(item):
    logger.info("[thegroove360.filmsenzalimiti] novedades")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = '<li><a href="([^"]+)" data.*?thumbnail="([^"]+)">[^>]+>\s*<div class="title">([^<]+)<\/div>\s*' \
             '<div class[^>]+>([^<]+)<\/div>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle, rating in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)

        if "test yb " in scrapedtitle or "test by" in scrapedtitle:
            continue
        if "[HD]" in scrapedtitle:
            quality = " ([COLOR yellow]HD[/COLOR])"
        else:
            quality = ""
        if rating:
            rating = " ([COLOR yellow]" + rating + "[/COLOR])"
            if "HD" in rating or "N/A" in rating or "N/D" in rating:
                rating = ""

        scrapedtitle = scrapedtitle.replace(" [HD]", "")
        scrapedtitle = scrapedtitle.replace(" & ", " e ").replace(":", " - ")
        scrapedtitle = scrapedtitle.replace(" – ", " - ").replace("’", "'")
        scrapedplot = ""
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos_movies",
                 contentType="movie",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR] " + quality + rating,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 extra=item.extra,
                 folder=True), tipo='movie'))

    # Extrae el paginador
    patronvideos = '<li><a href="([^>]+)"\s*>Pagina successiva'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="novedades",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/next_1.png",
                 extra=item.extra,
                 folder=True))

    return itemlist


# ==================================================================================================================================================

def peliculas_src(item):
    logger.info("[thegroove360.filmsenzalimiti] peliculas_src")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url).data

    # Extrae las entradas (carpetas)
    patron = r'<a href="([^"]+)" data-thumbnail="(.*?)"><div>\s*'
    patron += '<div class="title">([^>]+)</div>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        if "-serie" in scrapedurl or "-serie" in scrapedthumbnail:
            continue
        if "test yb " in scrapedtitle or "test by" in scrapedtitle:
            continue
        if "[HD]" in scrapedtitle:
            quality = " ([COLOR yellow]HD[/COLOR])"
        else:
            quality = ""
        scrapedtitle = scrapedtitle.replace(" [HD]", "")
        scrapedtitle = scrapedtitle.replace(":", " - ").replace("’", "'")
        info = httptools.downloadpage(scrapedurl).data
        scrapedplot = scrapertools.find_single_match(info,
                                                     '<div class="pad">[^>]+>[^>]+>(?:[^>]+<a href="[^"]+".*?<\/a>|).*?[^>]+>\s*(?:<div>|)(?:<p>|)([^<]+)<')
        # scrapedplot = scrapertools.decodeHtmlentities(scrapertools.find_single_match(daa, patron)).strip()
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos_movies",
                 contentType="movie",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True))

    return itemlist


# ==================================================================================================================================================

def peliculas_tvsrc(item):
    logger.info("[thegroove360.filmsenzalimiti] novedades")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url).data

    # Extrae las entradas (carpetas)
    patron = '<li><a href="([^"]+)" data-thumbnail="([^"]+)"><div>\s*'
    patron += '<div class="title">([^<]+)</div>'

    matches = re.compile(patron, re.DOTALL).finditer(data)

    for match in matches:
        scrapedurl = urlparse.urljoin(item.url, match.group(1))
        scrapedthumbnail = scrapertools.unescape(match.group(2))
        scrapedtitle = scrapertools.unescape(match.group(3))
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        if "-film" in scrapedurl or "-film" in scrapedthumbnail:
            continue
        if "[HD]" in scrapedtitle:
            quality = " ([COLOR yellow]HD[/COLOR])"
        else:
            quality = ""

        scrapedtitle = scrapedtitle.replace(" [HD]", "").replace(" & ", " e ")
        scrapedtitle = scrapedtitle.replace(" – ", " - ").replace("’", "'")
        scrapedtitle = scrapedtitle.strip()

        info = httptools.downloadpage(scrapedurl).data
        scrapedplot = scrapertools.find_single_match(info,
                                                     '<div class="pad">[^>]+>[^>]+>(?:[^>]+<a href="[^"]+".*?</a>|).*?[^>]+>\s*(?:<div>|)(?:<p>|)([^<]+)<')
        itemlist.append(
            Item(channel=__channel__,
                 action="episodios",
                 contentType="tv",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]" + quality,
                 url=scrapedurl,
                 extra=item.extra,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True))
    return itemlist


# ==================================================================================================================================================

def novedades_tv(item):
    logger.info("[thegroove360.filmsenzalimiti] novedades")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = '<li><a href="([^"]+)" data-thumbnail="([^"]+)"><div>\s*'
    patron += '<div class="title">([^<]+)</div>'

    matches = re.compile(patron, re.DOTALL).finditer(data)

    for match in matches:
        scrapedurl = urlparse.urljoin(item.url, match.group(1))
        scrapedthumbnail = scrapertools.unescape(match.group(2))
        scrapedtitle = scrapertools.unescape(match.group(3))
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        if "-film" in scrapedurl or "-film" in scrapedthumbnail:
            continue
        if "[HD]" in scrapedtitle:
            quality = " ([COLOR yellow]HD[/COLOR])"
        else:
            quality = ""

        scrapedtitle = scrapedtitle.replace(" [HD]", "").replace(" & ", " e ")
        scrapedtitle = scrapedtitle.replace(" – ", " - ").replace("’", "'")
        scrapedtitle = scrapedtitle.strip()

        scrapedplot = ""
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 contentType="tv",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]" + quality,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='tv'))

    # Extrae el paginador
    patronvideos = '<li><a href="([^"]+)"\s*>Pagina successiva'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="novedades_tv",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/next_1.png",
                 folder=True))

    return itemlist


# ==================================================================================================================================================

def peliculas_update(item):
    logger.info("[thegroove360.filmsenzalimiti] peliculas_update")
    itemlist = []
    PERPAGE = 14

    p = 1
    if '{}' in item.url:
        item.url, p = item.url.split('{}')
        p = int(p)

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = '<li><a href="([^"]+)" data-thumbnail="([^"]+)"><div>\s*'
    patron += '<div class="title">([^<]+)</div>\s*'
    patron += '<div class="episode" title="Nuovi episodi">([^<]+)</div>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for i, (scrapedurl, scrapedthumbnail, scrapedtitle, info) in enumerate(matches):
        if (p - 1) * PERPAGE > i: continue
        if i >= p * PERPAGE: break
        if "Sub" in info:
            lang = " ([COLOR orange]Sub Ita[/COLOR])"
        else:
            lang = ""
        info = " ([COLOR orange]" + info + "[/COLOR])"

        scrapedplot = ""
        scrapedtitle = scrapedtitle.replace(" & ", " e ").replace("’", "'")
        scrapedtitle = scrapedtitle.replace(" – ", " - ")
        info = info.replace(" Sub-Ita", "")
        scrapedtitle = scrapedtitle.strip()
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="episodios",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]" + info + lang,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='tv'))

    # Extrae el paginador
    if len(matches) >= p * PERPAGE:
        scrapedurl = item.url + '{}' + str(p + 1)
        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="peliculas_update",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/next_1.png",
                 folder=True))

    return itemlist


# ==================================================================================================================================================

def episodios(item):
    def load_episodios(html, item, itemlist, lang_title):
        patron = '((?:.*?<a[^h]+href="[^"]+"[^>]+target[^>]+>[^<]+<\/a>)+)'
        matches = re.compile(patron).findall(html)
        for data in matches:
            # Extrae las entradas
            scrapedtitle = data.split('<a ')[0]
            scrapedtitle = re.sub(r'<[^>]*>', '', scrapedtitle).strip()
            scrapedtitle = scrapedtitle.replace("Speedvideo", "").replace(";", "")
            if scrapedtitle != 'Categorie':
                itemlist.append(
                    Item(channel=__channel__,
                         action="findvideos",
                         title="[COLOR azure]%s[/COLOR]" % (scrapedtitle + " (" + lang_title + ")"),
                         url=data,
                         thumbnail=item.thumbnail,
                         extra=item.extra,
                         fulltitle=scrapedtitle + " (" + lang_title + ")" + ' - ' + item.show,
                         plot="[COLOR orange]" + item.show + "[/COLOR] " + item.plot,
                         show=item.show))

    logger.info("[thegroove360.filmsenzalimiti] episodios")

    itemlist = []

    # Descarga la página
    data = httptools.downloadpage(item.url).data
    data = scrapertools.decodeHtmlentities(data)

    lang_titles = []
    starts = []
    patron = r"STAGIONE.*?ITA|stagione.*?"
    matches = re.compile(patron, re.IGNORECASE).finditer(data)
    if "Continua con il video" in data:
        return findvideos_movies(item)

    for match in matches:
        season_title = match.group()
        if season_title != '':
            lang_titles.append('SUB ITA' if 'SUB' in season_title.upper() else 'ITA')
            starts.append(match.end())

    i = 1
    len_lang_titles = len(lang_titles)

    while i <= len_lang_titles:
        inizio = starts[i - 1]
        fine = starts[i] if i < len_lang_titles else -1

        html = data[inizio:fine]
        lang_title = lang_titles[i - 1]

        load_episodios(html, item, itemlist, lang_title)

        i += 1

    if config.get_library_support() and len(itemlist) != 0:
        itemlist.append(
            Item(channel=__channel__,
                 title=item.show,
                 url=item.url,
                 action="add_serie_to_library",
                 extra="episodios" + "###" + item.extra,
                 show=item.show))
        itemlist.append(
            Item(channel=__channel__,
                 title="Scarica tutti gli episodi della serie",
                 url=item.url,
                 action="download_all_episodes",
                 extra="episodios" + "###" + item.extra,
                 show=item.show))

    return itemlist


# ==================================================================================================================================================

def findvideos(item):
    logger.info("[thegroove360.filmsenzalimiti] findvideos_tv")
    itemlist = []

    patron = '<a.*?href=".*?goto\/([^"]+)"[^>]+>([^<]+)<\/a>'

    matches = re.compile(patron, re.DOTALL).findall(item.url)

    for scrapedurl, scrapedserver in matches:
        itemlist.append(
            Item(
                channel=__channel__,
                action="play",
                fulltitle=item.fulltitle,
                show=item.show,
                title="[COLOR azure][[COLOR orange]" + scrapedserver + "[/COLOR]] - " + item.title + "[/COLOR]",
                url=scrapedurl.decode('base64'),
                thumbnail=item.thumbnail,
                plot=item.plot,
                folder=True))

    return itemlist


# ===================================================================================================================================================

def findvideos_movies(item):
    logger.info("[thegroove360.filmsenzalimiti] findvideos_movies")
    itemlist = []

    data = httptools.downloadpage(item.url).data
    # The categories are the options for the combo
    patron = '<iframe class="embed-responsive-item" SRC="(([^.]+)[^"]+)"[^>]+></iframe>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    if "Stagione" in data or "stagione" in data or "STAGIONE" in data:
        return episodios(item)
    for scrapedurl, scrapedtitle in matches:
        scrapedurl = urlparse.urljoin(item.url, scrapedurl)
        scrapedthumbnail = ""
        scrapedplot = ""
        scrapedtitle = scrapedtitle.replace("https://", "")
        scrapedtitle = scrapedtitle.capitalize()
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 fulltitle=item.fulltitle,
                 title="[COLOR azure][[COLOR orange]" + scrapedtitle + "[/COLOR]] - " + item.title + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=item.thumbnail,
                 show=item.show,
                 plot=item.plot,
                 folder=True))

    patron = '<li><a href="([^"]+)" target="__blank" rel="nofollow">([^<]+)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    if "Stagione" in data or "stagione" in data or "STAGIONE" in data:
        return episodios(item)
    for scrapedurl, scrapedtitle in matches:
        scrapedurl = urlparse.urljoin(item.url, scrapedurl)
        scrapedthumbnail = ""
        scrapedplot = ""
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 fulltitle=item.fulltitle,
                 title="[COLOR azure][[COLOR orange]" + scrapedtitle + "[/COLOR]] - " + item.title + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=item.thumbnail,
                 show=item.show,
                 plot=item.plot,
                 folder=True))

    return itemlist


# ==================================================================================================================================================

def play(item):
    itemlist = []

    data = item.url

    if "rapidcrypt" in item.url:
        data = httptools.downloadpage(item.url).data
    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        servername = re.sub(r'[-\[\]\s]+', '', videoitem.title)
        videoitem.title = "".join(
            ['[COLOR azure][[COLOR orange]' + servername.capitalize() + '[/COLOR]] - ', item.show])
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__

    return itemlist