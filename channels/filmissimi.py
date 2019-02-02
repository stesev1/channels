# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# TheGroove360 - Kodi Addon
# ------------------------------------------------------------
# Canale per altadefinizione.wiki
# ------------------------------------------------------------

import re

import xbmc

from core import httptools
from platformcode import logger, servertools
from core import scrapertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "filmissimi"
host = "https://altadefinizione.wiki/"
headers = [['Referer', host]]


# -------------------------------------------------------------------------------------------------------------------------------------------
def mainlist(item):
    logger.info("[thegroove360.filmissimi] mainlist")
    itemlist = [Item(channel=__channel__,
                     action="elenco",
                     title="[COLOR yellow]Novita'[/COLOR]",
                     url=host,
                     thumbnail=NovitaThumbnail,
                     fanart=FilmFanart),
                Item(channel=__channel__,
                     action="elenco",
                     title="[COLOR azure]Film Sub-Ita[/COLOR]",
                     url=host + "/genere/sub-ita",
                     thumbnail=NovitaThumbnail,
                     fanart=FilmFanart),
                Item(channel=__channel__,
                     action="elenco",
                     title="[COLOR azure]Film HD[/COLOR]",
                     url=host + "/genere/film-in-hd",
                     thumbnail=NovitaThumbnail,
                     fanart=FilmFanart),
                Item(channel=__channel__,
                     action="genere",
                     title="[COLOR azure]Genere[/COLOR]",
                     url=host,
                     thumbnail=GenereThumbnail,
                     fanart=FilmFanart),
                Item(channel=__channel__,
                     action="search",
                     extra="movie",
                     title="[COLOR orange]Cerca..[/COLOR]",
                     thumbnail=CercaThumbnail,
                     fanart=FilmFanart)]

    return itemlist


# ===========================================================================================================================================

# -------------------------------------------------------------------------------------------------------------------------------------------
def newest(categoria):
    logger.info("[thegroove360.filmissimi] newest" + categoria)
    itemlist = []
    item = Item()
    try:
        if categoria == "peliculas":
            item.url = "http://www.filmissimi.net"
            item.action = "elenco"
            itemlist = elenco(item)

            if itemlist[-1].action == "elenco":
                itemlist.pop()

    # Continua la ricerca in caso di errore
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist


# ===========================================================================================================================================

# -------------------------------------------------------------------------------------------------------------------------------------------
def genere(item):
    logger.info("[thegroove360.filmissimi] genere")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data
    # bloque = scrapertools.get_match(data, '<ul id="menu-categorie-1" class="ge">(.*?)</div>')

    patron = '<li id=\"menu-item-.*?menu-item-object-category.*?<a href=\"([^\"]+)\">(.*?)<'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        scrapedplot = ""
        scrapedthumbnail = ""

        itemlist.append(
            Item(channel=__channel__,
                 action="elenco",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png",
                 folder=True))

    return itemlist


# ===========================================================================================================================================

# -------------------------------------------------------------------------------------------------------------------------------------------
def elenco(item):
    logger.info("[thegroove360.filmissimi] elenco")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data

    # elemento = scrapertools.find_single_match(data, '<div class="estre">(.*?)<div class="paginacion">')

    patron = '<div class=\"item\">\s<a href=\"([^\"]+)\" title=\"(.*?)\">\s.*?\s.*?<img src=\"([^\"]+)'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedtitle = scrapedtitle.split(" (")[0]
        logger.info("title=[" + scrapedtitle + "] url=[" + scrapedurl + "] thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 contentType="movie",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 fulltitle=scrapedtitle,
                 extra="movie",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail))

    # Paginazione
    # ===========================================================================================================================
    matches = scrapedSingle(item.url, '<div class="paginacion">(.*?)</div>',
                            "current'>.*?<\/span><.*?href='(.*?)'>.*?</a>")
    if len(matches) > 0:
        paginaurl = matches[0]
        itemlist.append(
            Item(channel=__channel__, action="elenco", title=AvantiTxt, url=paginaurl, thumbnail=AvantiImg))
        itemlist.append(Item(channel=__channel__, action="HomePage", title=HomeTxt, folder=True))
    else:
        itemlist.append(Item(channel=__channel__, action="mainlist", title=ListTxt, folder=True))
    # ===========================================================================================================================
    return itemlist


def findvideos(item):

    data = httptools.downloadpage(item.url).data

    patron = r'<div class=\"(.*?) tr\">\s+<iframe.*?data-lazy-src=\"([^\"]+)\">'
    matches = re.compile(patron, re.MULTILINE).findall(data)

    data = ""
    for scrapedtitle, scrapedurl in matches:
        print scrapedurl
        sdata = httptools.downloadpage(scrapedurl, headers=headers).data

        if "protectlink.stream" in scrapedurl:
            regex = r"Base64.decode\('([^']+)'"
            b64data = scrapertools.find_single_match(sdata, regex)
            import base64
            sdata = base64.b64decode(b64data)

        data += sdata + "\n"

    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        videoitem.title = item.title + videoitem.title
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.show = item.show
        videoitem.plot = item.plot
        videoitem.channel = __channel__

    return itemlist


# ===========================================================================================================================================


# -------------------------------------------------------------------------------------------------------------------------------------------
def search(item, texto):
    logger.info("[thegroove360.filmissimi] init texto=[" + texto + "]")
    itemlist = []
    url = host + "/?s=" + texto

    data = httptools.downloadpage(url, headers=headers).data

    patron = r's-item.*?\s.*?\s.*?\ssrc=\"([^\"]+)\".*?\s.*?\s.*?\s.*?\s.*?\s.*?\s.*?\s.*?\s.*?\s.*?\s.*?\s.*?\s.*?\s.*?\s.*?\s.*\s.*?\s.*?\s.*?\s.*?<a href=\"([^\"]+)\">(.*?)<'
    matches = re.compile(patron, re.MULTILINE).findall(data)

    for scrapedthumbnail, scrapedurl, scrapedtitle in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 fulltitle=scrapedtitle,
                 extra="movie",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail))

    # Paginazione
    # ===========================================================================================================================
    matches = scrapedSingle(url, '<div class="paginacion">(.*?)</div>', "current'>.*?<\/span><.*?href='(.*?)'>.*?</a>")

    if len(matches) > 0:
        paginaurl = matches[0]
        itemlist.append(Item(channel=__channel__, action="elenco", title=AvantiTxt, url=paginaurl, thumbnail=AvantiImg))
        itemlist.append(Item(channel=__channel__, action="HomePage", title=HomeTxt, folder=True))
    else:
        itemlist.append(Item(channel=__channel__, action="mainlist", title=ListTxt, folder=True))
    # ===========================================================================================================================
    return itemlist


# ===========================================================================================================================================

# =================================================================
# Funzioni di servizio
# -----------------------------------------------------------------
def scrapedAll(url="", patron=""):
    matches = []
    data = httptools.downloadpage(url, headers=headers).data
    MyPatron = patron
    matches = re.compile(MyPatron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    return matches


# =================================================================

# -----------------------------------------------------------------
def scrapedSingle(url="", single="", patron=""):
    data = httptools.downloadpage(url, headers=headers).data
    elemento = scrapertools.find_single_match(data, single)
    matches = re.compile(patron, re.DOTALL).findall(elemento)
    scrapertools.printMatches(matches)

    return matches


# =================================================================

# -----------------------------------------------------------------
def HomePage(item):
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.Stefano)")


# =================================================================

# =================================================================
# riferimenti di servizio
# ---------------------------------------------------------------------------------------------------------------------------------
NovitaThumbnail = "https://superrepo.org/static/images/icons/original/xplugin.video.moviereleases.png.pagespeed.ic.j4bhi0Vp3d.png"
GenereThumbnail = "https://farm8.staticflickr.com/7562/15516589868_13689936d0_o.png"
FilmFanart = "https://superrepo.org/static/images/fanart/original/script.artwork.downloader.jpg"
CercaThumbnail = "http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search"
CercaFanart = "https://i.ytimg.com/vi/IAlbvyBdYdY/maxresdefault.jpg"
HomeTxt = "[COLOR yellow]Torna Home[/COLOR]"
ListTxt = "[COLOR orange]Torna a elenco principale [/COLOR]"
AvantiTxt = "[COLOR orange]Successivo>>[/COLOR]"
AvantiImg = "http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png"
thumbnail = "http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"

# ----------------------------------------------------------------------------------------------------------------------------------#----------------------------------------------------------------------------------------------------------------------------------
