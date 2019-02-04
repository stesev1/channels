# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Thegroove360 - XBMC Plugin
# Canale  altadefinizione01casa
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

__channel__ = "altadefinizionezone"
host = "https://www.altadefinizione01.best"
headers = [['Referer', host]]

def mainlist(item):
    logger.info("[tregroove360.altadefinizione01casa] mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Film [COLOR orange]- Cinema[/COLOR]",
                     action="peliculas",
                     url="%s/cinema/" % host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/popcorn_serie_P.png"),
               Item(channel=__channel__,
                     title="[COLOR azure]Film [COLOR orange]- Novita'[/COLOR]",
                     action="peliculas_update",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/movie_new_P.png"),
               Item(channel=__channel__,
                     title="[COLOR azure]Film [COLOR orange]- Categorie[/COLOR]",
                     action="categorias",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/genres_P.png"),
               Item(channel=__channel__,
                     title="[COLOR azure]Film [COLOR orange]- Attori consigliati[/COLOR]",
                     action="actors_list",
                     url="%s/attori/" % host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/movie_actors_P.png"),
               Item(channel=__channel__,
                     title="[COLOR azure]Film [COLOR orange]- Archivio[/COLOR]",
                     action="peliculas_list",
                     url="%s/catalog/a/" % host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/all_movies_P.png"),
               Item(channel=__channel__,
                     title="[COLOR azure]Film [COLOR orange]- Lista A-Z[/COLOR]",
                     action="list_az",
                     url="%s/catalog/a/" % host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/a-z_P.png"),
               Item(channel=__channel__,
                     title="[COLOR yellow]Cerca Film...[/COLOR]",
                     action="search",
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/search_P.png")]

    return itemlist

# ==================================================================================================================================================

def categorias(item):
    logger.info("[tregroove360.altadefinizione01casa] categorias")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data
    bloque = scrapertools.get_match(data, '<ul class="kategori_list">(.*?)</ul>\s*</div>\s*</div>\s*</div>')

    # Extrae las entradas (carpetas)
    patron = '<li><a href="([^"]+)">([^<]+)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        scrapedurl = host + scrapedurl
        if "Altadefinizione01" in scrapedtitle: 
		    continue
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/genre_P.png",
                 folder=True))

    return itemlist

# ==================================================================================================================================================

def categorias_year(item):
    logger.info("[tregroove360.altadefinizione01casa] categorias")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data
    bloque = scrapertools.get_match(data, '<ul class="kategori_list">(.*?)</ul>')

    # Extrae las entradas (carpetas)
    patron = '<li><a href="([^"]+)">([^<]+)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        scrapedurl = host + scrapedurl
        if "Altadefinizione01" in scrapedtitle: 
		    continue
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/genre_P.png",
                 folder=True))

    return itemlist

# ==================================================================================================================================================

def list_az(item):
    logger.info("[tregroove360.altadefinizione01casa] list_az")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data


    # Extrae las entradas (carpetas)
    patron = '<a title=".*?" href="([^"]+)"><span>([^<]+)</span></a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        scrapedurl = host + scrapedurl
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_list",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/a-z_P.png",
                 folder=True))

    return itemlist
	
# ==================================================================================================================================================

def actors_list(item):
    logger.info("[tregroove360.altadefinizione01casa] actors_list")
    itemlist = []
    numpage = 999
	
    p = 1
    if '{}' in item.url:
        item.url, p = item.url.split('{}')
        p = int(p)
	
    data = httptools.downloadpage(item.url, headers=headers).data
    patron = '<h2>Attori consigliati su Altadefinizione01:</h2>(.*?)</div></div>'
	
    data = scrapertools.find_single_match(data, patron)
              
    patron = '<a href="([^"]+)" title="[^>]+">([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for i, (scrapedurl, scrapedtitle) in enumerate(matches):
        if (p - 1) * numpage > i: continue
        if i >= p * numpage: break
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/movie_actors_P.png",
                 folder=True))

    # Extrae el paginador
    if len(matches) >= p * numpage:
        scrapedurl = item.url + '{}' + str(p + 1)
        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="actors_list",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/next_1.png",
                 folder=True))

    return itemlist

# ==================================================================================================================================================

def peliculas_list(item):
    logger.info("[tregroove360.altadefinizione01casa] peliculas_list")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = '<img\s*[^>]+src="([^"]+)[^>]+>\s*</a>\s*</td>\s*[^>]+>'
    patron += '<h2>\s*<a href="([^"]+)"\s*title=".*?">([^<]+)</a>\s*</h2></td>.*?'
    patron += '<td class="mlnh-3">(.*?)</td>.*?<td class="mlnh-4">(.*?)</td>'
    matches = re.compile(patron, re.DOTALL).finditer(data)

    for match in matches:
        scrapedplot = ""
        quality = scrapertools.unescape(match.group(5))
        year = scrapertools.unescape(match.group(4))
        scrapedtitle = scrapertools.unescape(match.group(3))
        scrapedurl = scrapertools.unescape(match.group(2))
        scrapedthumbnail = urlparse.urljoin(item.url, match.group(1))

        if year:
          scrapetitle=scrapedtitle.strip() + " (" + year + ")"
        else:
          scrapetitle=scrapedtitle			
        if quality:
         quality = " ([COLOR yellow]" + quality + "[/COLOR])"
        if year:
         year = " ([COLOR yellow]" + year + "[/COLOR])"

		
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 contentType="movie",
                 fulltitle=scrapetitle,
                 show=scrapetitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]" + year + quality,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='movie'))

    # Extrae el paginador
    patronvideos = 'href="([^"]+)">&raquo;</a></i>'
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

# ==================================================================================================================================================	

def peliculas_update(item):
    logger.info("[tregroove360.altadefinizione01casa] peliculas_update")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    patron = '<div class="son_eklenen">.*?<div class="son_eklenen_head"></div>(.*?)<div class="son_eklenen">'
    data = scrapertools.find_single_match(data, patron)

    # Extrae las entradas (carpetas)
    patron = '</div>\s*<a href="([^"]+)">\s*' \
             '<img width=".*?"\s*height=".*?" src="([^"]+)" [^>]+ alt="([^<]+)"\s*title="".*?/>.*?' \
             '</a>\s*<div class="trdublaj">\s*(.*?)</div>\s*[^>]+>(.*?)\s*<' \
             '.*?<li>\s*<span class="ml[^"]+">(.*?)<\/.*?span>\s*<\/li>\s*' \
             '<li><span class="ml-label">([^<]+)</span></li>.*?<p>(.*?)</p>'
    matches = re.compile(patron, re.DOTALL).finditer(data)

    for match in matches:
        scrapedplot = scrapertools.unescape(match.group(8))
        year = scrapertools.unescape(match.group(7))
        rating = scrapertools.unescape(match.group(6))
        sub = scrapertools.unescape(match.group(5))
        quality = scrapertools.unescape(match.group(4))
        scrapedtitle = scrapertools.unescape(match.group(3))
        scrapedthumbnail = urlparse.urljoin(item.url, match.group(2))
        scrapedurl = scrapertools.unescape(match.group(1))
        if year:
          scrapetitle=scrapedtitle.strip() + " (" + year + ")"
        else:
          scrapetitle=scrapedtitle	
        if sub:
         sub = " ([COLOR yellow]" + sub + "[/COLOR])"
        if quality:
         quality = " ([COLOR yellow]" + quality + "[/COLOR])"
        if year:
         year = " ([COLOR yellow]" + year + "[/COLOR])"
         scrapetitle=scrapedtitle + " (" + year + ")"
        if rating:
         rating=rating.replace("<b>", "")
         rating = " ([COLOR yellow]" + rating + "[/COLOR])"

         
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 contentType="movie",
                 fulltitle=scrapetitle,
                 show=scrapetitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR] " + sub + year + quality + rating,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='movie'))

    # Extrae el paginador
    patronvideos = 'href="([^"]+)">&raquo;</a></i>'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_update",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/next_1.png",
                 folder=True))

    return itemlist

# ==================================================================================================================================================	
		
def peliculas(item):
    logger.info("[tregroove360.altadefinizione01casa] peliculas")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = '<h2>\s*<a href="([^"]+)">([^"]+)<\/a>\s*<\/h2>\s*[^>]+>[^>]+.*?\s*'
    patron += '</div>\s*<a href[^>]+>[^>]+src="([^"]+)"[^>]+>\s*</a>\s*'
    patron += '<div class="trdublaj">\s*(.*?)</div>\s*[^>]+>(.*?)\s*<'
    patron += '.*?<li>\s*<span class="ml[^"]+">(.*?)<\/.*?span>\s*<\/li>\s*' 
    patron += '<li><span class="ml-label">([^<]+)</span></li>.*?<p>(.*?)</p>'
    matches = re.compile(patron, re.DOTALL).finditer(data)

    for match in matches:
        scrapedplot = scrapertools.unescape(match.group(8))
        year = scrapertools.unescape(match.group(7))
        rating = scrapertools.unescape(match.group(6))
        sub = scrapertools.unescape(match.group(5))
        quality = scrapertools.unescape(match.group(4))
        scrapedthumbnail = urlparse.urljoin(item.url, match.group(3))
        scrapedtitle = scrapertools.unescape(match.group(2))
        scrapedurl = scrapertools.unescape(match.group(1))
        if year:
          scrapetitle=scrapedtitle.strip() + " (" + year + ")"
        else:
          scrapetitle=scrapedtitle		
        if sub:
         sub = " ([COLOR yellow]" + sub + "[/COLOR])"
        if quality:
         quality = " ([COLOR yellow]" + quality + "[/COLOR])"
        if year:
         year = " ([COLOR yellow]" + year + "[/COLOR])"

        if rating:
         rating=rating.replace("<b>", "")
         rating = " ([COLOR yellow]" + rating + "[/COLOR])"
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 contentType="movie",
                 fulltitle=scrapetitle,
                 show=scrapetitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR] " + sub + year + quality + rating,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='movie'))

    # Extrae el paginador
    patronvideos = 'href="([^"]+)">&raquo;</a></i>'
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

# ==================================================================================================================================================
	
def findvideos(item):
    logger.info("[tregroove360.altadefinizione01casa] findvideos")
    itemlist = []

    # Descarga la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data

    # Estrae i contenuti 
    patron = '</a>\s*<a href="[^>]+" data-link="([^"]+)">\s*<li class="part">'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl in matches:
        if not "http" in scrapedurl:
          scrapedurl = "http:" + scrapedurl
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
	
# ==================================================================================================================================================

def search(item, texto):
    logger.info("[tregroove360.altadefinizione01casa] " + item.url + " search " + texto)
    item.url = host + "/?do=search&subaction=search&story=" + texto
    try:
        return peliculas(item)

    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

# ==================================================================================================================================================


