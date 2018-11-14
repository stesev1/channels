# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# StreamOnDemand-PureITA / XBMC Plugin
# Canale  altadefinizione01_biz
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

__channel__ = "altadefinizione01_biz"
host = "http://altadefinizione01.link"
headers = [['Referer', host]]


def mainlist(item):
    logger.info("streamondemand-pureita.altadefinizione01_biz mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Film [COLOR orange]- Al Cinema[/COLOR]",
                     action="peliculas",
                     url="%s/film-del-cinema/" % host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/popcorn_cinema_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film [COLOR orange]- Aggiornati[/COLOR]",
                     action="peliculas",
                     url="%s/film/" % host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/movie_new_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film [COLOR orange]- Categorie[/COLOR]",
                     action="categorias",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genres_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film [COLOR orange]- Sub ITA[/COLOR]",
                     action="peliculas",
                     url="%s/film-sub-ita/" % host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/movie_sub_P.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca Film...[/COLOR]",
                     action="search",
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV[/COLOR]",
                     action="peliculas_tv",
                     url="%s/serie-tv-streaming/" % host,
                     extra="serie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/tv_series_P.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca Serie TV...[/COLOR]",
                     action="search",
                     extra="serie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png")]

    return itemlist

# ==================================================================================================================================================
	
def categorias(item):
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data
    bloque = scrapertools.get_match(data, '<ul class="listSubCat" id="Film">(.*?)</ul>')

    # Extrae las entradas (carpetas)
    patron = '<li><a href="([^"]+)">(.*?)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        scrapedurl = host + scrapedurl
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genre_P.png",
                 folder=True))

    return itemlist

# ==================================================================================================================================================
	
def search(item, texto):
    logger.info("streamondemand-pureita altadefinizione01_biz " + item.url + " search " + texto)
    item.url = host + "/?do=search&subaction=search&story=" + texto
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

# ==================================================================================================================================================		
		
def peliculas(item):
    logger.info("streamondemand-pureita altadefinizione01_biz peliculas")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = '<span class[^>]+>([^<]+)<\/span> <span class="ssound">([^<]+)</span>'
    patron += '<a href="([^"]+)"><img src="([^"]+)" class="[^>]+" alt="([^<]+)"\s*height[^>]+>'
    matches = re.compile(patron, re.DOTALL).finditer(data)

    for match in matches:
        scrapedplot = ""
        scrapedtitle = scrapertools.unescape(match.group(5))
        scrapedthumbnail = urlparse.urljoin(item.url, match.group(4))
        scrapedurl = urlparse.urljoin(item.url, match.group(3))
        lang = scrapertools.unescape(match.group(2))
        lang =lang.replace("Italiano", "ITA")
        quality = scrapertools.unescape(match.group(1))
        quality =" ([COLOR yellow]" + quality +"[/COLOR])"
        lang =" ([COLOR yellow]" + lang +"[/COLOR])"
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 contentType="movie",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]" + quality + lang,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='movie'))

    # Extrae el paginador
    patronvideos = '<a href="([^"]+)">Avanti →</a>'
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

# ==================================================================================================================================================	
	
def peliculas_tv(item):
    logger.info("streamondemand-pureita altadefinizione01_biz peliculas")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = '<span class[^>]+>([^<]+)<\/span> <span class="ssound">([^<]+)</span>'
    patron += '<a href="([^"]+)"><img src="([^"]+)" class="[^>]+" alt="([^<]+)"\s*height[^>]+>'
    matches = re.compile(patron, re.DOTALL).finditer(data)

    for match in matches:
        scrapedplot = ""
        scrapedtitle = scrapertools.unescape(match.group(5))
        scrapedthumbnail = urlparse.urljoin(item.url, match.group(4))
        scrapedurl = urlparse.urljoin(item.url, match.group(3))
        lang = scrapertools.unescape(match.group(2))
        quality = scrapertools.unescape(match.group(1))
        quality = " ([COLOR yellow]" + quality + "[/COLOR])"
        lang = lang.replace("Italiano", "ITA")
        lang = " ([COLOR yellow]" + lang + "[/COLOR])"
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 contentType="tv",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]" + quality + lang,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='tv'))

    # Extrae el paginador
    patronvideos = '<a href="([^"]+)">Avanti →</a>'
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

# ==================================================================================================================================================	
	
def episodios(item):
    logger.info("streamondemand-pureita altadefinizione01_biz episodios")

    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data

    patron = '<small class="text-muted">\s*([^<]+)</small>\s*([^<]+)</div>\s*<div class=".*?">\s*'
    patron += '<div class=".*?">\s*<a href[^>]+link="([^"]+)"><small class[^>]+>\s*</small>[^<]+</a>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedep, scrapedtitle, scrapedurl  in matches:
        scrapedplot = ""
        scrapedthumbnail = ""
        scrapedtitle = scrapedtitle.replace('Stai guardando: ', '').replace("&nbsp;", "").strip()
        scrapedep = scrapedep.replace("ep", "Ep. ")

        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 fulltitle=item.fulltitle + " - " + scrapedep + " - " + scrapedtitle,
                 show=item.show + " - " + scrapedep + " - " + scrapedtitle,
                 title="[COLOR azure]" + scrapedep + " - " + scrapedtitle + "[/COLOR]",
                 contentType="episode",
                 url=scrapedurl,
                 thumbnail=item.thumbnail,
                 plot="[COLOR orange]" + item.fulltitle + "[/COLOR] " + item.plot,
                 folder=True))

    if config.get_library_support() and len(itemlist) != 0:
        itemlist.append(
            Item(channel=__channel__,
                 title="Aggiungi alla libreria",
                 url=item.url,
                 action="add_serie_to_library",
                 extra="episodios",
                 show=item.show))
        itemlist.append(
            Item(channel=__channel__,
                 title="Scarica tutti gli episodi della serie",
                 url=item.url,
                 action="download_all_episodes",
                 extra="episodios",
                 show=item.show))

    return itemlist

# ==================================================================================================================================================		
	
def findvideos(item):

    data = httptools.downloadpage(item.url, headers=headers).data

    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        servername = re.sub(r'[-\[\]\s]+', '', videoitem.title)
        videoitem.title = "".join(['[[COLOR orange]' + servername.capitalize() + '[/COLOR]] - ', item.title])
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.plot = item.plot
        videoitem.channel = __channel__

    return itemlist	

# ==================================================================================================================================================
# ==================================================================================================================================================
# ==================================================================================================================================================
'''	
def findvideos_tv(item):
    itemlist=[]
    data = httptools.downloadpage(item.url, headers=headers).data

    elemento = scrapertools.find_single_match(data, 'file: "(.*?)",')

    itemlist.append(Item(channel=__channel__,
                         action="play",
                         title=item.title,
                         url=elemento,
                         thumbnail=item.thumbnail,
                         fulltitle=item.fulltitle,
                         show=item.fulltitle))
    return itemlist'''



