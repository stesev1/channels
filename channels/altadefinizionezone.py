# -*- coding: utf-8 -*-
# StreamOnDemand Community Edition - Kodi Addon
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canale altadefinizionezone
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# ------------------------------------------------------------
import re
import urlparse

from core import config, httptools
from platformcode import logger
from core import scrapertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "altadefinizionezone"

host = "https://www.altadefinizione01.casa/"

headers = [['Referer', host]]


def mainlist(item):
    logger.info("streamondemand.altadefinizionezone mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Ultimi Film Inseriti[/COLOR]",
                     action="peliculas",
                     url=host,
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film Per Categoria[/COLOR]",
                     action="categorias",
                     url=host,
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca...[/COLOR]",
                     action="search",
                     extra="movie",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie-TV[/COLOR]",
                     action="peliculas_tv",
                     url="%s/serie-tv/" % host,
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca Serie-TV...[/COLOR]",
                     action="search",
                     extra="serie",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search")]
    return itemlist


def categorias(item):
    itemlist = []

    # Carica la pagina
    data = httptools.downloadpage(item.url, headers=headers).data
    bloque = scrapertools.find_single_match(data, '<ul class="listSubCat" id="Film">(.*?)</ul>')

    # Estrae i contenuti
    patron = '<li><a href="(.*?)">(.*?)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        scrapedplot = ""
        scrapedthumbnail = ""
        scrapedurl = host + scrapedurl

        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png",
                 folder=True))

    return itemlist


def search(item, texto):
    logger.info("[altadefinizionezone.py] " + item.url + " search " + texto)
    item.url = host + "/?do=search&subaction=search&story=" + texto
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

def newest(categoria):
    logger.info("streamondemand.altadefinizionezone newest" + categoria)
    itemlist = []
    item = Item()
    try:
        if categoria == "peliculas":
            item.url = host
            item.action = "peliculas"
            itemlist = peliculas(item)

            if itemlist[-1].action == "peliculas":
                itemlist.pop()

    # Continua la ricerca in caso di errore
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist

def peliculas(item):
    logger.info("streamondemand.altadefinizionezone peliculas")
    itemlist = []

    # Carica la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Estrae i contenuti
    patron = '<h2 class="titleFilm"><a href="([^"]+)">(.*?)</a></h2>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        scrapedplot = ""
        scrapedthumbnail = ""
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
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
                 folder=True), tipo='movie'))

    # Paginazione
    patronvideos = '<span>[^<]+</span> <a href="(.*?)">'
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
    logger.info("streamondemand.altadefinizionezone peliculas")
    itemlist = []

    # Carica la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Estrae i contenuti
    patron = '<h2 class="titleFilm"><a href="([^"]+)">(.*?)</a></h2>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        scrapedplot = ""
        scrapedthumbnail = ""
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="seasons",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='tv'))

    # Paginazione
    patronvideos = '<span>[^<]+</span> <a href="(.*?)">'
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


def seasons(item):
    logger.info("streamondemand.channels.altadefinizionezone seasons")

    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data

    patron = '<li><a href="([^"]+)" data-toggle="tab">(.*?)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedseason in matches:
        scrapedurl = item.url + scrapedurl
        scrapedplot = ""
        scrapedthumbnail = ""
        scrapedtitle = item.title

        itemlist.append(
            Item(channel=__channel__,
                 action="episodios",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]" + " " + "Stagione" + scrapedseason,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True))

    return itemlist


def episodios(item):
    logger.info("streamondemand.channels.altadefinizionezone episodios")

    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data
    patron = '<div class="tab-pane fade" id="%s">(.*?)</ul>' % item.url.split('#')[1]
    bloque = scrapertools.find_single_match(data, patron)

    patron = '<div class="row">\s*<div[^<]+<[^>>]+>(.+?)<\/div>\s*<[^>]+>\s*<[^>]+>\s*<a[^=]+=[^=]+=[^=]+=[^=]+="\/\/([^"]+)">'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedtitle, scrapedurl in matches:
        scrapedthumbnail = ""
        scrapedplot = ""
        scrapedurl = "https://" + scrapedurl
        scrapedtitle = scrapedtitle.replace("</small>", "")

        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True))

    return itemlist

def HomePage(item):
    import xbmc
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.Stefano/?action=sod)")
