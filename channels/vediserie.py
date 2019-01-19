# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# TheGroove360 / XBMC Plugin
# Canale 
# ------------------------------------------------------------

import re

from core import config, httptools
from platformcode import logger
from core import scrapertools
from core import servertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "vediserie"

host = "http://www.vediserie.tv"


def mainlist(item):
    logger.info("[vediserie.py] mainlist")

    itemlist = [Item(channel=__channel__,
                     action="fichas",
                     title="[COLOR azure]Serie TV[/COLOR]",
                     url="%s/category/serie-tv/" % host,
                     thumbnail="http://i.imgur.com/rO0ggX2.png"),
                Item(channel=__channel__,
                     action="search",
                     extra="serie",
                     title="[COLOR yellow]Cerca...[/COLOR]",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search")]

    return itemlist


def search(item, texto):
    logger.info("[vediserie.py] search")

    item.url = host + "/?s=" + texto

    try:
        return fichas(item)

    # Continua la ricerca in caso di errore .
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def fichas(item):
    logger.info("[vediserie.py] fichas")
    itemlist = []

    data = httptools.downloadpage(item.url).data

    patron = '<h2>[^>]+>\s*'
    patron += '<img[^=]+=[^=]+=[^=]+="([^"]+)"[^>]+>\s*'
    patron += '<A HREF=([^>]+)>[^>]+>[^>]+>[^>]+>\s*'
    patron += '[^>]+>[^>]+>(.*?)</[^>]+>[^>]+>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedthumbnail, scrapedurl, scrapedtitle in matches:
        scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        if scrapedtitle.startswith('<span class="year">'):
            scrapedtitle = scrapedtitle[19:]

        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 title=scrapedtitle,
                 fulltitle=scrapedtitle,
                 url=scrapedurl.replace('"', ''),
                 show=scrapedtitle,
                 thumbnail=scrapedthumbnail), tipo='tv'))

    patron = '<span class=\'current\'>[^<]+</span><a class="page larger" href="(.*?)">'
    next_page = scrapertools.find_single_match(data, patron)
    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="fichas",
                 title="[COLOR orange]Successivo>>[/COLOR]",
                 url=next_page))

    return itemlist


def episodios(item):
    logger.info("[vediserie.py] episodios")

    itemlist = []

    # Carica la pagina 
    data = httptools.downloadpage(item.url).data

    patron = r'<div class="list" data-stagione="([^"]+)">\s*'
    patron += r'<ul class="listEpis">\s*'
    patron += r'<li><a href="javascript:void\(0\)" data-link="([^"]+)" data-id="([^"]+)">'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for season, url, episode in matches:
        season = str(int(season) + 1)
        episode = str(int(episode) + 1)
        if len(episode) == 1: episode = "0" + episode
        title = season + "x" + episode
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 contentType="episode",
                 title=title,
                 url=item.url,
                 thumbnail=item.thumbnail,
                 extra=url,
                 fulltitle=title + ' - ' + item.show,
                 show=item.show))

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
    logger.info("[vediserie.py]==> findvideos")
    itemlist = servertools.find_video_items(data=item.extra)

    for videoitem in itemlist:
        server = re.sub(r'[-\[\]\s]+', '', videoitem.title).capitalize()
        videoitem.title = "".join(["[%s] " % color(server, 'orange'), item.title])
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.show = item.show
        videoitem.plot = item.plot
        videoitem.channel = __channel__

    return itemlist

def color(text, color):
    return "[COLOR " + color + "]" + text + "[/COLOR]"

