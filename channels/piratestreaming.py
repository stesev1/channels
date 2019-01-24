# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# TheGroove360 / XBMC Plugin
# Canale 
# ------------------------------------------------------------
import re
import urlparse

from core import config, httptools
from platformcode import logger
from core import scrapertools
from core import servertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "piratestreaming"

host = "http://www.piratestreaming.watch"


def mainlist(item):
    logger.info()
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Film[/COLOR]",
                     action="peliculas",
                     extra="movie",
                     url="%s/category/films/" % host,
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca...[/COLOR]",
                     action="search",
                     extra="movie",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV[/COLOR]",
                     extra="serie",
                     action="peliculas_tv",
                     url="%s/category/serie/" % host,
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Anime[/COLOR]",
                     extra="serie",
                     action="peliculas_tv",
                     url="%s/category/anime-cartoni-animati/" % host,
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca SerieTV...[/COLOR]",
                     action="search",
                     extra="serie",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search")]

    return itemlist


def peliculas(item):
    logger.info()
    itemlist = []

    # Carica la pagina 
    data = httptools.downloadpage(item.url).data

    # Estrae i contenuti 
    patron = 'data-placement="bottom" title="(.*?)" alt=[^=]+="([^"]+)"> <img'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedtitle, scrapedurl in matches:
        scrapedthumbnail = ""
        scrapedplot = ""
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle).strip()
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 contentType="movie",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 extra=item.extra,
                 folder=True), tipo='movie'))

    # Paginazione 
    patronvideos = '<a\s*class="nextpostslink" rel="next" href="([^"]+)">Avanti'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="HomePage",
                 title="[COLOR yellow]Torna Home[/COLOR]",
                 folder=True)),
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png",
                 folder=True))

    return itemlist

def peliculas_tv(item):
    logger.info()
    itemlist = []

    # Carica la pagina 
    data = httptools.downloadpage(item.url).data

    # Estrae i contenuti 
    patron = 'data-placement="bottom" title="(.*?)" alt=[^=]+="([^"]+)"> <img'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedtitle, scrapedurl in matches:
        scrapedthumbnail = ""
        scrapedplot = ""
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle).strip()
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

    # Paginazione 
    patronvideos = '<a\s*class="nextpostslink" rel="next" href="([^"]+)">Avanti'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="HomePage",
                 title="[COLOR yellow]Torna Home[/COLOR]",
                 folder=True)),
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_tv",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png",
                 folder=True))

    return itemlist

def HomePage(item):
    import xbmc
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.Stefano)")

def search(item, texto):
    logger.info("[piratestreaming.py] " + item.url + " search " + texto)
    item.url = host + "/?s=" + texto
    try:
        if item.extra == "movie":
            return peliculas(item)
        if item.extra == "serie":
            return peliculas_tv(item)
    # Continua la ricerca in caso di errore 
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

def episodios(item):
    itemlist = []

    data = httptools.downloadpage(item.url).data

    patron = 'link-episode">(.*?)<\/span> <a\s*ref="nofollow" target=[^=]+="([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedtitle, scrapedurl in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle).strip()
        scrapedtitle = re.sub(r'\s+', ' ', scrapedtitle)
        scrapedtitle = scrapedtitle.replace(" -", "")
        scrapedtitle = scrapedtitle.replace("<strong>", "")
        scrapedtitle = scrapedtitle.replace("</strong>", " ")

        itemlist.append( 
            Item(channel=__channel__, 
                 action="findvid_serie",
                 contentType="episode", 
                 title=scrapedtitle, 
                 url=scrapedurl, 
                 thumbnail=item.thumbnail, 
                 extra=item.extra,
                 fulltitle=scrapedtitle, 
                 show=item.show))


    if config.get_library_support() and len(itemlist) != 0:
        itemlist.append(
            Item(channel=__channel__,
                 title="[COLOR yellow]""Aggiungi alla libreria""[/COLOR]",
                 url=item.url,
                 action="add_serie_to_library",
                 extra="episodios",
                 show=item.show))

    return itemlist


def findvid_serie(item):
    logger.info()

    itemlist = servertools.find_video_items(data=item.url)

    for videoitem in itemlist:
        videoitem.title = "".join([item.title, '[COLOR green][B]' + videoitem.title + '[/B][/COLOR]'])
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__

    return itemlist
