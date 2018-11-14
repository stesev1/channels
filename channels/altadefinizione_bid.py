# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand-PureITA - XBMC Plugin
# Canale  altadefinizione_bid
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

__channel__ = "altadefinizione_bid"
host = "https://altadefinizione.review"
headers     = [['Referer', host]]


def mainlist(item):
    logger.info("[streamondemand-pureita altadefinizione_bid] mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Film[COLOR orange] - Prima visione[/COLOR]",
                     action="peliculas",
                     url="%s/prime-visioni/" % host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/popcorn_cinema_P.png"),
               Item(channel=__channel__,
                     title="[COLOR azure]Film[COLOR orange] - Ultimi Inseriti[/COLOR]",
                     action="peliculas",
                     url="%s/genere/film/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/movies_P.png"),
               Item(channel=__channel__,
                     title="[COLOR azure]Film[COLOR orange] - HD[/COLOR]",
                     action="peliculas",
                     url=host + "/?s=[HD]",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/hd_movies_P.png"),
               Item(channel=__channel__,
                     title="[COLOR azure]Film[COLOR orange] - Categoria[/COLOR]",
                     action="categorias",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genres_P.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca Film...[/COLOR]",
                     action="search",
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png"),
               Item(channel=__channel__,
                     title="[COLOR azure]Serie TV - [COLOR orange]Nuove[/COLOR]",
                     action="peliculas_tv",
                     url=host+"/genere/serie-tv/",
                     extra="serie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/tv_series_P.png"),
               Item(channel=__channel__,
                     title="[COLOR azure]Serie TV - [COLOR orange]Aggiornate[/COLOR]",
                     action="peliculas_tv_new",
                     url=host+"/aggiornamenti-serie-tv/",
                     extra="serie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/new_tvshows_P.png"),
               Item(channel=__channel__,
                     title="[COLOR azure]Serie TV - [COLOR orange]Ultimi Episodi[/COLOR]",
                     action="peliculas_ep",
                     url=host+"/aggiornamenti-serie-tv/",
                     extra="serie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/new_tvshows_P.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca Serie TV...[/COLOR]",
                     action="search",
                     extra="serie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png")]

    return itemlist

# ==================================================================================================================================================

def categorias(item):
    logger.info("[streamondemand-pureita altadefinizione_bid] categorias")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data

    # Narrow search by selecting only the combo
    patron = '<li><a href="[^"]+">ULTIME SERIE TV</a></li>(.*?)</ul>'
    bloque = scrapertools.get_match(data, patron)

    # The categories are the options for the combo  
    patron = '<li><a href="([^"]+)">(.*?)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        scrapedurl = urlparse.urljoin(item.url, scrapedurl)
        if "Anime" in scrapedtitle:
         continue
        scrapedthumbnail = ""
        scrapedplot = ""
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genre_P.png",
                 extra=item.extra,
                 plot=scrapedplot))

    return itemlist

# ==================================================================================================================================================

def search(item, texto):
    logger.info("[streamondemand-pureita altadefinizione_bid] " + item.url + " search " + texto)
    item.url = host + "/?s=" + texto
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
    logger.info("[streamondemand-pureita altadefinizione_bid] peliculas")
    itemlist = []

    # Descarga la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = '<a href="([^"]+)" data-thumbnail="([^"]+)"><div>\s*' \
	         '<div class="title">([^>]+)</div>\s*[^>]+>([^<]+)</div>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle, rating in matches:
        if "test yb " in scrapedtitle or "test by" in scrapedtitle:
		   continue	
        if rating:
          rating = " ([COLOR yellow]" + rating + "[/COLOR])"
        if "HD" in rating:
          rating=""
        if "HD" in scrapedtitle:
           quality = " ([COLOR yellow]HD[/COLOR])"
        else:
            quality=""

        scrapedtitle = scrapedtitle.replace("[HD]", "")
		
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
    patronvideos = '</li>\s*<li><a href="([^>]+)" >Pagina successiva &raquo;</a></li>'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 extra=item.extra,
                 folder=True))

    return itemlist

# ==================================================================================================================================================

def peliculas_tv(item):
    logger.info("[streamondemand-pureita altadefinizione_bid] peliculas_tv")
    itemlist = []

    # Descarga la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = '<a href="([^"]+)" data-thumbnail="([^"]+)"><div>\s*<div class="title">([^<]+)</div>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        scrapedplot = ""
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 extra=item.extra,
                 folder=True), tipo='tv'))

    # Extrae el paginador 
    patronvideos = '</li>\s*<li><a href="([^>]+)" >Pagina successiva &raquo;</a></li>'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_tv",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 extra=item.extra,
                 folder=True))

    return itemlist

# ==================================================================================================================================================
	
def peliculas_tv_new(item):
    logger.info("[streamondemand-pureita altadefinizione_bid] peliculas_tv_new")
    itemlist = []
    PERPAGE = 14

    p = 1
    if '{}' in item.url:
        item.url, p = item.url.split('{}')
        p = int(p)
	
    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = '<a href="([^"]+)"\s*data-thumbnail="([^<]+)"><div>\s*<div class="title">([^>]+)</div>'
    matches = re.compile(patron).findall(data)

    for i, (scrapedurl, scrapedthumbnail, scrapedtitle) in enumerate(matches):
        if (p - 1) * PERPAGE > i: continue
        if i >= p * PERPAGE: break
        scrapedplot = ""
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 extra=item.extra,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 plot=scrapedplot,
                 folder=True), tipo='tv'))
				 
    if len(matches) >= p * PERPAGE:
        scrapedurl = item.url + '{}' + str(p + 1)
        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="peliculas_tv_new",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))

    return itemlist
	
# ==================================================================================================================================================

def peliculas_ep(item):
    logger.info("[streamondemand-pureita altadefinizione_bid] peliculas_ep")
    itemlist = []
    minpage = 14
	
    p = 1
    if '{}' in item.url:
       item.url, p = item.url.split('{}')
       p = int(p)
		
    # Descarga la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = '<li><a href="([^"]+)"\s*data-thumbnail="([^"]+)"><div>\s*'
    patron += '<div class="title">([^<]+)</div>\s*<div class[^>]+>([^<]+)</div>'
    matches = re.compile(patron, re.DOTALL).findall(data)


    for i, (scrapedurl, scrapedthumbnail, scrapedtitle, scrapedep) in enumerate(matches):
        if (p - 1) * minpage > i: continue
        if i >= p * minpage: break
        scrapedep = "  ([COLOR orange]" + scrapedep + "[/COLOR])"
        scrapedplot = ""

        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]" + scrapedep,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 extra=item.extra,
                 folder=True), tipo='tv'))
				 
    # Extrae el paginador
    if len(matches) >= p * minpage:
        scrapedurl = item.url + '{}' + str(p + 1)
        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="peliculas_ep",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))

    return itemlist

# ==================================================================================================================================================
	
def episodios(item):
    def load_episodios(html, item, itemlist, lang_title):
        patron = '((?:.*?<a\s*href="[^"]+"[^>]+>[^<]+<\/a>)+)'
        matches = re.compile(patron).findall(html)

        for data in matches:
            scrapedtitle = data.split('<a ')[0]
            scrapedtitle = re.sub(r'<[^>]*>', '', scrapedtitle).strip()
            if scrapedtitle != 'Categorie':
                scrapedtitle = scrapedtitle.replace('&#215;', 'x')
                scrapedtitle = scrapedtitle.replace(";", "")
                itemlist.append(
                    Item(channel=__channel__,
                         action="findvideos_tv",
                         contentType="episode",
                         title="[COLOR azure]%s[/COLOR]" % (scrapedtitle + " (" + lang_title + ")"),
                         url=data,
                         thumbnail=item.thumbnail,
                         extra=item.extra,
                         plot="[COLOR orange]" + item.fulltitle + "[/COLOR] " + item.plot,
                         fulltitle=item.fulltitle + " (" + lang_title + ")" + ' - ' + scrapedtitle,
                         show=item.show + " (" + lang_title + ")" + ' - ' + scrapedtitle))

    logger.info("[streamondemand-pureita altadefinizione_bid] episodios")
    itemlist = []

    # Descarga la pagina 
    data = httptools.downloadpage(item.url).data
    data = scrapertools.decodeHtmlentities(data)

    lang_titles = []
    starts = []
    patron = r"(?:tagione[^>]+.*?</strong>|)(?:Edizione|).*?"
    matches = re.compile(patron, re.IGNORECASE).finditer(data)
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


    return itemlist

# ==================================================================================================================================================
	
def findvideos_tv(item):
    logger.info("[streamondemand-pureita altadefinizione_bid] findvideos_tv")
    itemlist = []

    patron = '<a\s*href="([^"]+)"[^>]+>([^<]+)</a>'

    matches = re.compile(patron, re.DOTALL).findall(item.url)

    for scrapedurl, scrapedserver in matches:
        itemlist.append(
            Item(
                channel=__channel__,
                action="play",
                fulltitle=item.fulltitle,
                show=item.show,
                title="[[COLOR orange]" + scrapedserver + "[/COLOR]] - [COLOR azure]" + item.title + "[/COLOR]",
                url=scrapedurl,
                thumbnail=item.thumbnail,
                plot=item.plot,
                folder=True))

    return itemlist

# ==================================================================================================================================================

def findvideos_movies(item):
    logger.info("[streamondemand-pureita altadefinizione_bid] findvideos_movies")
    itemlist = []

    data = httptools.downloadpage(item.url).data
    # The categories are the options for the combo
    patron = '<iframe class="embed-responsive-item" SRC="(([^.]+)[^"]+)"[^>]+></iframe>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        scrapedurl = urlparse.urljoin(item.url, scrapedurl)
        scrapedthumbnail = ""
        scrapedplot = ""
        scrapedtitle = scrapedtitle.replace("https://", "")
        scrapedtitle = scrapedtitle.capitalize()
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 title="[COLOR azure][[COLOR orange]" + scrapedtitle + "[/COLOR]] - " + item.title + "[/COLOR]",
                 url=scrapedurl,
                 fulltitle=item.fulltitle,
                 show=item.show,
                 thumbnail=item.thumbnail,
                 plot=item.plot,
                 folder=True))
	
    patron = '<li><a href="([^"]+)" target="__blank" rel="nofollow">([^<]+)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        scrapedurl = urlparse.urljoin(item.url, scrapedurl)
        scrapedthumbnail = ""
        scrapedplot = ""
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 title="[[COLOR orange]" + scrapedtitle + "[/COLOR]] - [COLOR azure]" + item.title + "[/COLOR]",
                 url=scrapedurl,
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
"""
def findvideos(item):
    logger.info("streamondemand-pureita altadefinizione_bid findvideos")
	
    # Descarga la pagina 
    data = item.url if item.extra == 'serie' else httptools.downloadpage(item.url).data

    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        videoitem.title = "".join([item.title, '[COLOR orange][B]' + videoitem.title + '[/B][/COLOR]'])
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.show = item.show
        videoitem.plot = item.plot
        videoitem.channel = __channel__

    return itemlist
"""
# ==================================================================================================================================================
	
