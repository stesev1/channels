# -*- coding: iso-8859-1 -*-
# ------------------------------------------------------------
# StreamOnDemand-PureITA / XBMC Plugin
# Canale ItaliaFilm
# http://www.mimediacenter.info/foro/viewtopic.php?f=36&t=7808
# ------------------------------------------------------------

import os
import re
import time
import urllib
import urlparse

from core import config
from core import httptools
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "italiafilm"
host = "https://www.italia-film.pro"

headers = [['Referer', host]]

def isGeneric():
    return True

def mainlist(item):
    logger.info("[streamondemand-pureita italiafilm] mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Film & Serie TV[COLOR orange] - Novita'[/COLOR]",
                     action="peliculas",
                     extra="movie",
                     url="%s/novita-streaming-1/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/popcorn_cinema_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film[COLOR orange] - Categorie[/COLOR]",
                     action="categorias",
                     extra="movie",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genres_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film[COLOR orange] - HD[/COLOR]",
                     action="peliculas",
                     extra="movie",
                     url="%s/category/film-hd/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/hd_movies_P.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca Film...[/COLOR]",
                     action="search",
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV[COLOR orange] - Novita'[/COLOR]",
                     action="peliculas_tv",
                     extra="serie",
                     url="%s/category/serie-tv/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/tv_series_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV[COLOR orange] - Ultimi Aggiornamenti[/COLOR]",
                     action="pel_tv",
                     extra="serie",
                     url="%s/ultimi-telefilm-streaming/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/new_tvshows_P.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca Serie TV...[/COLOR]",
                     action="search",
                     extra="serie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png")]
    return itemlist

# ==================================================================================================================================================
	
def categorias(item):
    logger.info("[streamondemand-pureita italiafilm] categorias")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data
    data = scrapertools.find_single_match(data, '<a href=".">Categorie</a>(.*?)</div>')

    patron = '<li[^>]+><a href="([^"]+)">Film([^<]+)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for url, title in matches:
        scrapedurl = urlparse.urljoin(item.url, url)
        scrapedtitle = title
        scrapedplot = ""
        scrapedthumbnail = ""
        if scrapedtitle.startswith((" Porno")):
            continue
        itemlist.append(
            Item(channel=__channel__,
                 action='peliculas',
                 extra=item.extra,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genre_P.png",
                 plot=scrapedplot,
                 folder=True))

    return itemlist

# ==================================================================================================================================================
	
def search(item, texto):
    logger.info("[streamondemand-pureita italiafilm] search " + texto)
    item.url = host + "/?s=" + texto

    try:
        if item.extra == "movie":
            return peliculas(item)
        if item.extra == "serie":
            return peliculas_tv(item)
    # Se captura la excepcion, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

# ==================================================================================================================================================

def peliculas(item):
    logger.info("[streamondemand-pureita italiafilm] peliculas")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data
    patron = '<article(.*?)</article>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for match in matches:
        title = scrapertools.find_single_match(match, '<h3[^<]+<a href="[^"]+"[^<]+>([^<]+)</a>')
        title = title.replace("Streaming", "").replace("-)", ")")
        title = scrapertools.decodeHtmlentities(title).strip()
        url = scrapertools.find_single_match(match, '<h3[^<]+<a href="([^"]+)"')
        plot = ""
        thumbnail = scrapertools.find_single_match(match, 'data-echo="([^"]+)"')


        itemlist.append(infoSod(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="findvideos_movie" if not "serie" in url else "episodios",
                 fulltitle=title,
                 show=title,
                 title="[COLOR azure]" + title + "[/COLOR]",
                 url=url,
                 thumbnail=thumbnail,
                 plot=plot,
                 viewmode="movie_with_plot",
                 folder=True), tipo="movie" if not "serie" in url else "tv"))

    # Siguiente
    try:
        pagina_siguiente = scrapertools.get_match(data, '<a class="next page-numbers" href="([^"]+)"')
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 extra=item.extra,
                 title="[COLOR orange]Successivi >> [/COLOR]",
                 url=pagina_siguiente,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))
    except:
        pass

    return itemlist

# ==================================================================================================================================================

def findvideos_movie(item):
    logger.info("[streamondemand-pureita italiafilm] findvideos_movie")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data
    bloque = scrapertools.get_match(data, '</p>\s*<p>(.*?)</strong></p>')

    # Extrae las entradas (carpetas)
    patron = '<a href="([^"]+)" [^>]+>([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 title=item.title + "  [[COLOR orange]" + scrapedtitle + "[/COLOR]]",
                 url=scrapedurl,
                 thumbnail=item.thumbnail,
                 plot=item.plot,
                 folder=True))

    patron = '<iframe style="border: 0;" src="([^.]+\.([^.]+)[^"]+)" width="100%" height="100%" allowfullscreen="allowfullscreen"><\/iframe><\/div>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 title=item.title + "  [[COLOR orange]" + scrapedtitle + "[/COLOR]]",
                 url=scrapedurl,
                 thumbnail=item.thumbnail,
                 plot=item.plot,
                 folder=True))
				 
    return itemlist
# ==================================================================================================================================================
	
def findvid_old(item):
    logger.info("[streamondemand-pureita italiafilm] findvid_old")

    itemlist = []

    # Carica la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data

    # Estrae i contenuti 
    patron = '<iframe style="border: 0;" src="([^"]+)" width="[^"]*" height="[^"]*" scrolling="[^"]*" allowfullscreen="[^"]*">'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl in matches:
        data += httptools.downloadpage(scrapedurl, headers=headers).data

    ### robalo fix obfuscator - start ####

    patron = 'href="(https?://www\.keeplinks\.eu/p16/([^"]+))"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for keeplinks, id in matches:
        headers.append(['Cookie', 'flag[' + id + ']=1; defaults=1; nopopatall=' + str(int(time.time()))])
        headers.append(['Referer', keeplinks])

        html = httptools.downloadpage(keeplinks, headers=headers).data
        data += str(scrapertools.find_multiple_matches(html, '<a href="([^"]+)" target="_blank"'))

    ### robalo fix obfuscator - end ####

    for videoitem in servertools.find_video_items(data=data):
        videoitem.title = item.title + videoitem.title
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.show = item.show
        videoitem.plot = item.plot
        videoitem.channel = __channel__
        itemlist.append(videoitem)
		
    patron = '<a href="([^"]+)" rel="noopener" [^>]+>([^<]+)<'
    matches = re.compile(patron, re.DOTALL).findall(item.url)

    for scrapedurl, scrapedserver in matches:
        itemlist.append(
            Item(
                channel=__channel__,
                action="findvideos",
                fulltitle=item.fulltitle,
                show=item.title,
                title="[COLOR azure]" + item.title + "  [[COLOR orange]" + scrapedserver + "[/COLOR]]",
                url=scrapedurl,
                thumbnail=item.thumbnail,
                plot=item.plot,
                folder=True))
	
    return itemlist

# ==================================================================================================================================================	

def peliculas_tv(item):
    logger.info("[streamondemand-pureita italiafilm] peliculas_tv")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data
    patron = '<article(.*?)</article>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for match in matches:
        title = scrapertools.find_single_match(match, '<h3[^<]+<a href="[^"]+"[^<]+>([^<]+)</a>')
        title = title.replace("Streaming", "").replace("-)", ")")
        title = scrapertools.decodeHtmlentities(title).strip()
        show_title = re.sub('\(.*?\)', '', title.replace('Serie TV', ''))
        url = scrapertools.find_single_match(match, '<h3[^<]+<a href="([^"]+)"')
        plot = ""
        thumbnail = scrapertools.find_single_match(match, 'data-echo="([^"]+)"')


        itemlist.append(infoSod(
            Item(channel=__channel__,
                 extra=item.extra,
                 action='episodios' if 'serie' in url else 'findvideos_movie',
                 fulltitle=title,
                 show=show_title,
                 title="[COLOR azure]" + title + "[/COLOR]",
                 url=url,
                 thumbnail=thumbnail,
                 plot=plot,
                 viewmode="movie_with_plot",
                 folder=True), tipo='tv'))

    # Siguiente
    try:
        pagina_siguiente = scrapertools.get_match(data, '<a class="next page-numbers" href="([^"]+)"')
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_tv",
                 extra=item.extra,
                 title="[COLOR orange]Successivi >> [/COLOR]",
                 url=pagina_siguiente,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))
    except:
        pass

    return itemlist

# ==================================================================================================================================================
	
def pel_tv_old(item):
    logger.info("[streamondemand-pureita italiafilm] pel_tv_old")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data
    patron = '<span class="tvseries_name">(.*?)</span>\s*<a href="([^"]+)"[^>]+><i class="icon-link"></i>(.*?)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scraptitle1, scrapedurl, scraptitle2 in matches:
        title = scraptitle1 + scraptitle2
        plot = ""
        thumbnail = ""
        url = scrapedurl

        itemlist.append(infoSod(
            Item(channel=__channel__,
                 extra=item.extra,
                 action='episodios' if item.extra == 'serie' else 'findvideos',
                 fulltitle=title,
                 show=title,
                 title="[COLOR azure]" + title + "[/COLOR]",
                 url=url,
                 thumbnail=thumbnail,
                 plot=plot,
                 viewmode="movie_with_plot",
                 folder=True), tipo='tv'))

    # Siguiente
    try:
        pagina_siguiente = scrapertools.get_match(data, '<a class="next page-numbers" href="([^"]+)"')
        itemlist.append(
            Item(channel=__channel__,
                 action="pel_tv",
                 extra=item.extra,
                 title="[COLOR orange]Successivi >> [/COLOR]",
                 url=pagina_siguiente,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))
    except:
        pass

    return itemlist
	
# ==================================================================================================================================================
	
def pel_tv(item):
    logger.info("[streamondemand-pureita italiafilm] pel_tv")

    itemlist = []
    PERPAGE = 8

    p = 1
    if '{}' in item.url:
        item.url, p = item.url.split('{}')
        p = int(p)

    # Descarga la pagina

    data = httptools.downloadpage(item.url, headers=headers).data

    # Estrae i contenuti 
    patron = '<span class="tvseries_name">([^<]+)<\/span>\s*'
    patron += '<a href="([^"]+)" class="tvseries_episode" title="[^>]+"><i class="icon-link"><\/i>([^<]+)<\/a>\s*'
    patron += '<span class="clear"><\/span>\s*<\/li>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    scrapedthumbnail = ""
    scrapedplot = ""
    for i, (scrapedtitle, scrapedurl, scraped_ep) in enumerate(matches):
        if (p - 1) * PERPAGE > i: continue
        if i >= p * PERPAGE: break
        title = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="episodios",
                 contentType="tv",
                 title=title + scraped_ep,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=title,
                 show=title,
                 plot=scrapedplot,
                 folder=True), tipo='tv'))
				 
    # Extrae el paginador
    if len(matches) >= p * PERPAGE:
        scrapedurl = item.url + '{}' + str(p + 1)
        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="pel_tv",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))

    return itemlist
# ==================================================================================================================================================
	
def episodios(item):
    def load_episodios(html, item, itemlist, lang_title):
        for data in scrapertools.decodeHtmlentities(html).splitlines():
            # Extrae las entradas
            end = data.find('<a ')
            if end > 0:
                scrapedtitle = re.sub(r'<[^>]*>', '', data[:end]).strip()
            else:
                scrapedtitle = ''
            if scrapedtitle == '':
                patron = '<a\s*href="[^"]+"\s*target="_blank">([^<]+)</a>'
                scrapedtitle = scrapertools.find_single_match(data, patron).strip()
            title = scrapertools.find_single_match(scrapedtitle, '\d+[^\d]+\d+')
            if title == '':
                title = scrapedtitle
            if title != '':
                title = re.sub(r"(\d+)[^\d]+(\d+)", r"\1x\2", title)
                title += " (" + lang_title + ")"
                itemlist.append(
                    Item(channel=__channel__,
                         action="findvideos_tv",
                         title=title.replace("-)", ")"),
                         url=data,
                         thumbnail=item.thumbnail,
                         extra=item.extra,
                         fulltitle=title + ' - ' + item.show,
                         plot="[COLOR yellow][B]" + item.fulltitle + "[/B][/COLOR] " + item.plot, 
                         show=item.show))

    logger.info("[streamondemand-pureita italiafilm] episodios")

    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    start = data.find('id="pd_rating_holder')
    end = data.find('id="linkcorrotto-show"', start)

    data = data[start:end]

    lang_titles = []
    starts = []
    patron = r"STAGION[I|E](.*?ITA)?"
    matches = re.compile(patron, re.IGNORECASE).finditer(data)
    for match in matches:
        season_title = match.group()
        # if season_title != '':
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

    if len(itemlist) == 0:
        load_episodios(data, item, itemlist, 'ITA')


    return itemlist

# ==================================================================================================================================================
def findvideos_tv(item):
    logger.info("[streamondemand-pureita italiafilm] findvideos_tv")
    itemlist = []
	
    data = httptools.downloadpage(item.url, headers=headers).data	
    patron = 'href="([^"]+)"[^>]+>([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(item.url)

    for scrapedurl, scrapedserver in matches:
        itemlist.append(
            Item(
                channel=__channel__,
                action="play",
                fulltitle=item.fulltitle,
                show=item.title,
                title="[COLOR azure]" + item.title + "  [[COLOR orange]" + scrapedserver + "[/COLOR]]",
                url=scrapedurl,
                thumbnail=item.thumbnail,
                plot=item.plot,
                folder=True))

    return itemlist	
	
# ==================================================================================================================================================	
	
def findvideos(item):
    logger.info("[streamondemand-pureita italiafilm] findvideos")

    # Descarga la página
    data = item.url 

    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        videoitem.title = item.fulltitle + videoitem.title
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.show = item.show
        videoitem.plot = item.plot
        videoitem.channel = __channel__

    return itemlist

# ==================================================================================================================================================
	
def play(item):
    itemlist=[]

    data = item.url

    if "italia-film" in item.url:
       data = httptools.downloadpage(item.url).data
	  
    while 'vcrypt' in item.url:
        item.url = httptools.downloadpage(item.url, only_headers=True, follow_redirects=False).headers.get("location")
        data = item.url
		
    #logger.debug(data)

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
	
def findvideos_old(item):
    logger.info("[streamondemand-pureita italiafilm] findvideos_old")
    itemlist = []

    # Descarga la pagina

    data = httptools.downloadpage(item.url, headers=headers).data
    
    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        server = re.sub(r'[-\[\]\s]+', '', videoitem.title)
        videoitem.title = "".join([item.title, ' [COLOR orange][B]' + server + '[/B][/COLOR]'])
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.plot = item.plot
        videoitem.channel = __channel__
    # Extrae las entradas (carpetas)

    patron = '<a href="([^"]+)"[^>]+>([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:

        scrapedplot = ""
        scrapedthumbnail = ""
        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 fulltitle=item.fulltitle,
                 action="play",
                 title=item.title + " [COLOR orange][B]" + scrapedtitle + "[/B][/COLOR]",
                 url=scrapedurl,
                 thumbnail=item.thumbnail,
                 plot=item.plot,
                 folder=True))


    return itemlist	
