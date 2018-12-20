# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# TheGroove360 - XBMC Plugin
# Canale per mondoserietv
# ------------------------------------------------------------

import re
import urllib

# from channels import autoplay
from channels import filtertools
from core import servertools, scrapertools, httptools
from core.item import Item
# from core.tmdb import infoIca
from lib.unshortenit import unshorten
from platformcode import logger
from core.tmdb import infoSod
from core import config

# from servers import servertools

__channel__ = "mondoserietv"

host = "https://mondoserietv.com"
IDIOMAS = {'Italiano': 'IT'}
list_language = IDIOMAS.values()
list_servers = ['akstream']
list_quality = ['default']

__comprueba_enlaces__ = config.get_setting('comprueba_enlaces', 'mondoserietv')
__comprueba_enlaces_num__ = config.get_setting('comprueba_enlaces_num', 'mondoserietv')

headers = {'Referer': host}

PERPAGE = 14


def mainlist(item):
    logger.info("[thegroove360.mondoserietv] mainlist")

    # autoplay.init(item.channel, list_servers, list_quality)

    itemlist = [Item(channel=item.channel,
                     action="lista_serie",
                     title="[COLOR azure]Lista Serie Tv Anni 50 60 70 80[/COLOR]",
                     url=("%s/lista-serie-tv-anni-60-70-80/" % host),
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/popcorn_cinema_movie_.png"),
                Item(channel=item.channel,
                     action="lista_serie",
                     title="[COLOR azure]Lista Serie Tv Italiane[/COLOR]",
                     url=("%s/lista-serie-tv-italiane/" % host),
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/popcorn_cinema_movie_.png"),
                Item(channel=item.channel,
                     action="lista_serie",
                     title="[COLOR azure]Lista Cartoni Animati & Anime[/COLOR]",
                     url=("%s/lista-cartoni-animati-e-anime/" % host),
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/popcorn_cinema_movie_.png"),
                Item(channel=item.channel,
                     action="peliculas",
                     title="[COLOR azure]Lista Film[/COLOR]",
                     url=("%s/lista-film/" % host),
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/popcorn_cinema_movie_.png"),
                Item(channel=item.channel,
                     title="[COLOR yellow]Cerca Film...[/COLOR]",
                     action="search",
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/search_P.png"),
                Item(channel=item.channel,
                     title="[COLOR yellow]Cerca SerieTV...[/COLOR]",
                     action="search",
                     extra="tvshow",
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/search_P.png")]
    # autoplay.show_option(item.channel, itemlist)

    return itemlist


def search(item, texto):
    logger.info("[thegroove360.mondoserietv] search " + texto)
    item.url = "%s/?s=%s" % (host, texto)

    try:
        if item.extra == "movie":
            return search_peliculas(item)
        if item.extra == "tvshow":
            return search_peliculas_tv(item)

    # Continua la ricerca in caso di errore
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def search_peliculas(item):
    logger.info("[thegroove360.mondoserietv] search_peliculas")
    itemlist = []

    # Carica la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Estrae i contenuti
    patron = '<div class="boxinfo">\s*<a href="([^"]+)">\s*<span class="tt">(.*?)</span>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        scrapedplot = ""
        scrapedthumbnail = ""
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)

        itemlist.append(infoSod(
            Item(channel=item.channel,
                 action="findvideos",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 extra=item.extra,
                 folder=True), tipo='movie'))

    return itemlist


def search_peliculas_tv(item):
    logger.info("[thegroove360.mondoserietv] search_peliculas_tv")
    itemlist = []

    # Carica la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Estrae i contenuti
    patron = '<div class="boxinfo">\s*<a href="([^"]+)">\s*<span class="tt">(.*?)</span>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        scrapedplot = ""
        scrapedthumbnail = ""
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)

        itemlist.append(infoSod(
            Item(channel=item.channel,
                 action="episodios",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 extra=item.extra,
                 folder=True), tipo='tv'))

    return itemlist


def peliculas(item):
    logger.info("[thegroove360.mondoserietv] film")
    itemlist = []

    p = 1
    if '{}' in item.url:
        item.url, p = item.url.split('{}')
        p = int(p)

    data = httptools.downloadpage(item.url, headers=headers).data

    blocco = scrapertools.find_single_match(data, '<div class="entry-content pagess">(.*?)</ul>')
    patron = r'<a href="(.*?)" title="(.*?)">'
    matches = re.compile(patron, re.DOTALL).findall(blocco)

    for i, (scrapedurl, scrapedtitle) in enumerate(matches):
        if (p - 1) * PERPAGE > i: continue
        if i >= p * PERPAGE: break
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(infoSod(Item(channel=item.channel,
                                     contentType="movie",
                                     action="findvideos",
                                     title=scrapedtitle,
                                     fulltitle=scrapedtitle,
                                     url=scrapedurl,
                                     fanart=item.fanart if item.fanart != "" else item.scrapedthumbnail,
                                     show=item.fulltitle,
                                     folder=True), tipo='movie'))

    if len(matches) >= p * PERPAGE:
        scrapedurl = item.url + '{}' + str(p + 1)
        itemlist.append(
            Item(channel=item.channel,
                 extra=item.extra,
                 action="peliculas",
                 title="[COLOR lightgreen]" + config.get_localized_string(30992) + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/next_1.png",
                 folder=True))

    return itemlist


def lista_serie(item):
    logger.info("[thegroove360.mondoserietv] novità")
    itemlist = []

    p = 1
    if '{}' in item.url:
        item.url, p = item.url.split('{}')
        p = int(p)

    data = httptools.downloadpage(item.url, headers=headers).data

    blocco = scrapertools.find_single_match(data, '<div class="entry-content pagess">(.*?)</ul>')
    patron = r'<a href="(.*?)" title="(.*?)">'
    matches = re.compile(patron, re.DOTALL).findall(blocco)
    scrapertools.printMatches(matches)

    for i, (scrapedurl, scrapedtitle) in enumerate(matches):
        if (p - 1) * PERPAGE > i: continue
        if i >= p * PERPAGE: break
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(infoSod(Item(channel=item.channel,
                                     action="episodios",
                                     title=scrapedtitle,
                                     fulltitle=scrapedtitle,
                                     url=scrapedurl,
                                     fanart=item.fanart if item.fanart != "" else item.scrapedthumbnail,
                                     show=item.fulltitle,
                                     folder=True), tipo='tv'))

    if len(matches) >= p * PERPAGE:
        scrapedurl = item.url + '{}' + str(p + 1)
        itemlist.append(
            Item(channel=item.channel,
                 extra=item.extra,
                 action="lista_serie",
                 title="[COLOR lightgreen]" + config.get_localized_string(30992) + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/next_1.png",
                 folder=True))

    return itemlist


def episodios(item):
    logger.info("[thegroove360.mondoserietv] episodios")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data
    patron = '<input type="hidden" name="id" value="(.*?)">'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for id_post in matches:
        post = "https://player.mondoserietv.com/media/embedgs.php?id_post=" + id_post

    data = httptools.downloadpage(item.url, headers=headers).data
    blocco = scrapertools.get_match(data, '<table>(.*?)</table>')

    patron = '<tr><td><b>(.*?)(\d+)((?:x\d+| ))(.*?)<\/b><\/td>'
    matches = re.compile(patron, re.DOTALL).findall(blocco)

    for t1, s, e, t2 in matches:

        if "x" not in e:
            e = s

        if e == s:
            s = None

        if s is None:
            s = "1"

        # if s.startswith('0'):
        #    s = s.replace("0", "")

        if e.startswith('x'):
            e = e.replace("x", "")

        scrapedtitle = t1 + s + "x" + e + " " + t2
        scrapedurl = post + "&season=" + s + "&episode=" + e
        itemlist.append(
            Item(channel=item.channel,
                 contentType="episode",
                 action="findvideos",
                 items=s,
                 iteme=e,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=item.url,
                 thumbnail=item.scrapedthumbnail,
                 plot=item.scrapedplot,
                 folder=True))

    if len(itemlist) != 0:
        itemlist.append(
            Item(channel=item.channel,
                 title="[COLOR lightblue]%s[/COLOR]" % config.get_localized_string(30161),
                 url=item.url,
                 action="add_serie_to_library",
                 extra="episodios",
                 show=item.show))

    return itemlist


def findvideos(item):
    logger.info(" findvideos")

    if item.contentType != "episode":
        return findvideos_movie(item)

    data = httptools.downloadpage(item.url, headers=headers).data

    regex = r"<td>.*" + item.fulltitle.replace("  ", " ") + ".*&nbsp;.*<a href=.*\starget='_blank'><img.*<\/td>"

    b = re.compile(regex, re.MULTILINE).findall(data)

    print  b[0]

    if b:
        blocco = b[0]
    else:
        return []

    itemlist = servertools.find_video_items(data=blocco)
    for videoitem in itemlist:
        videoitem.title = item.title + videoitem.title
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.show = item.show
        videoitem.plot = item.plot
        videoitem.channel = __channel__

    return itemlist


def findvideos_movie(item):
    logger.info(" findvideos_movie")

    # Carica la pagina

    data = httptools.downloadpage(item.url).data

    patron = r"<a href='([^']+)'[^>]*?>[^<]*?<img src='[^']+' style='[^']+' alt='[^']+'>[^<]+?</a>"
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl in matches:
        url, c = unshorten(scrapedurl)
        data += url + '\n'

    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        videoitem.title = "".join([item.title, '[COLOR green][B]' + videoitem.title + '[/B][/COLOR]'])
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.show = item.show
        videoitem.plot = item.plot
        videoitem.channel = item.channel
        videoitem.contentType = item.contentType

    return itemlist
