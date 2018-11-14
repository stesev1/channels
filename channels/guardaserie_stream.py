# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand-PureITA / XBMC Plugin
# Canale  guardaserie_stream
# http://www.mimediacenter.info/foro/viewtopic.php?f=36&t=7808
# ------------------------------------------------------------
import re
import urlparse

from core import httptools
from core import config
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "guardaserie_stream"
host        = "https://guardaserie.co/"
host_ep     = "https://player.guardaserie.co/media/"
headers     = [['Referer', host]]


thumbnail_animation="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/animation_P.png"
thumbnail_az="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/a-z_P.png"
thumbnail_classic="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/classictv_P.png"
thumbnail_search="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png"
thumbnail_doc="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/documentary_P.png"
thumbnail_fanart="https://superrepo.org/static/images/fanart/original/script.artwork.downloader.jpg"
thumbnail_genres="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genres_P.png"
thumbnail_lista="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/tv_serie_P.png"
thumbnail_list="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/all_movies_P.png"
thumbnail_novita="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/new_tvshows_P.png"
thumbnail_successivo="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png"
thumbnail_theatre="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/popcorn_new.png"
thumbnail_top="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"


def mainlist(item):
    logger.info("[streamondemand-pureita guardaserie_stream] mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Film - [COLOR orange]Novità[/COLOR]",
                     action="movie_list",
                     url="%s/ultimi-film-aggiunti/" % host,
                     extra="movie",
                     thumbnail=thumbnail_theatre,
                     fanart=thumbnail_lista),
                Item(channel=__channel__,
                     title="[COLOR azure]Film - [COLOR orange]Archivio[/COLOR]",
                     action="movie_list",
                     url="%s/lista-film/" % host,
                     extra="movie",
                     thumbnail=thumbnail_list,
                     fanart=thumbnail_lista),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie tv - [COLOR orange]Novità[/COLOR]",
                     action="lista_novita",
                     url=host,
                     thumbnail=thumbnail_theatre,
                     fanart=thumbnail_lista),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie tv - [COLOR orange]Animazione[/COLOR]",
                     action="lista_serie",
                     url="%s/lista-cartoni-animati-e-anime/" % host,
                     thumbnail=thumbnail_animation,
                     fanart=thumbnail_lista),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie tv - [COLOR orange]Alta Definizione[/COLOR]",
                     action="lista_serie",
                     url="%s/lista-serie-tv-in-altadefinizione/" % host,
                     thumbnail=thumbnail_lista,
                     fanart=thumbnail_lista),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie tv - [COLOR orange]Menu [/COLOR]",
                     action="menu_tvshow",
                     thumbnail=thumbnail_genres,
                     fanart=thumbnail_lista),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca...[/COLOR]",
                     action="search",
                     extra='serie',
                     thumbnail=thumbnail_search)]
    return itemlist
	
# ==================================================================================================================================================

def menu_tvshow(item):
    logger.info("[streamondemand-pureita guardaserie_stream] mainlist_tvshow")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Serie tv[COLOR orange] - Alta Definizione[/COLOR]",
                     action="lista_serie",
                     url="%s/lista-serie-tv-in-altadefinizione/" % host,
                     thumbnail=thumbnail_lista,
                     fanart=thumbnail_lista),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie tv[COLOR orange] -  Animazione[/COLOR]",
                     action="lista_serie",
                     url="%s/lista-cartoni-animati-e-anime/" % host,
                     thumbnail=thumbnail_animation,
                     fanart=thumbnail_lista),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie tv[COLOR orange] - Documentari[/COLOR]",
                     action="lista_serie",
                     url="%s/lista-documentari/" % host,
                     thumbnail=thumbnail_doc,
                     fanart=thumbnail_lista),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie tv[COLOR orange] - Classic Tv[/COLOR]",
                     action="lista_serie",
                     url="%s/lista-serie-tv-anni-60-70-80/" % host,
                     thumbnail=thumbnail_classic,
                     fanart=thumbnail_lista),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie tv[COLOR orange] - Italiane[/COLOR]",
                     action="lista_serie",
                     url="%s/lista-serie-tv-italiane/" % host,
                     thumbnail=thumbnail_lista,
                     fanart=thumbnail_lista),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie tv[COLOR orange] - Archivio[/COLOR]",
                     action="lista_serie",
                     url="%s/lista-serie-tv/" % host,
                     thumbnail=thumbnail_az,
                     fanart=thumbnail_lista),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca...[/COLOR]",
                     action="search",
                     extra='serie',
                     thumbnail=thumbnail_search)]
    return itemlist
	
# ==================================================================================================================================================

def search(item, texto):
    logger.info("[streamondemand-pureita guardaserie_stream]] " + item.url + " search " + texto)

    item.url = host + "/?s=" + texto

    try:
        return peliculas_src(item)

    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

# ==================================================================================================================================================

def peliculas_src(item):
    logger.info("[streamondemand-pureita guardaserie_stream] lista_novita")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data
	
    patron = '<div class="image">\s*<img src="([^"]+)" alt[^>]+>.*?'
    patron += '<a href="([^"]+)">\s*<span class="tt">([^<]+)<\/span>\s*'
    patron += '<span class="ttx">\s*(.*?)<div class="degradado">.*?'
    patron += '>\s*<\/div>\s*<\/div>\s*<div class=([^<]+)'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedthumbnail, scrapedurl, scrapedtitle, scrapedplot, type in matches:
        if not "http" in scrapedthumbnail:
          scrapedthumbnail=host+scrapedthumbnail
		
        scrapedtitle=scrapertools.decodeHtmlentities(scrapedtitle).strip()

        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos" if not "typepost" in type else "episodios",
                 contentType="movie" if not "typepost" in type else "tv",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 fulltitle=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 show=scrapedtitle,
                 folder=True), tipo='movie' if not "typepost" in type else "tv"))
								 
    return itemlist

# ==================================================================================================================================================

def movie_list(item):
    logger.info("[streamondemand-pureita guardaserie_stream] lista_serie")
    itemlist = []
    numpage = 14
	
    p = 1
    if '{}' in item.url:
        item.url, p = item.url.split('{}')
        p = int(p)
	
	
    data = httptools.downloadpage(item.url, headers=headers).data

    bloque = scrapertools.find_single_match(data, '<h1>[^<]+</h1>(.*?)</div>\s*<script')
    patron="<a href='([^']+)[^>]+>([^<]+)<\/a>"
    matches = re.compile(patron, re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for i, (scrapedurl,scrapedtitle) in enumerate(matches):
        if (p - 1) * numpage > i: continue
        if i >= p * numpage: break
        scrapedtitle=scrapedtitle.replace("(500)", "500").replace("&#8217;", "'").replace(":", " - ")
        scrapedtitle=scrapedtitle.replace("&#8211;", "-")
        title=scrapertools.decodeHtmlentities(scrapedtitle).strip()
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 contentType="movie",
                 title="[COLOR azure]" + title + "[/COLOR]",
                 fulltitle=title,
                 url=scrapedurl,
                 show="[COLOR azure]" + title + "[/COLOR]",
                 folder=True),tipo="movie"))
			
    # Extrae el paginador
    if len(matches) >= p * numpage:
        scrapedurl = item.url + '{}' + str(p + 1)
        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="movie_list",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))

    return itemlist
	
# ==================================================================================================================================================

def lista_serie(item):
    logger.info("[streamondemand-pureita guardaserie_stream] lista_serie")
    itemlist = []
    numpage = 14
	
    p = 1
    if '{}' in item.url:
        item.url, p = item.url.split('{}')
        p = int(p)
	
	
    data = httptools.downloadpage(item.url, headers=headers).data

    blocco = scrapertools.find_single_match(data, 'id="lcp_instance_0">(.*?)</ul>')
    patron='<a href="([^"]+)" title="([^<]+)">[^<]+</a>'
    matches = re.compile(patron, re.DOTALL).findall(blocco)
    scrapertools.printMatches(matches)

    for i, (scrapedurl,scrapedtitle) in enumerate(matches):
        if (p - 1) * numpage > i: continue
        if i >= p * numpage: break
        scrapedtitle=scrapedtitle.replace("&#8211; serie animata", "").replace(" e i ", " And The ")
        scrapedtitle=scrapedtitle.replace("&#8211;", "-").replace("nnn", "n")
        title=scrapertools.decodeHtmlentities(scrapedtitle.title()).strip()
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 contentType="tv",
                 title="[COLOR azure]" + title + "[/COLOR]",
                 fulltitle=title,
                 url=scrapedurl,
                 show=title,
                 folder=True),tipo='tv'))

    # Extrae el paginador
    if len(matches) >= p * numpage:
        scrapedurl = item.url + '{}' + str(p + 1)
        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="lista_serie",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))

    return itemlist
	
# ==================================================================================================================================================

def lista_novita(item):
    logger.info("[streamondemand-pureita guardaserie_stream] lista_novita")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data

    patron = '<img src="([^"]+)"[^>]+>\s*[^>]+>[^>]+>\s*(?:<span class.*?<\/b><\/b>\s*([^<]+)<\/span>\s*|)'
    patron += '<\/div>\s*<\/a>\s*<div class[^>]+>\s*<a href="([^"]+)">\s*[^>]+>([^<]+)<\/span>\s*'
    patron += '<span class[^>]+>\s*(.*?)<div[^>]+>.*?<h2>[^<]+</h2>\s*(?:<span class="year">([^<]+)</span>|)'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedthumbnail, rating, scrapedurl, scrapedtitle, scrapedplot, date in matches:
        if rating:
          rating=" ([COLOR yellow]" + rating.strip() + "[/COLOR])"
        if date:
          date=date.rstrip('–')
          date=date.replace("–", "-")
          year = " ("+ date.strip() + ")"
          years=" ([COLOR yellow]" + date + "[/COLOR])"
        else:
          year=""
          years=""
           
        scrapedtitle=scrapertools.decodeHtmlentities(scrapedtitle).strip()
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 contentType="tv",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]" + years + rating,
                 fulltitle=scrapedtitle + year,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 show=scrapedtitle,
                 folder=True),tipo='tv'))
								 
    patron = '<a href="([^"]+)"\s*>Next</a></div>'
    next_page = scrapertools.find_single_match(data, patron)
    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="lista_novita",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=next_page,
                 thumbnail=thumbnail_successivo))

    return itemlist

# ==================================================================================================================================================
	
def episodios(item):
    logger.info("[streamondemand-pureita.guardaserie_stream] episodios")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data
    patron = r"<iframe src='([^']+)' FRAMEBORDER[^>]+></iframe>"
    url = scrapertools.find_single_match(data, patron)

    data = httptools.downloadpage(url).data.replace('\n', '')


    section_stagione = scrapertools.find_single_match(data, 'Stagione([^+]+)<\/div>')
    patron = "<a href='([^']+)'><button type='button'[^>]+>(\d+)<\/button>"
    seasons = re.compile(patron, re.DOTALL).findall(section_stagione)

    for scrapedseason_url, scrapedseason in seasons:
        season_url= host_ep + scrapedseason_url
        data = httptools.downloadpage(season_url).data

        section_episodio = scrapertools.find_single_match(data, "Episodio(.*?)</div><div style='background-color.*?'>")
        patron = "<a href='([^']+)'>[^>]+>\s*(\d+)\s*<\/button>"
        episodes = re.compile(patron, re.DOTALL).findall(section_episodio)

        for scrapedepisode_url, scrapedepisode in episodes:
            episode_url = host_ep + scrapedepisode_url

            title = scrapedseason + "x" + scrapedepisode.zfill(2)

            itemlist.append(
                Item(channel=__channel__,
                     action="findvideos_all",
                     contentType="episode",
                     title="[COLOR azure]" + title + " - [/COLOR]" + item.title,
                     url=episode_url, 
                     fulltitle=item.fulltitle  + " - " + title,
                     show="[COLOR azure]" + item.show  + " - " + title + "[/COLOR]",
                     plot="[COLOR orange]" + item.fulltitle + "[/COLOR] " + item.plot,
                     thumbnail=item.thumbnail))


    return itemlist	
	

# ==================================================================================================================================================

def findvideos(item):
    logger.info("[streamondemand-pureita guardaserie_stream] findvideos_all")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data
	
    # Extrae las entradas (carpetas)
    patron = "<a href='([^']+)'[^>]+.*?img\s*src='[^']+'[^>]+>([^<]+)</a>"

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle  in matches:
        scrapedtitle=scrapedtitle.strip().capitalize()
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 title="[[COLOR orange]" + scrapedtitle + "[/COLOR]] - " + item.show,
                 fulltitle=item.fulltitle,
                 show=item.show,
                 url=scrapedurl,
                 thumbnail=item.thumbnail,
                 plot=item.plot,
                 folder=True))

    return itemlist

# ==================================================================================================================================================

def findvideos_all(item):
    logger.info("[streamondemand-pureita guardaserie_stream] findvideos_all")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data
	
    # Extrae las entradas (carpetas)
    patron = "<IFRAME SRC='([^\/]+\/\/([^\.]+)[^']+)' FRAMEBORDER=0 [^>]+><\/IFRAME>"

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle  in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 title="[[COLOR orange]" + scrapedtitle.capitalize() + "[/COLOR]] " + item.show,
                 fulltitle=item.fulltitle,
                 show=item.show,
                 url=scrapedurl,
                 thumbnail=item.thumbnail,
                 plot=item.plot,
                 folder=True))

    return itemlist

# ==================================================================================================================================================

def play(item):
    itemlist=[]

    data = item.url
    if 'vcrypt' in item.url:
        item.url = httptools.downloadpage(item.url, only_headers=True, follow_redirects=False).headers.get("location")
        data = item.url

    logger.debug(data)

    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        videoitem.title = item.title
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__

    return itemlist
	
# ==================================================================================================================================================