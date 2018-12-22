# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Thegroove360 - XBMC Plugin
# Canale vedohd
# ------------------------------------------------------------

import re
import urllib

from core import httptools
from platformcode import logger
from core import scrapertools
from core import servertools
from core.item import Item

__channel__ = "vedohd"
__category__ = "F,S,A"
__type__ = "generic"
__title__ = "vedohd"
__language__ = "IT"

host = "http://vedohd.tv/"
headers = [['Referer', host]]


def mainlist(item):
    logger.info("[thegroove360.vedohd] mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Ultimi film inseriti[/COLOR]",
                     action="peliculas",
                     extra="movie",
                     url=host,
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film HD[/COLOR]",
                     action="peliculas",
                     extra="movie",
                     url="%sfilm-hd/" % host,
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Categorie film[/COLOR]",
                     action="categorias",
                     extra="movie",
                     url=host,
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Per Anno[/COLOR]",
                     action="anno",
                     extra="movie",
                     url=host,
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca...[/COLOR]",
                     action="search",
                     extra="movie",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search"),
                ]

    return itemlist


def search(item, texto):
    logger.info("[thegroove360.vedohd] " + item.url + " search " + texto)
    item.url = host + "/?s=" + texto

    try:
        if item.extra == "movie":
            return peliculas_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def newest():
    logger.info("[thegroove360.vedohd] newest")
    item = Item()
    try:
        item.url = host
        item.action = "peliculas"
        item.extra = "movie"
        itemlist = peliculas(item)

    # Continua la ricerca in caso di errore
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist


def categorias(item):
    logger.info("[thegroove360.vedohd] categorias")
    data = httptools.downloadpage(item.url).data
    patron = r'<ul class=\"genres.*></ul></nav>.*?<nav'
    blocco = scrapertools.get_match(data, patron)

    patron = r'<a href=\"([^\"]+)\".*?>(.*?)</a>'
    matches = re.compile(patron, re.IGNORECASE).findall(blocco)

    itemlist = []

    for scrapedurl, scrapedtitle in matches:
        scrapedthumbnail = ""
        scrapedplot = ""
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 contentType="movie",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 extra=item.extra,
                 folder=True)
        )

    return itemlist


def anno(item):
    logger.info("[thegroove360.vedohd] categorias")
    data = httptools.downloadpage(item.url).data
    patron = r'<ul class=\"releases.*></ul></nav>.*?'
    blocco = scrapertools.get_match(data, patron)

    patron = r'<a href=\"([^\"]+)\".*?>(.*?)</a>'
    matches = re.compile(patron, re.IGNORECASE).findall(blocco)

    itemlist = []

    for scrapedurl, scrapedtitle in matches:
        scrapedthumbnail = ""
        scrapedplot = ""
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 contentType="movie",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 extra=item.extra,
                 folder=True)
        )

    return itemlist


def peliculas(item):
    logger.info("[thegroove360.vedohd] peliculas")
    itemlist = []

    # Carica la pagina
    data = httptools.downloadpage(item.url).data

    # Estrae i contenuti
    patron = r'<article.*?<img src=\"([^\"]+)\".*?</span>\s(.*?)</div>.*?=\"mepo\">\s(.*?)</div><a href=\"([^\"]+)\".*?<h3><a.*?>(.*?)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedthumbnail, scrapedrate, scrapedquality, scrapedurl, scrapedtitle in matches:
        scrapedplot = ""

        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 contentType="movie",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR] - IMDb: " + scrapedrate,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 extra=item.extra,
                 folder=True))

    # Paginazione
    patronvideos = r'<a class=\'arrow_pag\' href=\"([^\"]+)\">'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = matches[0]
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
                 extra=item.extra,
                 folder=True))

    return itemlist


def peliculas_search(item):
    logger.info("[thegroove360.vedohd] peliculas_search")
    itemlist = []

    # Carica la pagina
    data = httptools.downloadpage(item.url).data

    # Estrae i contenuti
    patron = r'<article.*?<a href=\"([^\"]+)\"><img src=\"([^\"]+)\".*?><a.*?>(.*?)<'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        scrapedplot = ""

        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 contentType="movie",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR] ",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 extra=item.extra,
                 folder=True))

    # Paginazione
    patronvideos = r'<a class=\'arrow_pag\' href=\"([^\"]+)\">'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = matches[0]
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
                 extra=item.extra,
                 folder=True))

    return itemlist


def findvideos(item):
    data = httptools.downloadpage(item.url).data
    patron = r"<li id='player-.*?'.*?class='dooplay_player_option'\sdata-type='(.*?)'\sdata-post='(.*?)'\sdata-nume='(.*?)'>.*?'title'>(.*?)</"
    matches = re.compile(patron, re.IGNORECASE).findall(data)

    itemlist = []

    for scrapedtype, scrapedpost, scrapednume, scrapedtitle in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 fulltitle=item.title + " [" + scrapedtitle + "]",
                 show=scrapedtitle,
                 title="[COLOR azure]" + item.title + "[/COLOR] " + " [" + scrapedtitle + "]",
                 url="%swp-admin/admin-ajax.php" % host,
                 post=scrapedpost,
                 nume=scrapednume,
                 type=scrapedtype,
                 extra=item.extra,
                 folder=True))

    return itemlist


def play(item):
    payload = urllib.urlencode({'action': 'doo_player_ajax', 'post': item.post, 'nume': item.nume, 'type': item.type})
    data = httptools.downloadpage(item.url, post=payload).data

    patron = r"<iframe.*src='(([^']+))'\s"
    matches = re.compile(patron, re.IGNORECASE).findall(data)

    url = matches[0][0]
    data = httptools.downloadpage(url, headers=headers).data

    itemlist = servertools.find_video_items(data=data)

    return itemlist
