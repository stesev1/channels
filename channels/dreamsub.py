# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# TheGroove360 - XBMC Plugin
# Canale per dreamsub
# ------------------------------------------------------------

import re
import urlparse

from core import config, httptools, servertools
from platformcode import logger
from core import scrapertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "dreamsub"

host = "https://www.dreamsub.online"


def mainlist(item):
    logger.info("[thegroove360.dreamsub] mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Anime / Cartoni[/COLOR]",
                     action="serietv",
                     url="%s/anime" % host,
                     thumbnail="http://orig09.deviantart.net/df5a/f/2014/169/2/a/fist_of_the_north_star_folder_icon_by_minacsky_saya-d7mq8c8.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Categorie[/COLOR]",
                     action="categorie",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/popcorn_cinema_movie_.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Ultimi episodi Anime[/COLOR]",
                     action="ultimiep",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/popcorn_cinema_movie_.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca...[/COLOR]",
                     action="search",
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/search_P.png")]

    return itemlist


def newest(categoria):
    logger.info("[thegroove360.dreamsub] newest" + categoria)
    itemlist = []
    item = Item()
    try:
        if categoria == "anime":
            item.url = "https://www.dreamsub.online"
            item.action = "ultimiep"
            itemlist = ultimiep(item)

            if itemlist[-1].action == "ultimiep":
                itemlist.pop()
    # Continua la ricerca in caso di errore 
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist


def serietv(item):
    logger.info("[thegroove360.dreamsub] peliculas")
    itemlist = []

    # Carica la pagina 
    data = httptools.downloadpage(item.url).data
    bloque = scrapertools.get_match(data,
                                    '<input type="submit" value="Vai!" class="blueButton">(.*?)<div class="footer">')

    # Estrae i contenuti 
    patron = 'Lingua[^<]+<br>\s*<a href="([^"]+)" title="([^"]+)">'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        scrapedurl = host + scrapedurl
        scrapedplot = ""
        scrapedthumbnail = ""
        scrapedtitle = scrapedtitle.replace("Streaming", "")
        scrapedtitle = scrapedtitle.replace("Lista episodi ", "")
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='tv'))

    # Paginazione 
    patronvideos = '<li class="currentPage">[^>]+><li[^<]+<a href="([^"]+)">'
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
                 action="serietv",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png",
                 folder=True))

    return itemlist


def ultimiep(item):
    logger.info("[thegroove360.dreamsub] ultimiep")
    itemlist = []

    # Carica la pagina 
    data = httptools.downloadpage(item.url).data
    bloque = scrapertools.get_match(data, '<ul class="last" id="recentAddedEpisodesAnimeDDM">(.*?)</ul>')

    # Estrae i contenuti 
    patron = '<li><a href="([^"]+)"[^>]+>([^<]+)<br>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        ep = scrapertools.find_single_match(scrapedtitle, r'\d+$').zfill(2)
        scrapedtitle = re.sub(r'\d+$', ep, scrapedtitle)
        scrapedurl = host + scrapedurl
        scrapedplot = ""
        scrapedthumbnail = ""
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 fulltitle=re.sub(r'\d*-?\d+$', '', scrapedtitle).strip(),
                 show=scrapedtitle,
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='tv'))
    return itemlist


def categorie(item):
    logger.info("[thegroove360.dreamsub] categorie")
    itemlist = []

    data = httptools.downloadpage(item.url).data
    blocco = scrapertools.find_single_match(data, r'<select name="genere" id="genere" class="selectInput">(.*?)</select>')
    patron = r'<option value="([^"]+)">'
    matches = re.compile(patron, re.DOTALL).findall(blocco)

    for value in matches:
        url = "%s/genere/%s" % (host, value)
        itemlist.append(
                Item(channel=__channel__,
                     action="serietv",
                     title="[COLOR azure]%s[/COLOR]" % value.capitalize(),
                     url=url,
                     extra="tv",
                     thumbnail=item.thumbnail,
                     folder=True))
                     
    return itemlist

def HomePage(item):
    import xbmc
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.Stefano)")


def search(item, texto):
    logger.info("[thegroove360.dreamsub] " + item.url + " search " + texto)
    item.url = "%s/search/%s" % (host, texto)
    try:
        return serietv(item)
    # Continua la ricerca in caso di errore 
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def episodios(item):
    logger.info("[thegroove360.dreamsub] episodios")

    itemlist = []

    data = httptools.downloadpage(item.url).data
    bloque = scrapertools.get_match(data, '<div class="seasonEp">(.*?)<div class="footer">')

    patron = '<li><a href="([^"]+)"[^<]+<b>(.*?)<\/b>[^>]+>([^<]+)<\/i>(.*?)<'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, title1, title2, title3 in matches:
        scrapedurl = host + scrapedurl
        scrapedtitle = title1 + " " + title2 + title3
        scrapedtitle = scrapedtitle.replace("Download", "")
        scrapedtitle = scrapedtitle.replace("Streaming", "")
        scrapedtitle = scrapedtitle.replace("& ", "")
        scrapedtitle = re.sub(r'\s+', ' ', scrapedtitle)

        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 fulltitle=scrapedtitle,
                 show=item.show,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=item.thumbnail,
                 plot=item.plot,
                 folder=True))

    if config.get_library_support() and len(itemlist) != 0:
        itemlist.append(
            Item(channel=__channel__,
                 title="Aggiungi alla libreria",
                 url=item.url,
                 action="add_serie_to_library",
                 extra="episodios",
                 show=item.show))

    return itemlist

def findvideos(item):
    logger.info()

    print item.url
    data = httptools.downloadpage(item.url).data

    itemlist = servertools.find_video_items(data=data)
    if 'keepem.online' in data:
        urls = scrapertools.find_multiple_matches(data, r'(https://keepem\.online/f/[^"]+)"')
        for url in urls:
            url = httptools.downloadpage(url).url
            itemlist += servertools.find_video_items(data=url)
                
    for videoitem in itemlist:
        server = re.sub(r'[-\[\]\s]+', '', videoitem.title)
        videoitem.title = "".join(["[[COLOR orange]%s[/COLOR]] " % server.capitalize(), item.title])
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__

    return itemlist