# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Thegroove360 - XBMC Plugin
# Canale  cineblog_life
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

__channel__ = "cineblog_life"
host = "https://www.cineblog.life"
headers = [['Referer', host]]

def mainlist(item):
    logger.info("[thegroove360.cineblog_life] mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Film - [COLOR orange]Novita'[/COLOR]",
                     action="peliculas",
                     url="%s/filmlist/" % host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/popcorn_serie_P.png"),
               Item(channel=__channel__,
                     title="[COLOR azure]Film - [COLOR orange]HD[/COLOR]",
                     action="peliculas",
                     extra="movie",
                     url=host+"/categorie/film-in-altadefinizione",
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/hd_movies_P.png"),
               Item(channel=__channel__,
                     title="[COLOR azure]Film - [COLOR orange]Sub Ita[/COLOR]",
                     action="peliculas",
                     extra="movie",
                     url="%s/categorie/film-sub-ita/" % host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/movie_sub_P.png"),
               Item(channel=__channel__,
                     title="[COLOR azure]Film - [COLOR orange]Categoria[/COLOR]",
                     action="categorias",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/genres_P.png"),
               Item(channel=__channel__,
                     title="[COLOR azure]Film - [COLOR orange]Lista A-Z[/COLOR]",
                     action="categorias_list",
                     extra="movie",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/a-z_P.png"),
               Item(channel=__channel__,
                     title="[COLOR azure]Serie TV - [COLOR orange]Lista[/COLOR]",
                     action="peliculas_tv",
                     extra="serie",
                     url="%s/serie-tv/" % host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/a-z_P.png"),
                Item(channel=__channel__,
                     title="[COLOR orange]Cerca...[/COLOR]",
                     action="search",
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/search_P.png")]

    return itemlist

# ===================================================================================================================================================	

def categorias(item):
    logger.info("[thegroove360.cineblog_life] categorias")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data

    # Descarga la pagina
    bloque = scrapertools.get_match(data, 'Categorie</a>(.*?)</ul>')

    # Extrae las entradas (carpetas)
    patron = '<li id[^>]+"><a href="([^"]+)">(.*?)</a>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 extra=item.extra,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/genre_P.png",
                 url=scrapedurl))

    return itemlist

# ===================================================================================================================================================
	
def categorias_list(item):
    logger.info("[thegroove360.cineblog_life] categorias")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data
    bloque = scrapertools.get_match(data, '<ul class="AZList">(.*?)</ul>')
                   
    # Extrae las entradas (carpetas)
    patron = '<a href="([^"]+)">([^<]+)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_list",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 extra=item.extra,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/genre_P.png",
                 url=scrapedurl))

    return itemlist	
	
# ===================================================================================================================================================	
	
def search(item, texto):
    logger.info("[cineblog_life.py] " + item.url + " search " + texto)
    item.url = host + "?s=" + texto
    try:
        return peliculas_search(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

# ===================================================================================================================================================
		
def peliculas_search(item):
    logger.info("[thegroove360.cineblog_life] peliculas")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = r'<a href="([^"]+)">\s*<div class="Image">\s*<figure clas[^>]+>'
    patron += r'<img[^>]+src="([^"]+)"\sclass[^>]+></figure>.*?'
    patron += r'<h3 class="Title">(.*?)</h3>(.*?)'
    patron += r'<p>(.*?)</p>'
    matches = re.compile(patron, re.DOTALL).finditer(data)

    for match in matches:
        scrapedplot = scrapertools.unescape(match.group(5))
        info = scrapertools.unescape(match.group(4))
        scrapedtitle = scrapertools.unescape(match.group(3))
        scrapedthumbnail = scrapertools.unescape(match.group(2))
        scrapedurl = urlparse.urljoin(item.url, match.group(1))
        scrapedtitle = scrapedtitle.replace("&", "e")
        if "1080p" in info or "720p" in info:
         quality = " ([COLOR yellow]HD[/COLOR])"
        else:
         if "360p" in info:
          quality = " ([COLOR yellow]LQ[/COLOR])"
         else:
          quality = ""         
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos" if not "serie" in scrapedurl else "episodios",
                 contentType="movie",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title=scrapedtitle + quality,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='movie' if not "serie" in scrapedurl else "tv"))

    return itemlist		

# ===================================================================================================================================================
		
def peliculas(item):
    logger.info("[thegroove360.cineblog_life] peliculas")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = r'<a href="([^"]+)">\s*<div class="Image">\s*<figure clas[^>]+><img[^>]+src="([^"]+)"\s*'
    patron += r'class[^>]+><\/figure>\s*<\/div>\s*<h3 class="Title">(.*?)<\/h3>.*?'
    patron += r'<span[^>]+>([^<]+)</span><span class="Qlty">([^<]+)</span>.*?'
    patron += r'.*?<p>(.*?)</p>'
    matches = re.compile(patron, re.DOTALL).finditer(data)

    for match in matches:
        scrapedplot = scrapertools.unescape(match.group(6))
        quality = scrapertools.unescape(match.group(5))
        year = scrapertools.unescape(match.group(4))
        scrapedtitle = scrapertools.unescape(match.group(3))
        scrapedthumbnail = scrapertools.unescape(match.group(2))
        scrapedurl = urlparse.urljoin(item.url, match.group(1))
        scrapedtitle = scrapedtitle.replace("&", "e")
        if "." in year or "h" in year:
          year=""
        else:
          year= " ([COLOR yellow]" + year + "[/COLOR])"
        if "1080" in quality or "720" in quality:
          quality = " ([COLOR yellow]HD[/COLOR])"
        else:
          if "Unknown" in quality:
           quality = " ([COLOR yellow]NA[/COLOR])"
          else:
           quality = " ([COLOR yellow]LQ[/COLOR])"
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 contentType="movie",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]" + year  + quality,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='movie'))


    patronvideos = '<a class="next page-numbers" href="([^"]+)">'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/next_1.png",
                 folder=True))

    return itemlist

# ===================================================================================================================================================	

def peliculas_list(item):
    logger.info("[thegroove360.cineblog_life] peliculas")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = r'src="([^"]+)"\s*class="[^>]+>\s*<\/a>\s*<\/td>\s*<td[^>]+>\s*'
    patron += r'<a href="([^"]+)"\s*class[^>]+>\s*<strong>([^<]+)<\/strong>.*?'
    patron += r'<span class="Qlty">([^<]+)</span>'
    matches = re.compile(patron, re.DOTALL).finditer(data)

    for match in matches:
        scrapedplot = ""
        quality = scrapertools.unescape(match.group(4))
        scrapedtitle = scrapertools.unescape(match.group(3))
        scrapedurl = urlparse.urljoin(item.url, match.group(2))
        scrapedthumbnail = scrapertools.unescape(match.group(1))
        scrapedtitle = scrapedtitle.replace("&", "e").replace("’", "'")
        if "1080" in quality or "720" in quality:
          quality = " ([COLOR yellow]HD[/COLOR])"
        else:
          if "Unknown" in quality:
           quality = " ([COLOR yellow]NA[/COLOR])"
          else:
           quality = " ([COLOR yellow]LQ[/COLOR])"
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 contentType="movie",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]" + quality,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='movie'))


    patronvideos = '<a class="next page-numbers" href="([^"]+)">'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_list",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/next_1.png",
                 folder=True))

    return itemlist

# ===================================================================================================================================================

def peliculas_tv(item):
    logger.info("[thegroove360.cineblog_life] peliculas")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = r'<a href="([^"]+)">\s*<div class="Image">\s*'
    patron += r'<figure class[^>]+>\s*<img[^>]+src="([^"]+)"\s*class[^>]+>.*?'
    patron += r'<h3 class="Title">([^<]+)</h3>\s*<span class="Year">([^<]+)</span>.*?'
    patron += r'.*?<p>(.*?)</p>'
    matches = re.compile(patron, re.DOTALL).finditer(data)

    for match in matches:
        scrapedplot = scrapertools.unescape(match.group(5))
        year = scrapertools.unescape(match.group(4))
        scrapedtitle = scrapertools.unescape(match.group(3))
        scrapedthumbnail = scrapertools.unescape(match.group(2))
        scrapedurl = urlparse.urljoin(item.url, match.group(1))
        scrapedtitle = scrapedtitle.replace("&", "e")
        if "." in year or "h" in year:
          year=""
        else:
          year= " ([COLOR yellow]" + year + "[/COLOR])"
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 contentType="serie",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]" + year,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='tv'))


    patronvideos = '<a class="next page-numbers" href="([^"]+)">'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_tv",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/next_1.png",
                 folder=True))

    return itemlist
	
# ===================================================================================================================================================	

def episodios(item):
    logger.info("[thegroove360.cineblog_life] categorias")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data

                   
    # Extrae las entradas (carpetas)
    patron = r'<td class="MvTbImg B"><a href="([^"]+)" .*?'
    patron += r'<\/td>\s*<td class="MvTbTtl"><a href="[^\d]+([^"]+)">([^<]+)<\/a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedep, scrapedtitle in matches:
        scrapedep = scrapedep.replace("/", "")
        ep=" [COLOR orange]" + scrapedep + "[/COLOR] - "
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 contentType="tv",
                 title=ep + "[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 fulltitle=item.fulltitle + " - " + scrapedep,
                 show=ep + " - " + scrapedtitle,
                 url=scrapedurl,
                 extra="tv",
                 plot="[COLOR orange]" + item.fulltitle + "[/COLOR] " + item.plot,
                 thumbnail=item.thumbnail,
                 folder=True))

    return itemlist
	
# ===================================================================================================================================================
	
def findvideos(item):
    logger.info("[streamondemand- animesenzalimiti] categorie")
    itemlist = []

    data = httptools.downloadpage(item.url).data
    blocco = scrapertools.get_match(data, r'<th>Risoluzione</th>(.*?)</table>')
    patron = r'<td><a rel="nofollow" target="_blank" href="([^"]+)" class="Button STPb">[^<]+</a></td>\s*'
    patron += r'<td><span><img src=".*?" alt=".*?">\s*([^<]+)</span></td>\s*'
    patron += r'<td><span>.*?</span></td>\s*<td><span>([^<]+)</span></td>'
    matches = re.compile(patron, re.DOTALL).findall(blocco)

    for scrapedurl, scrapedtitle, quality in matches:
        scrapedurl = scrapedurl.replace("#038;", "")
        quality = quality.replace("1080p", "HD")
        quality = quality.replace("Unknown", "NA")

        itemlist.append(
                Item(channel=__channel__,
                     action="play",
                     fulltitle=item.fulltitle,
                     title="[COLOR azure][[COLOR orange]" + scrapedtitle  + " - " + quality + "[/COLOR]] - " + item.fulltitle + "[/COLOR]",
                     url=scrapedurl,
                     show=item.title,
                     plot=item.plot,
                     thumbnail=item.thumbnail,
                     folder=True))
					 
    data = httptools.downloadpage(item.url).data
    patron = r'<a class="link-catch-all" data-counter="\d+"><b>([^<]+)</b></a></li>\s*</ul></div>\s*'
    patron += r'<div data-counter="\d+" class="tabs-catch-all"  data-src="([^<]+)" ></div>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedtitle, scrapedurl in matches:
        scrapedurl = scrapedurl.replace("#038;", "")

        itemlist.append(
                Item(channel=__channel__,
                     action="play",
                     fulltitle=item.fulltitle,
                     title="[COLOR azure][[COLOR orange]" + scrapedtitle  + "[/COLOR]] - " + item.fulltitle + "[/COLOR]",
                     url=scrapedurl,
                     show=item.title,
                     plot=item.plot,
                     thumbnail=item.thumbnail,
                     folder=True))

    return itemlist

# ===================================================================================================================================================
	
def play(item):
    logger.info()
    data = httptools.downloadpage(item.url).data
    
    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        servername = re.sub(r'[-\[\]\s]+', '', videoitem.title)
        videoitem.title = "".join(["[COLOR azure]"+item.fulltitle, ' - [[COLOR orange]'+servername.capitalize()+'[/COLOR]]'])
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__
    return itemlist
