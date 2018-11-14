# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# StreamOnDemand-PureITA / XBMC Plugin
# Canal guardarefilm
# http://www.mimediacenter.info/foro/viewtopic.php?f=36&t=7808
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

__channel__ = "guardarefilm"
host = "https://www.guardarefilm.pink"
headers = [['Referer', host]]

def mainlist(item):
    logger.info("streamondemand-pureita guardarefilm mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Film & Serie Tv [COLOR orange]- Top 100[/COLOR]",
                     action="pelis_top",
                     url="%s/top100.html" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/popcorn_new.png"),
	            Item(channel=__channel__,
                     title="[COLOR azure]Film [COLOR orange]- Novita'[/COLOR]",
                     action="peliculas",
                     url="%s/streaming-al-cinema/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/movie_new_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film [COLOR orange]- Categorie[/COLOR]",
                     action="categorias",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genres_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film [COLOR orange]- HD[/COLOR]",
                     action="peliculas",
                     url="%s/film-streaming-hd/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/hd_movies_P.png"),
                #Item(channel=__channel__,
                     #title="[COLOR azure]Film [COLOR orange]- Animazione[/COLOR]",
                     #action="peliculas",
                     #url="%s/streaming-cartoni-animati/" % host,
                     #thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/animated_movie_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV[/COLOR]",
                     action="peliculas_tv",
                     extra="serie",
                     url="%s/serie-tv-streaming/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/tv_series_P.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca Film...[/COLOR]",
                     action="search",
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca Serie TV...[/COLOR]",
                     action="search",
                     extra="serie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png")]
    return itemlist

# ===================================================================================================================================================

def categorias(item):
    logger.info("streamondemand-pureita guardarefilm categorias")
    itemlist = []
    data = httptools.downloadpage(item.url, headers=headers).data

    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data, 'Genere</a>\s*<ul class="reset dropmenu">(.*?)</ul>')

    # The categories are the options for the combo
    patron = '<li><a href="([^"]+)">([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        if "Film" in scrapedtitle:
		   scrapedtitle = scrapedtitle.replace("Film", "[COLOR orange][B]" + "Film - " + "[/B][/COLOR]")
        scrapedtitle = scrapedtitle.replace(" in ", "")
        scrapedtitle = scrapedtitle.replace("Streaming", "")
        scrapedtitle = scrapedtitle.replace("lingua originale", "Sottotitolati")
        scrapedurl = urlparse.urljoin(item.url, scrapedurl)
        scrapedthumbnail = ""
        scrapedplot = ""
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genre_P.png",
                 plot=scrapedplot))

    return itemlist

# ===================================================================================================================================================

def search(item, texto):
    logger.info("[streamondemand-pureita guardarefilm] " + item.url + " search " + texto)
    item.url = '%s?do=search_advanced&q=%s&section=0&director=&actor=&year_from=&year_to=' % (host, texto)
    try:
        if item.extra == "movie":
            return peliculas(item)
        if item.extra == "serie":
            return peliculas_tv(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

# ===================================================================================================================================================

def peliculas(item):
    logger.info("streamondemand-pureita guardarefilm peliculas")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = '<div class="poster"><a href="([^"]+)"><img src="([^"]+)"\s*alt=""><span class[^>]+>'
    patron += '</span></a></div>\s*<div class[^>]+><a href[^>]+>([^<]+)</a></div>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        scrapedthumbnail = urlparse.urljoin(item.url, scrapedthumbnail)
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle).strip()
        scrapedplot = ""

        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos" if not "serie-tv" in scrapedurl else "episodios",
                 contentType="movie",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='movie' if not "serie-tv" in scrapedurl else "tv"))

    # Extrae el paginador
    patronvideos = '<span>\d+</span>\s*<a href="([^"]+)">\d+</a>'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))

    return itemlist

# ===================================================================================================================================================

def peliculas_tv(item):
    logger.info("streamondemand-pureita guardarefilm peliculas")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = '<div class="poster"><a href="([^"]+)"><img src="([^"]+)"\s*alt=""><span class[^>]+>'
    patron += '</span></a></div>\s*<div class[^>]+><a href[^>]+>([^<]+)</a></div>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        scrapedplot = ""
        scrapedthumbnail = urlparse.urljoin(item.url, scrapedthumbnail)
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle).strip()

        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios" if "serie-tv" in scrapedurl  else "findvideos",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 contentType="tvshow",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='tv' if "serie-tv" in scrapedurl  else "movie"))

    # Extrae el paginador
    patronvideos = '<span>\d+</span>\s*<a href="([^"]+)">\d+</a>'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_tv",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))

    return itemlist

# ===================================================================================================================================================

def pelis_top(item):
    logger.info("streamondemand-pureita guardarefilm peliculas")
    itemlist = []
    PERPAGE = 10

    p = 1
    if '{}' in item.url:
        item.url, p = item.url.split('{}')
        p = int(p)
	
    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = r'<li>\s*<span class="top100_title"><a href="([^"]+)">([^<]+)</a></span>'
    matches = re.compile(patron).findall(data)

    for i, (scrapedurl, scrapedtitle) in enumerate(matches):
        if (p - 1) * PERPAGE > i: continue
        if i >= p * PERPAGE: break
        scrapedplot = ""
        scrapedthumbnail = ""
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios" if "serie-tv" in scrapedurl  else "findvideos",
                 extra=item.extra,
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 plot=scrapedplot,
                 folder=True), tipo='tv' if "serie-tv" in scrapedurl  else "movie"))
				 
    if len(matches) >= p * PERPAGE:
        scrapedurl = item.url + '{}' + str(p + 1)
        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="pelis_top",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))

    return itemlist

# ===================================================================================================================================================

def episodios(item):
    logger.info("streamondemand-pureita guardarefilm episodios")
    itemlist = []

    # Descarga la página
    data = httptools.downloadpage(item.url, headers=headers).data

    patron = r'<li id="serie[^"]+"\s*data-title="[^\d+]+\s*([^"]+)">'
    patron += r'[^>]+>[^>]+>[^>]+>[^>]+>\s*<span class="right">(.*?)</span>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedtitle, scrapedurl in matches:
        if "(presto in streaming)" in scrapedtitle:
          note=" ([COLOR orange]Prossimamente[/COLOR])"
        else:
          note=""
        scrapedtitle = scrapedtitle.replace("(presto in streaming)", "")
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos_tv",
                 contentType="episode",
                 title=scrapedtitle + note,
                 url=item.url,
                 thumbnail=item.thumbnail,
                 extra=scrapedurl,
                 fulltitle=item.fulltitle + " - " + scrapedtitle,
                 plot="[COLOR orange]" + item.fulltitle + "[/COLOR] " + item.plot,
                 show=item.show))

    if config.get_library_support() and len(itemlist) != 0:
        itemlist.append(
            Item(channel=__channel__,
                 title="[COLOR red][I]" + "Aggiungi alla libreria" + "[/I][/COLOR]",
                 url=item.url,
                 action="add_serie_to_library",
                 extra="episodios",
                 show=item.show))

    return itemlist

# ===================================================================================================================================================
	
def findvideos_tv(item):
    logger.info("streamondemand-pureita guardarefilm findvideos")

    # Descarga la página
    data = item.extra
	
    patron = 'data-link="([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)
	
    for scrapedurl in matches:
        if not "http" in scrapedurl:
          scrapedurl= "https:" + scrapedurl
        data += httptools.downloadpage(scrapedurl).data
		
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

# ===================================================================================================================================================
	
def findvideos(item):
    logger.info("[StreamOnDemand-PureITA GuardaFilm] findvideos")
    itemlist = []
	
    data = httptools.downloadpage(item.url, headers=headers).data 
    patron = 'data-link="([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)
	
    for scrapedurl in matches:
        if not "http" in scrapedurl:
          scrapedurl= "https:" + scrapedurl

        data += httptools.downloadpage(scrapedurl).data

    for videoitem in servertools.find_video_items(data=data):
        servername = re.sub(r'[-\[\]\s]+', '', videoitem.title)
        videoitem.title = "".join(['[COLOR azure][[COLOR orange]' + servername.capitalize() + '[/COLOR]] - ', item.title])
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.show = item.show
        videoitem.plot = item.plot
        videoitem.channel = __channel__
        itemlist.append(videoitem)

    return itemlist
