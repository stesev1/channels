# -*- coding: utf-8 -*-
# StreamOnDemand Community Edition - Kodi Addon
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canale cinemasubito
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# ------------------------------------------------------------
import binascii
import re
import urlparse

from core import httptools, scrapertools, servertools
from core.item import Item
from core.tmdb import infoSod
from lib import jscrypto
from platformcode import logger

__channel__ = "cinemasubito"

host = "https://www.cinemasubito.org/"

headers = [
    ['User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0'],
    ['Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'],
    ['Accept-Encoding', 'gzip, deflate'],
    ['Accept-Language', 'en-US,en;q=0.5'],
    ['Host', 'www.cinemasubito.org'],
    ['DNT', '1'],
    ['Upgrade-Insecure-Requests', '1'],
    ['Connection', 'keep-alive'],
    ['Referer', host],
    ['Cache-Control', 'max-age=0']
]

def mainlist(item):
    logger.info("streamondemand.cinemasubito mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Film[/COLOR]",
                     action="peliculas",
                     url="%s/film/pagina/1" % host,
                     extra="movie",
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
                     title="[COLOR azure]Serie TV[/COLOR]",
                     action="peliculas_tv",
                     url="%s/serie" % host,
                     extra="serie",
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca Serie TV...[/COLOR]",
                     action="search",
                     extra="serie",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search")]

    return itemlist

def search(item, texto):
    logger.info("streamondemand.cinemasubito " + item.url + " search " + texto)
    item.url = host + "/cerca/" + texto
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

def categorias(item):
    itemlist = []

    # Carica la pagina
    data = httptools.downloadpage(item.url, headers=headers).data
    bloque = scrapertools.get_match(data, '<h4>Genere</h4>(.*?)<li class="genre">')

    # Estrae i contenuti
    patron = '<a href="([^"]+)" title="([^"]+)">'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        scrapedtitle = scrapedtitle.replace("Film genere ", "")
        itemlist.append(
            Item(
                channel=__channel__,
                action="peliculas",
                title=scrapedtitle,
                url=scrapedurl,
                thumbnail=
                "https://farm8.staticflickr.com/7562/15516589868_13689936d0_o.png",
                folder=True))

    return itemlist

def peliculas(item):
    logger.info("streamondemand.cinemasubito peliculas")
    itemlist = []

    # Carica la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Estrae i contenuti
    patron = '<a href="([^"]+)" title="([^"]+)">\s*<div class="wrt">'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        scrapedplot = ""
        scrapedthumbnail = ""
        if host not in scrapedurl:
            scrapedurl = host + scrapedurl
        else:
            scrapedurl = scrapedurl

        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='movie'))

    # Paginazione
    patronvideos = '<a href="[^"]+"[^d]+data-ci-pagination-page[^>]+>[^<]+<\/a><\/span>[^=]+="([^"]+)"'
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
    logger.info("streamondemand.cinemasubito peliculas")
    itemlist = []

    # Carica la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Estrae i contenuti
    patron = '<a href="([^"]+)" title="([^"]+)">\s*<div class="wrt">'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        scrapedplot = ""
        scrapedthumbnail = ""
        if host not in scrapedurl:
            scrapedurl = host + scrapedurl
        else:
            scrapedurl = scrapedurl

        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='tv'))

    # Paginazione
    patronvideos = '<a href="[^"]+"[^d]+data-ci-pagination-page[^>]+>[^<]+<\/a><\/span>[^=]+="([^"]+)"'
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

def episodios(item):
    logger.info("streamondemand.channels.cinemasubito episodios")

    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data

    patron = 'href="([^"]+)"><span class="glyphicon glyphicon-triangle-right"></span>(.*?)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        scrapedplot = ""
        scrapedthumbnail = ""
        if host not in scrapedurl:
            scrapedurl = host + scrapedurl
        else:
            scrapedurl = scrapedurl

        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='tv'))

    return itemlist


def findvideos(item):
    logger.info("streamondemand.cinemasubito findvideos_tv")

    links = set()
    data = httptools.downloadpage(item.url, headers=headers).data
    p = scrapertools.find_single_match(data, r'var decrypted = CryptoJS\.AES\.decrypt\(vlinkCrypted, "([^"]+)",')
    urls = scrapertools.find_multiple_matches(data, r"<li><a rel=[^t]+target=[^c]+class=[^=]+=[^:]+:'(.*?)'[^:]+:'(.*?)'[^:]+:'(.*?)'")
    for url, iv, salt in urls:
        salt = binascii.unhexlify(salt)
        iv = binascii.unhexlify(iv)
        url = jscrypto.decode(url, p, iv=iv, salt=salt)
        url = url.replace('\/', '/')
        links.add(url)

    itemlist = servertools.find_video_items(data=str(links) + data)
    for videoitem in itemlist:
        videoitem.title = item.title + videoitem.title
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.show = item.show
        videoitem.plot = item.plot
        videoitem.channel = __channel__

    return itemlist


def HomePage(item):
    import xbmc
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.streamondemand)")
