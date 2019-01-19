# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# TheGroove360 / XBMC Plugin
# Canale 
# ------------------------------------------------------------

import re
import urlparse

from core import config
from core import servertools
from core import scrapertools
from core import logger
from core import httptools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "mondolunaticohd"
host = "http://mondolunatico.org"

def mainlist(item):
    logger.info("[mondolunaticohd] mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Film [COLOR orange]- Top IMDb[/COLOR]",
                     action="peliculas",
                     url="%s/hds/top-imdb/" % host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/popcorn_cinema_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film [COLOR orange]- Aggiornati[/COLOR]",
                     action="peliculas",
                     url="%s/hds/tag/openload/" % host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/hd_movies_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film [COLOR orange]- Alta Definizione[/COLOR]",
                     action="peliculas",
                     url="%s/hds/tag/download-hd/" % host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/blueray_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film [COLOR orange]- Lista[/COLOR]",
                     action="list",
                     url="%s/hds/lista-alfabetica/" % host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/a-z_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film [COLOR orange]- Categoria[/COLOR]",
                     action="categorias",
                     url="%s/hds/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genres_P.png"),
                Item(channel=__channel__,
                     title="[COLOR orange]Cerca...[/COLOR]",
                     action="search",
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png")]

    return itemlist

# ==============================================================================================================================================================================

def categorias(item):
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url).data
    bloque = scrapertools.get_match(data, "Film Al Cinema</a>(.*?)Richieste</a></li>")

    # Extrae las entradas 
    patron = '<li id=".*?" class=".*?"><a href="([^"]+)">(.*?)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        if scrapedtitle.startswith("Action &#038; Adventure"): 
            continue
        scrapedtitle=scrapedtitle.replace("televisione film", "Film TV")
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genre_P.png",
                 folder=True))

    return itemlist

# ====================================================================================================================================================================

def list(item):
    logger.info("[mondolunaticohd]  list")
    itemlist = []
    numpage = 14
	
    p = 1
    if '{}' in item.url:
        item.url, p = item.url.split('{}')
        p = int(p)

    # Descarga la pagina 
    data = httptools.downloadpage(item.url).data

	
    # Extrae las entradas 
    patron = '<li><b><a href="([^"]+)">(.*?)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

	
    scrapedplot = ""
    for i, (scrapedurl, scrapedtitle) in enumerate(matches):
        if (p - 1) * numpage > i: continue
        if i >= p * numpage: break
        title = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedthumbnail = ""
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="findvideos",
                 contentType="movie",
                 title="[COLOR azure]" + title + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=title,
                 show=title,
                 plot=scrapedplot,
                 folder=True), tipo='movie'))

				 
    # Extract the paginador 
    if len(matches) >= p * numpage:
        scrapedurl = item.url + '{}' + str(p + 1)
        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="list",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/successivo_P.png",
                 folder=True))

    return itemlist

# ====================================================================================================================================================================

def search(item, texto):
    logger.info("[[mondolunaticohd]] " + item.url + " search " + texto)
    item.url = host + "/hds/?s=" + texto
    try:
        if item.extra == "movie":
            return peliculas(item)
    # Continua la ricerca in caso di errore 
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

# ====================================================================================================================================================================
		
def pelis_movie_src(item):
    logger.info("[mondolunaticohd] peliculas")

    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url).data

    # Extrae las entradas 
    patron = '<div class="thumbnail animation-2">\s*<a href="([^"]+)">\s*<img src="([^"]+)" alt="(.*?)" />'
    matches = re.compile(patron, re.DOTALL).findall(data)

    scrapedplot = ""
    for scrapedurl, scrapedthumbnail, scrapedtitle, in matches:
        if "Fichier" in scrapedtitle:
          continue
        title = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="findvideos",
                 contentType="movie",
                 title="[COLOR azure]" + title + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=title,
                 show=title,
                 plot=scrapedplot,
                 folder=True), tipo='movie'))

    return itemlist

# ====================================================================================================================================================================

def peliculas(item):
    logger.info("[mondolunaticohd] peliculas")
    itemlist = []
    numpage = 14

    p = 1
    if '{}' in item.url:
        item.url, p = item.url.split('{}')
        p = int(p)

    # Descarga la pagina 
    data = httptools.downloadpage(item.url).data

    # Extrae las entradas 
    patron = '<a href="([^"]+)" data-url="" class="ml-mask jt" data-hasqtip=".*?" oldtitle="(.*?)" title="">'
    matches = re.compile(patron, re.DOTALL).findall(data)

    scrapedplot = ""
    for i, (scrapedurl, scrapedtitle) in enumerate(matches):
        if (p - 1) * numpage > i: continue
        if i >= p * numpage: break
        scrapedtitle=scrapedtitle.replace("&#8217;", "'")
        if "Fichier" in scrapedtitle:
          continue
        title = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedthumbnail = ""
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="findvideos",
                 contentType="movie",
                 title="[COLOR azure]" + title + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=title,
                 show=title,
                 plot=scrapedplot,
                 folder=True), tipo='movie'))

				 
    # Extract the paginador 
    if len(matches) >= p * numpage:
        scrapedurl = item.url + '{}' + str(p + 1)
        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="peliculas",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))
				 
    else:
         next_page = scrapertools.find_single_match(data, "</div>\s*<div id='pagination.*?>\d+</a></li><li><a rel='nofollow' class='page\s*larger' href='([^']+)'>\d+<\/a></li><li><a")
         if next_page != "":
             itemlist.append(
                 Item(channel=__channel__,
                      action="peliculas",
                      title="[COLOR orange]Successivi >>[/COLOR]",
                      url=next_page,
                      thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png"))	

    return itemlist

# ==================================================================================================================================================

def findvideos(item):
    itemlist = []
	
    data = httptools.downloadpage(item.url).data

    itemlist.extend(servertools.find_video_items(data=data))
    for videoitem in itemlist:
        servername = re.sub(r'[-\[\]\s]+', '', videoitem.title)
        videoitem.title = "".join(['[[COLOR orange]' + servername.capitalize() + '[/COLOR]] - ', item.title])
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.plot = item.plot
        videoitem.channel = __channel__

    return itemlist
