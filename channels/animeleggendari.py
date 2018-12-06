# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Thegroove360 - XBMC Plugin
# Canale  per http://www.animeleggendari.com/
# ------------------------------------------------------------

import re

from core import servertools, httptools, scrapertools
from platformcode import logger
from core.item import Item
from core.tmdb import infoSod

__channel__ = "animeleggendari"

host = "https://animeleggendari.com"

# ----------------------------------------------------------------------------------------------------------------
def mainlist(item):
    logger.info()
    itemlist = [Item(channel=__channel__,
                     action="lista_anime",
                     title=color("Anime Leggendari", "red"),
                     url="%s/category/anime-leggendari/" % host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/popcorn_cinema_movie_.png"),
                Item(channel=__channel__,
                     action="lista_anime",
                     title=color("Anime Conclusi", "azure"),
                     url="%s/category/serie-anime-concluse/" % host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/popcorn_cinema_movie_.png"),
                Item(channel=__channel__,
                     action="lista_anime",
                     title=color("Anime in corso", "azure"),
                     url="%s/category/anime-in-corso/" % host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/popcorn_cinema_movie_.png"),
                Item(channel=__channel__,
                     action="search",
                     title=color("Cerca anime ...", "yellow"),
                     extra="anime",
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/search_P.png")]

    return itemlist

# ================================================================================================================
# ----------------------------------------------------------------------------------------------------------------
def search(item, texto):
    logger.info()
    item.url = host + "/?s=" + texto
    try:
        return lista_anime(item)
    # Continua la ricerca in caso di errore 
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def lista_anime(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    patron = r'<a class="[^"]+" href="([^"]+)" title="([^"]+)"><img[^s]+src="([^"]+)"[^>]+'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle.strip()).replace("streaming", "")
        if 'top 10 anime da vedere' in scrapedtitle.lower(): continue

        lang = scrapertools.find_single_match(scrapedtitle, r"((?:SUB ITA|ITA))")
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodi",
                 contentType="tv",
                 title=scrapedtitle.replace(lang, color(lang, "red")),
                 fulltitle=scrapedtitle.replace(lang, ""),
                 url=scrapedurl,
                 extra="tv",
                 thumbnail=scrapedthumbnail,
                 folder=True), tipo="tv"))

    patronvideos = r'<a class="next page-numbers" href="([^"]+)">'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = matches[0]
        itemlist.append(
            Item(channel=__channel__,
                 action="HomePage",
                 title=color("Torna Home", "yellow"),
                 folder=True)),
        itemlist.append(
            Item(channel=__channel__,
                 action="lista_anime",
                 title=color("Successivo >>", "orange"),
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/next_1.png",
                 folder=True))

    return itemlist

# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def episodi(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    blocco = scrapertools.find_single_match(data, r'(?:<p style="text-align: left;">|<div class="pagination clearfix">\s*)(.*?)</span></a></div>')

    # Il primo episodio è la pagina stessa
    itemlist.append(
        Item(channel=__channel__,
             action="findvideos",
             contentType="tv",
             title="Episodio: 1",
             fulltitle="%s %s %s " % (color(item.title, "deepskyblue"), color("|", "azure"), color("1", "orange")),
             url=item.url,
             extra="tv",
             thumbnail=item.thumbnail,
             folder=True))
    if blocco != "":
        patron = r'<a href="([^"]+)"><span class="pagelink">(\d+)</span></a>'
        matches = re.compile(patron, re.DOTALL).findall(data)
        for scrapedurl, scrapednumber in matches:
            itemlist.append(
                Item(channel=__channel__,
                     action="findvideos",
                     contentType="tv",
                     title="Episodio: %s" % scrapednumber,
                     fulltitle="%s %s %s " % (color(item.title, "deepskyblue"), color("|", "azure"), color(scrapednumber, "orange")),
                     url=scrapedurl,
                     extra="tv",
                     thumbnail=item.thumbnail,
                     folder=True))

    return itemlist

# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def findvideos(item):
    logger.info()

    data = httptools.downloadpage(item.url).data
    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        server = re.sub(r'[-\[\]\s]+', '', videoitem.title)
        videoitem.title = "".join(["[%s] " % color(server.capitalize(), 'orange'), item.title])
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__
    return itemlist

# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def color(text, color):
    return "[COLOR "+color+"]"+text+"[/COLOR]"

def HomePage(item):
    import xbmc
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.Stefano/?action=sod)")

# ================================================================================================================
