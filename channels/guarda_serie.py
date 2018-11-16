# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# StreamOnDemand-PureITA / XBMC Plugin
# Canal guarda_serie
# http://www.mimediacenter.info/foro/viewtopic.php?f=36&t=7808
# ------------------------------------------------------------

import base64
import re
import urlparse

from core import config
from core import httptools
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "guarda_serie"
host = "https://guardaserie.site"
headers = [['Referer', host]]


def mainlist(item):
    logger.info("[guarda_serie] mainlist")

    itemlist = [
        Item(channel=__channel__,
             title="[COLOR azure]Serie TV[COLOR orange] - Ultime Aggiornate[/COLOR]",
             action="peliculas_update",
             url=host,
             extra="serie",
             thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/new_tvshows_P.png"),
        Item(channel=__channel__,
             title="[COLOR azure]Serie TV[COLOR orange] - Novita'[/COLOR]",
             action="peliculas",
             url="%s/serietv/" % host,
             extra="serie",
             thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/tv_series_P.png"),
        Item(channel=__channel__,
             title="[COLOR azure]Serie TV[COLOR orange] - TV Show[/COLOR]",
             action="peliculas",
             url="%s/genre/tv-show/" % host,
             extra="serie",
             thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/tv_serie_P.png"),
        Item(channel=__channel__,
             title="[COLOR azure]Serie TV[COLOR orange] - Animazione[/COLOR]",
             action="peliculas",
             url="%s/genre/animazione-e-bambini/" % host,
             extra="serie",
             thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/animation_P.png"),
        Item(channel=__channel__,
             title="[COLOR azure]Serie TV[COLOR orange] - Categorie[/COLOR]",
             action="genere",
             url=host,
             thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genres_P.png"),
        Item(channel=__channel__,
             title="[COLOR orange]Cerca...[/COLOR]",
             action="search",
             extra="movie",
             thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png")]

    return itemlist

# ==================================================================================================================================================

def search(item, texto):
    logger.info("[guarda_serie] " + item.url + " search " + texto)

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


def peliculas_search(item):
    logger.info("[guarda_serie] peliculas_search")

    itemlist = []

    # Descarga la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data
	
    patron = '<div class="thumbnail animation-2">\s*<a href="([^"]+)">\s*'
    patron += '<img src="([^"]+)"\s*alt="([^<]+)" />.*?<p>(.*?)</p>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle, scrapedplot  in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle).strip()
        scrapedtitle = scrapedtitle.replace(" Streaming HD", "").replace(" streaming", "")
        scrapedtitle = scrapedtitle.replace("-)", ")").replace("’", "'")
        scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)

        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=scrapedtitle,
                 plot=scrapedplot,
                 show=scrapedtitle), tipo='tv'))

    # Paginación
    next_page = scrapertools.find_single_match(data, '<a href="([^"]+)" ><span class="icon-chevron-right">')
    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=next_page,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png"))

    return itemlist

# ==================================================================================================================================================		

def genere(item):
    logger.info("[guarda_serie] genere")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data
    bloque = scrapertools.get_match(data, 'Animazione e Bambini</a> <i>(.*?)</ul></nav>')

    # Extrae las entradas (carpetas)
    patron = '<li class="cat-item cat-item-\d+"><a href="([^"]+)" >([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        if "Tv Show" in scrapedtitle or "Serie Tv" in scrapedtitle:
          continue
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genre_P.png",
                 folder=True))

    return itemlist

# ==================================================================================================================================================

def peliculas(item):
    logger.info("[guarda_serie] peliculas")

    itemlist = []

    # Descarga la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data	
	
    patron = '<div class="poster">\s*<img\s*src="([^"]+)"\s*alt="([^"]+)">\s*'
    patron += '<div class="rating">[^>]+></span>\s*([^<]+)</div>\s*[^>]+>\s*[^>]+>([^<]+)</span>\s*'
    patron += '</div>\s*<a href="([^"]+)">[^>]+></div>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedthumbnail, scrapedtitle, rating, quality, scrapedurl in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle).strip()
        if rating=="10" or rating=="0":
           rating = ""
        else:
           rating = " ([COLOR yellow]" + rating + "[/COLOR])"
        quality = " ([COLOR yellow]" + quality + "[/COLOR])"
        scrapedtitle = scrapedtitle.replace(" Streaming HD", "").replace(" streaming", "")
        scrapedtitle = scrapedtitle.replace("-)", ")").replace("’", "'")
        scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)


        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 contentType="episode",
                 show=scrapedtitle,
                 title=scrapedtitle + quality + rating,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=scrapedtitle,
                 plot="",
                 folder=True), tipo='tv'))

    # Paginación
    next_page = scrapertools.find_single_match(data, '<a href="([^"]+)" ><span class="icon-chevron-right">')
    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=next_page,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png"))

    return itemlist

# ==================================================================================================================================================

def peliculas_update(item):
    logger.info("[guarda_serie] peliculas_last")

    itemlist = []

    # Descarga la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data
    bloque = scrapertools.get_match(data, '<h2>Aggiornamenti Serie Tv</h2><(.*?)Vedi tutte</a></span>')	
	
    patron = '<img src="([^"]+)" alt="([^"]+)"><div class="rating">[^>]+>'
    patron += '</span>\s*([^<]+)</div><div class="featu">.*?</div>'
    patron += '<a href="([^"]+)">[^>]+></div>'

    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedthumbnail, scrapedtitle, rating, scrapedurl in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle).strip()
        if rating=="10" or rating=="0":
           rating = ""
        else:
           rating = " ([COLOR yellow]" + rating + "[/COLOR])"
        scrapedtitle = scrapedtitle.replace(" Streaming HD", "").replace(" streaming", "")
        scrapedtitle = scrapedtitle.replace("-)", ")").replace("’", "'")
        scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)

        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 title="[COLOR azure]" + scrapedtitle + '[/COLOR]' + rating,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 plot="",
                 folder=True), tipo='tv'))

    # Paginación
    next_page = scrapertools.find_single_match(data, '<a href="([^"]+)" ><span class="icon-chevron-right">')
    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_update",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=next_page,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png"))

    return itemlist

# ==================================================================================================================================================

def episodios(item):
    logger.info("[guarda_serie] episodios")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data
    patron = r'<iframe class="metaframe rptss" src="([^"]+)" frameborder="0" scrolling="no" allowfullscreen></iframe>'
    url = scrapertools.find_single_match(data, patron)

    data = httptools.downloadpage(url).data.replace('\n', '')

    section_stagione = scrapertools.find_single_match(data, '<i class="fa fa-home fa-fw"></i> Stagioni</a>(.*?)<select name="sea_select" class="dynamic_select">')
    patron = '<a href="([^"]+)" ><i class="fa fa-tachometer fa-fw"></i>\s*(\d+)</a></li>'
    seasons = re.compile(patron, re.DOTALL).findall(section_stagione)

    for scrapedseason_url, scrapedseason in seasons:

        season_url = urlparse.urljoin(url, scrapedseason_url)
        data = httptools.downloadpage(season_url).data.replace('\n', '')

        section_episodio = scrapertools.find_single_match(data, '<i class="fa fa-home fa-fw"></i> Episodio</a>(.*?)<select name="ep_select" class="dynamic_select">')
        patron = '<a href="([^"]+)" ><i class="fa fa-tachometer fa-fw"></i>\s*(\d+)</a></li>'
        episodes = re.compile(patron, re.DOTALL).findall(section_episodio)

        for scrapedepurl, scrapedepisode in episodes:
            episode_url = urlparse.urljoin(url, scrapedepurl)

            title = scrapedseason + "x" + scrapedepisode

            itemlist.append(
                Item(channel=__channel__,
                     action="findvideos_tv",
                     contentType="episode",
                     title="[COLOR azure]" + title + " -- " +  item.show + "[/COLOR]",
                     url=episode_url, 
                     fulltitle=title + " - " + item.show,
                     show=title + " - " + item.show,
                     plot="[COLOR orange]" + item.show + "[/COLOR]  " + item.plot,
                     thumbnail=item.thumbnail))

    return itemlist

# ==================================================================================================================================================

def findvideos_tv(item):
    logger.info("[guarda_serie] genere")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data
    bloque = scrapertools.get_match(data, '</ul>\s*<select\s*style(.*?)</nav>\s*</div>')

    # Extrae las entradas (carpetas)
    patron = '<a class=""\s*href="([^"]+)">\s*([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        if 'protectlink' in data:
          return findvideos_server(item)
        if scrapedtitle==" ":
          continue
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 fulltitle=item.fulltitle + " - " + scrapedtitle,
                 show=item.show + " - " + scrapedtitle,
                 title="[COLOR azure][[COLOR orange]" + scrapedtitle + "[/COLOR]] - " + item.title + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=item.thumbnail,
                 plot=item.plot,
                 folder=True))

    return itemlist

# ==================================================================================================================================================

def findvideos_server(item):
    logger.info("[guarda_serie] genere")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url).data

    # Extrae las entradas (carpetas)
    patron = '<a class="" href="[^"]+">\s*([^<]+)</a>.*?<iframe src=".*?//.*?=([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedtitle, scrapedurl in matches:
        scrapedurl = scrapedurl.decode('base64')
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 fulltitle=item.fulltitle,
                 show=item.show,
                 title="[COLOR azure][[COLOR orange]" + scrapedtitle.strip() + "[/COLOR]] - " + item.title + "[/COLOR]",
                 url=scrapedurl.strip(),
                 thumbnail=item.thumbnail,
                 plot=item.plot,
                 folder=True))

    return itemlist
	
# ==================================================================================================================================================	

def play(item):
    itemlist=[]

    data = item.url

    if "rapidcrypt" in item.url:
       data = httptools.downloadpage(item.url).data
	  
    if  'nodmca' in item.url:
        item.url = httptools.downloadpage(item.url, only_headers=True, follow_redirects=False).headers.get("location")
        data = item.url

    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        videoitem.title = item.title
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.plot = item.plot
        videoitem.channel = __channel__

    return itemlist
	
# ==================================================================================================================================================
# ==================================================================================================================================================

def findvideos(item):
    logger.info("[guarda_serie] findvideos")
    encontrados = set()
    itemlist = []

    # Descarga la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data
    patron = r'</ul>\s*<select  style(.*?)</nav>\s*</div>'
    bloque = scrapertools.find_single_match(data, patron)

    # Extrae las entradas (carpetas)
    patron = '<a class="" href="([^"]+)">\s*([^<]+)</a>'
    server_link = scrapertools.find_multiple_matches(bloque, patron)
    for scrapedurl, scrapedtitle in server_link:
        data = httptools.downloadpage(scrapedurl, headers=headers).data		
        if 'protectlink.stream' in data:
            scrapedcode = scrapertools.find_multiple_matches(data, r'<iframe src=".*?//.*?=([^"]+)"')

            for url in scrapedcode:
              url = url.decode('base64')
              encontrados.add(url)

    if encontrados:
        itemlist = servertools.find_video_items(data=str(encontrados))
        for videoitem in itemlist:
            videoitem.fulltitle = item.fulltitle
            videoitem.show = item.show
            videoitem.title = item.title + '[COLOR orange]' + videoitem.title + '[/COLOR]'
            videoitem.thumbnail = item.thumbnail
            videoitem.plot = item.plot
            videoitem.channel = __channel__

    return itemlist