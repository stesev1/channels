# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# TheGroove360 - XBMC Plugin
# Canale filmperevolvere
# ------------------------------------------------------------

import re
import urlparse

import lib.pyaes as aes
from core import httptools
from platformcode import logger
from core import scrapertools
from core import servertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "filmperevolvere"

host = "https://filmperevolvere.it"

headers = [
    ['User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:54.0) Gecko/20100101 Firefox/54.0'],
    ['Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'],
    ['Accept-Encoding', 'gzip, deflate'],
    ['Accept-Language', 'en-US,en;q=0.5'],
    ['Referer', host],
    ['DNT', '1'],
    ['Upgrade-Insecure-Requests', '1'],
    ['Cache-Control', 'max-age=0']
]


def mainlist(item):
    logger.info("[thegroove360.filmperevolvere] mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Ultimi Film Inseriti[/COLOR]",
                     action="peliculas",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/popcorn_cinema_movie_.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Categorie[/COLOR]",
                     action="categorie",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/popcorn_cinema_movie_.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca...[/COLOR]",
                     action="search",
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/search_P.png")]

    return itemlist


def newest(categoria):
    logger.info("[filmperevolvere.py] newest" + categoria)
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


def search(item, texto):
    logger.info("[filmperevolvere.py] " + item.url + " search " + texto)
    item.url = host + "/?s=" + texto

    try:
        return peliculas(item)

    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)

    return []


def categorie(item):
    itemlist = []

    c = get_test_cookie(item.url)
    if c: headers.append(['Cookie', c])

    # Carica la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data
    bloque = scrapertools.get_match(data,'GENERI.*\s<ul class="mega-sub-menu">\s(.*?)<\/ul>')

    # Estrae i contenuti 
    patron = 'href="([^"]*)">([^<]*)<'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:

        if scrapedtitle.startswith(("HOME")):
            continue
        if scrapedtitle.startswith(("SERIE TV")):
            continue
        if scrapedtitle.startswith(("GENERI")):
            continue

        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas2",
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/popcorn_cinema_movie_.png",
                 folder=True))

    return itemlist


def peliculas(item):
    logger.info("[thegroove360.filmperevolvere] peliculas")
    itemlist = []

    c = get_test_cookie(item.url)
    if c: headers.append(['Cookie', c])

    if item.url[1]=="|":
        patron = 'class="ei-item-title"><a\s*href="([^"]*)">([^<]*)'
        item.url=item.url[2:]
    else:
        patron = '<div class="post-thumbnail">\s*<a href="([^"]+)" title="Permalink a([^"]+)">\s.*?src="(.*?)"'

    # Carica la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data

    # Estrae i contenuti 
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        scrapedplot = ""
        scrapedtitle = scrapedtitle.title()
        txt = "Serie Tv"
        if txt in scrapedtitle: continue
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
    patronvideos = 'rel="next" href="(.*?)"'
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
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/5abaf5c6bc9e50ca4595082c8956375fbc38d909/images/channels_icon/next_1.png",
                 folder=True))

    return itemlist


def findvideos(item):
    logger.info("[thegroove360.filmperevolvere] findvideos")

    c = get_test_cookie(item.url)
    if c: headers.append(['Cookie', c])

    # Carica la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data

    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        videoitem.title = "".join([item.title, '[COLOR green][B]', videoitem.title, '[/B][/COLOR]'])
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__

    return itemlist


def HomePage(item):
    import xbmc
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.Stefano)")


def get_test_cookie(url):
    data = httptools.downloadpage(url, headers=headers).data
    a = scrapertools.find_single_match(data, 'a=toNumbers\("([^"]+)"\)')
    if a:
        b = scrapertools.find_single_match(data, 'b=toNumbers\("([^"]+)"\)')
        if b:
            c = scrapertools.find_single_match(data, 'c=toNumbers\("([^"]+)"\)')
            if c:
                cookie = aes.AESModeOfOperationCBC(a.decode('hex'), iv=b.decode('hex')).decrypt(c.decode('hex'))
                return '__test=%s' % cookie.encode('hex')
    return ''

def peliculas2(item):
    logger.info("[thegroove360.filmperevolvere] peliculas2")
    itemlist = []

    c = get_test_cookie(item.url)
    if c: headers.append(['Cookie', c])

    if item.url[1]=="|":
        patron = 'class="ei-item-title"><a\s*href="([^"]*)">([^<]*)'
        item.url=item.url[2:]
    else:
        patron = '<div class="ei-item-image"><a href="(.*?)"><img src="(.*?)\?.*?href.*?>(.*?)<'

    # Carica la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Estrae i contenuti
    matches = re.compile(patron, re.IGNORECASE).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        scrapedplot = ""
        #scrapedtitle = scrapedtitle.title()
        #txt = "Serie Tv"
        #if txt in scrapedtitle: continue
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
    patronvideos = '<li class="next right"><a href="([^"]+)"[^>]+>'
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
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/5abaf5c6bc9e50ca4595082c8956375fbc38d909/images/channels_icon/next_1.png",
                 folder=True))

    return itemlist
