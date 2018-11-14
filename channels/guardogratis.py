# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# StreamOnDemand-PureITA / XBMC Plugin
# Canale GuardoGratis
# http://www.mimediacenter.info/foro/viewtopic.php?f=36&t=7808
# ------------------------------------------------------------

import re
import urlparse

from core import config 
from core import httptools
from core import logger 
from core import servertools
from core import scrapertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "guardogratis"
host = "http://guardogratis.it/"

headers = [['User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:52.0) Gecko/20100101 Firefox/52.0'],
           ['Accept-Encoding', 'gzip, deflate'],
           ['Referer', host]]


def mainlist(item):
    logger.info("streamondemand-pureita guardogratis.py mainlist")
    itemlist = [Item(channel=__channel__,
                     title="Film[COLOR orange]   - Novita'[/COLOR]",
                     action="film",
                     url="%s/movies/" % host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/popcorn_new.png"),
                Item(channel=__channel__,
                     title="Film[COLOR orange]   - Top IMDB[/COLOR]",
                     action="film",
                     url="%s/top-imdb/" % host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/hd_movies_P.png"),
                Item(channel=__channel__,
                     title="Film[COLOR orange]   - Animazione[/COLOR]",
                     action="film",
                     url="%s/genre/animazione/" % host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/animated_movie_P.png"),
                Item(channel=__channel__,
                     title="Film[COLOR orange]   - Categorie[/COLOR]",
                     action="genere",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genres_P.png"),
	            Item(channel=__channel__,
                     title="Serie TV",
                     action="film",
                     url="%s/series/" % host,
                     extra="serie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/tv_series_P.png"),
                Item(channel=__channel__,
                     title="[COLOR orange]Cerca.....[/COLOR]",
                     action="search",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png")]

    return itemlist

# ==================================================================================================================================================

def search(item, texto):
    logger.info("streamondemand-pureita guardogratis.py search")
    item.url = host + "/?s=" + texto
    try:
        return film(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

# ==================================================================================================================================================

def genere(item):
    logger.info("streamondemand-pureita guardogratis.py pergenere")
    itemlist = []
    
    data = scrapertools.anti_cloudflare(item.url, headers=headers)
    blocco = scrapertools.get_match(data, 'Tutti i film</a>(.*?)Top film</a>')

    patron = '<a href="([^"]+)">([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(blocco)
	
    for scrapedurl, scrapedtitle in matches:
         if "Erotico" in scrapedtitle:
          continue
         itemlist.append(
             Item(channel=__channel__,
                 action="film",
                 title=scrapedtitle,
                 url=scrapedurl,
                 extra="movie",
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genre_P.png",
                 folder=True))

    return itemlist

# ==================================================================================================================================================

def film(item):
    logger.info("streamondemand-pureita guardogratis.py film")
    itemlist = []


    data = scrapertools.anti_cloudflare(item.url, headers=headers)
    patron = '<div data-movie-id=".*?" class="ml-item">\s*<a href="([^"]+)" data-url="" class="ml-mask jt" data-hasqtip=".*?" oldtitle=".*?" title="">.*?'
    patron += '<img data-original="([^"]+)" class="lazy thumb mli-thumb" alt="([^<]+)">.*?'
    patron += '<div class="jt-info.*?">\s*([^<]+)</.*?<p class="f-desc">(.*?)<\/p>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedimg, scrapedtitle, rating, scrapedplot in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle).strip()
        if rating:
          rating = " ([COLOR yellow]" + rating + "[/COLOR])"

        scrapedtitle=scrapedtitle.replace("[", "(").replace("]", ")")
        scrapedplot = scrapedplot.replace("<p>", "")
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios" if "series" in scrapedurl else "findvideos",
                 contentType="tv" if "series" in scrapedurl else "movie",
                 title=scrapedtitle + rating,
                 fulltitle=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedimg,
                 plot=scrapedplot,
                 show=scrapedtitle,
                 extra=item.extra,
                 folder=True), tipo="tv" if "series" in scrapedurl else "movie"))

    patron = "<li class='active'><a class=''>\d+</a></li><li><a rel='nofollow' class='page larger' href='([^']+)'>\d+</a>"
    matches = re.compile(patron, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = matches[0]
        itemlist.append(
            Item(channel=__channel__,
                action="film",
                title="[COLOR orange]Successivi >>[/COLOR]",
                url=scrapedurl,
                thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                folder=True))


    return itemlist

# ==================================================================================================================================================
"""
def film_top(item):
    logger.info("streamondemand-pureita guardogratis.py film")
    itemlist = []

    data = scrapertools.anti_cloudflare(item.url, headers=headers)
	
    patron = '<div data-movie-id=".*?" class="ml-item">\s*<a href="([^"]+)" data-url="" class="ml-mask jt" data-hasqtip=".*?" oldtitle=".*?" title="">\s*'
    patron += '<img data-original="([^"]+)" class="lazy thumb mli-thumb" alt="([^<]+)">'
    matches = re.compile(patron, re.DOTALL).findall(blocco)

    for scrapedurl, scrapedimg, scrapedtitle in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle).strip()
        if "series" in scrapedurl:
		    continue

        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 title=scrapedtitle,
                 fulltitle=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedimg,
                 extra=item.extra,
                 folder=True), tipo="movie"))

    patron = '<link rel="next" href="([^"]+)" />'
    matches = re.compile(patron, re.DOTALL).findall(data)


    if len(matches) > 0:
        scrapedurl = matches[0]
        itemlist.append(
            Item(channel=__channel__,
                action="film_top",
                title="[COLOR orange]Successivo >>[/COLOR]",
                url=scrapedurl,
                thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                folder=True))


    return itemlist
"""
# ==================================================================================================================================================
	
def film_new(item):
    logger.info("streamondemand-pureita guardogratis.py film")
    itemlist = []

    data = scrapertools.anti_cloudflare(item.url, headers=headers)
    blocco = scrapertools.get_match(data, 'Ultimi Film<i class="fa fa-chevron-right ml10">(.*?)Ultime Serie TV <i class="fa fa-chevron-right ml10">')
	
    patron = '<div data-movie-id=".*?" class="ml-item">\s*<a href="([^"]+)" data-url="" class="ml-mask jt" data-hasqtip=".*?" oldtitle=".*?" title="">.*?'
    patron += '<img data-original="([^"]+)" class="lazy thumb mli-thumb" alt="([^<]+)">.*?'
    patron += '<div class="jt-info.*?">\s*([^<]+)</.*?<p class="f-desc">(.*?)<\/p>'
    matches = re.compile(patron, re.DOTALL).findall(blocco)

    for scrapedurl, scrapedimg, scrapedtitle, rating, scrapedplot in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle).strip()
        if rating:
          rating = " ([COLOR yellow]" + rating + "[/COLOR])"
        scrapedtitle=scrapedtitle.replace("[", "(").replace("]", ")")
        scrapedplot = scrapedplot.replace("<p>", "")

        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 title=scrapedtitle + rating,
                 fulltitle=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedimg,
                 plot=scrapedplot,
                 extra=item.extra,
                 folder=True), tipo="movie"))

    patron = '<link rel="next" href="([^"]+)" />'
    matches = re.compile(patron, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = matches[0]
        itemlist.append(
            Item(channel=__channel__,
                action="film_new",
                title="[COLOR orange]Successivo >>[/COLOR]",
                url=scrapedurl,
                thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                folder=True))


    return itemlist

# ==================================================================================================================================================
	
def episodios(item):
    logger.info("streamondemand.channels.guardogratis episodios")

    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data
    blocco = scrapertools.get_match(data, '</i>\s*<span>Comments</span>(.*?)</div>\s*</div>\s*</div>\s*</div>')

    patron = '<a href="([^"]+)">\s*(.*?)<\/a>'
    matches = re.compile(patron, re.DOTALL).findall(blocco)

    for scrapedurl, scrapedtitle in matches:			
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 fulltitle=item.fulltitle + " - " + scrapedtitle,
                 show=item.show + " - " + scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=item.thumbnail,
                 plot="[COLOR orange]" + item.fulltitle + " - [/COLOR]" + item.plot,
                 folder=True))

    return itemlist
	
# ==================================================================================================================================================
	
def findvideos(item):
    itemlist = []
	
    data = httptools.downloadpage(item.url).data

    itemlist.extend(servertools.find_video_items(data=data))
    for videoitem in itemlist:
        servername = re.sub(r'[-\[\]\s]+', '', videoitem.title)
        videoitem.title = "".join(['[COLOR azure][[COLOR orange]' + servername.capitalize() + '[/COLOR]] - ', item.title])
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.plot = item.plot
        videoitem.channel = __channel__

    return itemlist

