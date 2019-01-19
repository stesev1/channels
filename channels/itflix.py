# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# TheGroove360 / XBMC Plugin
# Canale 
# ------------------------------------------------------------

from core import httptools, scrapertools, servertools, listtools
from core.item import Item
from platformcode import logger
from core.tmdb import infoSod
import re

__channel__ = "itflix"
listtools.__channel__ = __channel__

host = "https://itflix.stream"

headers = [['Referer', host]]


def mainlist(item):
    logger.info("[itflix.py] mainlist")

    # Main options
    itemlist = [Item(channel=__channel__,
                     action="peliculas",
                     title="[COLOR azure]Film[/COLOR]",
                     url="%s/film" % host,
                     # extra="film",
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     action="peliculas",
                     title="[COLOR azure]Piu Votati[/COLOR]",
                     url="%s/i-piu-votati/" % host,
                     extracheck="piuvotati",
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     action="peliculas",
                     title="[COLOR azure]Piu Popolari[/COLOR]",
                     url="%s/piu-popolari/" % host,
                     extracheck="piupopolari",
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     action="peliculas",
                     title="[COLOR azure]Al Cinema[/COLOR]",
                     url="%s" % host,
                     extracheck="alcinema",
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     action="by_anno_or_by_genere",
                     title="[COLOR azure]Genere[/COLOR]",
                     url=host,
                     extracheck="by_genere",
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     action="by_anno_or_by_genere",
                     title="[COLOR azure]Elenco Per Anno[/COLOR]",
                     url="%s/i-piu-votati/" % host,
                     extracheck="by_anno",
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     action="search",
                     title="[COLOR yellow]Cerca Film[/COLOR]",
                     extra="movie",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search")]

    return itemlist


def peliculas(item):
    logger.info("[itflix.py] peliculas")
    patron = ''

    if item.url == "":
        item.url = host
    # Carica la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data
    datat = data

    ## Setting generic parameters for moth of movies
    patronqual = '.*?quality[^>]*>([^<]+)<'
    itemp = {'title': '\\2 (\\6) [[COLOR orange]\\4[/COLOR] - Rate: [COLOR yellow]\\3[/COLOR]]',
             'url': '\\5',
             'thumbnail': '\\1',
             'extracheck': item.extracheck}

    ## special condition for few movies
    if item.extracheck == "film":
        datat = scrapertools.find_single_match(data, '<header><h2>Film.*?<\/header>.*?<\/article><\/div>')
    elif item.extracheck == "alcinema":
        datat = scrapertools.find_single_match(data, '<header><h2>Al.*?<\/header>.*?<\/article><\/div>')
        itemp['title'] = '\\2 (\\6) [Rate: [COLOR yellow]\\3[/COLOR]]'
        patronqual = '(.)'
    elif item.extracheck == "search":
        itemp['title'] = '\\3 (\\4)'
        itemp['url'] = '\\2'
        patron = 'class="thumbnail\s*animation-2".*?src="([^"]+)".*?href="([^"]+)".*?>([^<]+)<.*?year">([^<]+)'

    if not patron: patron = '<article\s*id.*?src="([^"]+)"\s*alt="([^"]+)".*?rating.*?\/span>\s*([^<]+)<' + patronqual + '.*?href="([^"]+)".*?span>([^<]+)<.*?<\/article>'

    itemlist = listtools.list_titles_info(regx=patron, data=datat, itemp=itemp, tipos='movie')

    i = listtools.next_page(data, '<span class="current">[^<]+</span><a href=\'(.*?)\'[^>]+>', 'peliculas')
    if i: itemlist.append(i)

    return itemlist


def by_anno_or_by_genere(item):
    logger.info("[itflix.py] genere")

    if item.url == "": item.url = host

    # Carica la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data

    if item.extracheck == "by_anno":
        patronvideos = '<li><a href="([^"]+)">([^"]+)<\/a><\/li>'
    elif item.extracheck == "by_genere":
        patronvideos = '<li id="menu-item.*?genres.*?<a href="([^"]+)">([^"]+)<\/a><\/li>'

    itemlist = listtools.list_titles(regx=patronvideos, data=data,
                                     itemp={'title': '\\2', 'url': '\\1', 'action': 'peliculas', 'content': 'list'})

    return itemlist


def search(item, texto):
    logger.info("[itflix.py] " + item.url + " search " + texto)
    item.url = host + "/?s=" + texto

    try:
        return peliculas_src(item)

    # Continua la ricerca in caso di errore 
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

def peliculas_src(item):
    logger.info("Stefano.itflix peliculas")
    itemlist = []

    # Carica la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data

    # Estrae i contenuti 
    patron = r'<div class="title"> <a href="([^"]+)">(.*?)<'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        scrapedplot = ""
        scrapedthumbnail = ""

        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 contentType="movie",
                 extra="movie",
                 title=scrapedtitle,
                 fulltitle=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail), tipo="movie"))

    return itemlist

def findvideos(item):
    logger.info("[itflix.py] findvideos")

    # Carica la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data

    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        videoitem.title = "".join([item.title, '[COLOR green][B]' + videoitem.title + '[/B][/COLOR]'])
        videoitem.channel = __channel__

    return itemlist
