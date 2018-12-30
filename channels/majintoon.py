# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# TheGroove360 / XBMC Plugin
# Canal majintoon
# ------------------------------------------------------------

import re
import urlparse

from core import config
from core import logger
from core import servertools
from core import httptools
from core import scrapertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "majintoon"
host = "https://toonitalia.org/"
headers = [['Referer', host]]


def mainlist(item):
    logger.info("[thegroove360.majintoon] mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Video [COLOR orange]- Aggiornati[/COLOR]",
                     action="peliculas_new",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/popcorn_new.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Anime [COLOR orange]- Popolari[/COLOR]",
                     action="peliculas_popular",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/anime_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Anime [COLOR orange]- Lista[/COLOR]",
                     action="lista_animation",
                     url=host + "/lista-anime-2/",
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/anime_lista_P.png"),               
                Item(channel=__channel__,
                     title="[COLOR azure]Anime [COLOR orange]- Sub-ITA[/COLOR]",
                     action="lista_animation",
                     url=host + "/lista-anime-sub-ita/",
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/anime_sub_P.png"),
                #Item(channel=__channel__,
                     #title="[COLOR azure]Animazione [COLOR orange]- Bambini[/COLOR]",
                     #action="lista_animation",
                     #url=host + "/category/per-tutti/",
                     #extra="tv",
                     #thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/animation_P.png"),
	            #Item(channel=__channel__,
                     #action="categorie",
                     #title="[COLOR azure]Anime & Serie TV [COLOR orange]- Cetegorie[/COLOR]",
                     #url=host,
                     #thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/anime_genre_P.png"),              
                #Item(channel=__channel__,
                     #title="[COLOR azure]Anime [COLOR orange]- Film Animation[/COLOR]",
                     #action="lista_animation",
                     #extra="movie",
                     #url="%s/lista-film-animazione/" % host,
                     #thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/animated_movie_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV[/COLOR]",
                     action="lista_animation",
                     url=host + "/lista-serie-tv/",
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/tv_series_P.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca Film...[/COLOR]",
                     action="search",
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/search_P.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca Serie TV...[/COLOR]",
                     action="search",
                     extra="serie",
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/search_P.png")]

    return itemlist

# ===================================================================================================================================================

def search(item, texto):
    logger.info("[thegroove360.majintoon] " + item.url + " search " + texto)
    item.url = host + "/?s=" + texto
    try:
        return peliculas_src(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

# ===================================================================================================================================================

def categorie(item):
    logger.info("[thegroove360.majintoon] categorie")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data
	
    blocco = scrapertools.get_match(data, r'Categorie</a>\s*<ul\s*class="sub-menu">(.*?)</ul>\s*</li>')
    patron = r'<li[^>]+><a href="([^"]+)">([^<]+)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(blocco)

    for scrapedurl, scrapedtitle in matches:
        itemlist.append(
                Item(channel=__channel__,
                     action="lista_animation",
                     title=scrapedtitle,
                     url=scrapedurl,
                     extra="tv",
                     thumbnail=item.thumbnail,
                     folder=True))

    return itemlist
	
# ===================================================================================================================================================

def peliculas_popular(item):
    logger.info("[thegroove360.majintoon] categorie")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data
	
    blocco = scrapertools.get_match(data, r'I piu visti</h2>(.*?)</ul>')
    patron = r'<a href="([^"]+)" title="[^"]+" class="wpp-post-title" target="_self">([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(blocco)


    for scrapedurl, scrapedtitle in matches:
        scrapedthumbnail =""
        scrapedplot= ""
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="peliculas_server",
                 contentType="tv",
                 title=scrapedtitle,
                 fulltitle=scrapedtitle,
                 url=scrapedurl,
                 show=scrapedtitle,
                 extra="tv",
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo="tv"))

    return itemlist
	
# ===================================================================================================================================================

def peliculas_src(item):
    logger.info("[thegroove360.majintoon] lista_animation")
    itemlist = []
    minpage = 14
	
    p = 1
    if '{}' in item.url:
       item.url, p = item.url.split('{}')
       p = int(p)

    data = httptools.downloadpage(item.url, headers=headers).data

    patron = r'<h2 class="entry-title"><a href="([^"]+)" rel="bookmark">([^<]+)</a></h2>.*?'
    patron += r'<p>(.*?)</p>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for i, (scrapedurl, scrapedtitle, scrapedplot) in enumerate(matches):
        if (p - 1) * minpage > i: continue
        if i >= p * minpage: break
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedthumbnail = ""

        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="peliculas_server",
                 contentType="tv",
                 title=scrapedtitle,
                 fulltitle=scrapedtitle,
                 url=scrapedurl,
                 show=scrapedtitle,
                 extra="tv",
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo="tv"))
				 
    # Extrae el paginador
    if len(matches) >= p * minpage:
        scrapedurl = item.url + '{}' + str(p + 1)
        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="peliculas_src",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/next_1.png",
                 folder=True))

    return itemlist

# ===================================================================================================================================================

def peliculas_new(item):
    logger.info("[thegroove360.majintoon] lista_animation")
    itemlist = []
    minpage = 14
	
    p = 1
    if '{}' in item.url:
       item.url, p = item.url.split('{}')
       p = int(p)

    data = httptools.downloadpage(item.url, headers=headers).data

    patron = r'<h2 class="entry-title"><a href="([^"]+)" rel="bookmark">([^<]+)</a></h2>.*?'
    patron += r'<p class[^>]+><a href="[^"]+"><img width[^>]+src="([^"]+)" class[^>]+>.*?'
    patron += r'<p>(.*?)<\/p>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for i, (scrapedurl, scrapedtitle, scrapedthumbnail, scrapedplot) in enumerate(matches):
        if (p - 1) * minpage > i: continue
        if i >= p * minpage: break
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)

        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="peliculas_server",
                 contentType="tv",
                 title=scrapedtitle,
                 fulltitle=scrapedtitle,
                 url=scrapedurl,
                 show=scrapedtitle,
                 extra="tv",
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo="tv"))
				 
    # Extrae el paginador
    if len(matches) >= p * minpage:
        scrapedurl = item.url + '{}' + str(p + 1)
        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="peliculas_new",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/next_1.png",
                 folder=True))

    return itemlist

# ===================================================================================================================================================

def lista_animation(item):
    logger.info("[thegroove360.majintoon] lista_animation")
    itemlist = []
    minpage = 14
	
    p = 1
    if '{}' in item.url:
       item.url, p = item.url.split('{}')
       p = int(p)

    data = httptools.downloadpage(item.url, headers=headers).data

    patron = r'<li ><a href="([^"]+)" title="[^>]+">([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for i, (scrapedurl, scrapedtitle) in enumerate(matches):
        if (p - 1) * minpage > i: continue
        if i >= p * minpage: break
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedthumbnail = ""
        scrapedplot = ""
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="peliculas_server",
                 contentType="tv",
                 title=scrapedtitle,
                 fulltitle=scrapedtitle,
                 url=scrapedurl,
                 show=scrapedtitle,
                 extra="tv",
                 plot=scrapedplot,
                 thumbnail=scrapedthumbnail,
                 folder=True), tipo="tv"))
				 
    # Extrae el paginador
    if len(matches) >= p * minpage:
        scrapedurl = item.url + '{}' + str(p + 1)
        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="lista_animation",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/next_1.png",
                 folder=True))

    return itemlist
	
# ===================================================================================================================================================

def peliculas_server(item):
    logger.info("[thegroove360.majintoon] peliculas_server")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data
    patron = r'style=".*?">([^<]+)</span><br />(.*?)<span'
    list = scrapertools.find_multiple_matches(data, patron)
    if not len(list) > 0:
        patron = r'<span style="[^"]+">Link\s*([^<]+)</span><br />(.*?)<\/p>'
        list = scrapertools.find_multiple_matches(data, patron)
    for scrapedtitle, link in list:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedtitle = scrapedtitle.replace("0", "[COLOR yellow] - [/COLOR]")
        if "wiki" in scrapedtitle or "Scegli" in scrapedtitle \
		    or "ep." in scrapedtitle or "Special" in scrapedtitle:
          continue
        scrapedtitle = scrapedtitle.replace("Link", "Riproduci con")
        itemlist.append(
            Item(channel=__channel__,
                 action="episodes",
                 title="[COLOR orange]" + scrapedtitle + "[/COLOR]",
                 url=link,
                 extra=scrapedtitle,
                 plot=item.plot,
                 thumbnail=item.thumbnail,
                 folder=True))

    return itemlist

# ===================================================================================================================================================

def episodes(item):
    logger.info("[thegroove360.majintoon] episodes")
    itemlist = []
	
    data = httptools.downloadpage(item.url, headers=headers).data

    patron = r'<a href="([^"]+)"\s*target="_blank"\s*rel[^>]+>([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(item.url)

    for scrapedurl, scrapedtitle in matches:
        if 'Wikipedia' not in scrapedurl:
            scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle).replace("×", "x")
            scrapedtitle = scrapedtitle.replace("_", " ")
            scrapedtitle = scrapedtitle.replace(".mp4", "")
            itemlist.append(
                Item(channel=__channel__,
                     action="findvideos",
                     contentType="tv",
                     title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                     thumbnail=item.thumbnail,
                     fulltitle=scrapedtitle,
                     url=scrapedurl,
                     show=item.show,
                     plot=item.plot,
                     extra="tv",
                     folder=True))
	
    patron = r'<a href="([^"]+)"\s*target="_blank"[^>]+>[^>]+>[^>]+>[^>]+>\s*[^>]+>([^<]+)[^>]+>'
    matches = re.compile(patron, re.DOTALL).findall(item.url)

    for scrapedurl, scrapedtitle in matches:
        if 'Wikipedia' not in scrapedurl:
            scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle).replace("×", "x")
            scrapedtitle = scrapedtitle.replace("_", " ")
            scrapedtitle = scrapedtitle.replace(".mp4", "")
            itemlist.append(
                Item(channel=__channel__,
                     action="findvideos",
                     contentType="tv",
                     title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                     fulltitle=scrapedtitle,
                     url=scrapedurl,
                     extra="tv",
                     show=item.show,
                     plot=item.plot,
                     thumbnail=item.thumbnail,
                     folder=True))
	
    return itemlist

# ===================================================================================================================================================

def findvideos(item):
    logger.info("[thegroove360.majintoon] findvideos")
    itemlist = servertools.find_video_items(data=item.url)
    
    for videoitem in itemlist:
        videoitem.channel = __channel__
        server = re.sub(r'[-\[\]\s]+', '', videoitem.title)
        videoitem.title = "".join(['[COLOR orange] ' + "[[B]" + server + "[/B]] " + item.title + '[/COLOR]'])
        videoitem.thumbnail = item.thumbnail
        videoitem.plot = item.plot
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show

    return itemlist