# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Thegroove360 - XBMC Plugin
# Canale  per eurostreaming.tv
# ------------------------------------------------------------

import re
import urlparse

from core import config, httptools, scrapertools, servertools
from core.item import Item
from core.tmdb import infoSod
from platformcode import logger

__channel__ = "eurostreaming"

host = "https://eurostreaming.zone"


def mainlist(item):
    logger.info("[thegroove360.eurostreaming] mainlist")
    itemlist = [
        Item(
            channel=__channel__,
            title="[COLOR azure]Ultimi Aggiornamenti[/COLOR]",
            action="serietv",
            extra='serie',
            url=host,
            thumbnail=
            "https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/popcorn_cinema_movie_.png"
        ),
        Item(
            channel=__channel__,
            title="[COLOR azure]Serie TV[/COLOR]",
            action="serietv",
            extra='serie',
            url="%s/category/serie-tv-archive/" % host,
            thumbnail=
            "https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/popcorn_cinema_movie_.png"
        ),
        Item(
            channel=__channel__,
            title="[COLOR azure]Anime / Cartoni[/COLOR]",
            action="serietv",
            extra='serie',
            url="%s/category/anime-cartoni-animati/" % host,
            thumbnail=
            "http://orig09.deviantart.net/df5a/f/2014/169/2/a/fist_of_the_north_star_folder_icon_by_minacsky_saya-d7mq8c8.png"
        ),
        Item(
            channel=__channel__,
            title="[COLOR yellow]Cerca...[/COLOR]",
            action="search",
            extra='serie',
            thumbnail=
            "https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/search_P.png")
    ]

    return itemlist


def serietv(item):
    logger.info("[thegroove360.eurostreaming] peliculas")
    itemlist = []

    # Carica la pagina
    data = httptools.downloadpage(item.url).data

    # Estrae i contenuti
    patron = r'<div class="post-thumb">\s*<a href="([^"]+)" title="([^"]+)">\s*<img src="([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        scrapedplot = ""
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle.replace("Streaming", ""))
        if scrapedtitle.startswith("Link to "):
            scrapedtitle = scrapedtitle[8:]
        num = scrapertools.find_single_match(scrapedurl, '(-\d+/)')
        if num:
            scrapedurl = scrapedurl.replace(num, "-episodi/")
        itemlist.append(
            infoSod(
                Item(
                    channel=__channel__,
                    action="episodios",
                    fulltitle=scrapedtitle,
                    show=scrapedtitle,
                    title=scrapedtitle,
                    url=scrapedurl,
                    thumbnail=scrapedthumbnail,
                    plot=scrapedplot,
                    extra=item.extra,
                    folder=True),
                tipo='tv'))

    # Paginazione
    patronvideos = '<a class="next page-numbers" href="?([^>"]+)">Avanti &raquo;</a>'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(
                channel=__channel__,
                action="HomePage",
                title="[COLOR yellow]Torna Home[/COLOR]",
                folder=True)),
        itemlist.append(
            Item(
                channel=__channel__,
                action="serietv",
                title="[COLOR orange]Successivo >>[/COLOR]",
                url=scrapedurl,
                thumbnail=
                "https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/next_1.png",
                extra=item.extra,
                folder=True))

    return itemlist


def HomePage(item):
    import xbmc
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.Stefano)")


def search(item, texto):
    logger.info("[eurostreaming.py] " + item.url + " search " + texto)
    item.url = "%s/?s=%s" % (host, texto)
    try:
        return serietv(item)
    # Continua la ricerca in caso di errore
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def episodios(item):
    def load_episodios():
        for data in match.split('<br />'):
            ## Estrae i contenuti
            end = data.find('<a ')
            if end > 0:
                scrapedtitle = scrapertools.find_single_match(data[:end], '\d+[^\d]+\d+')
                scrapedtitle = scrapedtitle.replace('×', 'x')
                itemlist.append(
                    Item(
                        channel=__channel__,
                        action="findvideos",
                        contentType="episode",
                        title=scrapedtitle + " (" + lang_title + ")",
                        url=data,
                        thumbnail=item.thumbnail,
                        extra=item.extra,
                        fulltitle=scrapedtitle + " (" + lang_title + ")" + ' - ' + item.show,
                        show=item.show))

    logger.info("[thegroove360.eurostreaming] episodios")

    itemlist = []

    ## Carica la pagina
    data = httptools.downloadpage(item.url).data

    patron = r'go_to\":\"([^\"]+)\"'
    matches = re.compile(patron, re.IGNORECASE).findall(data)

    if len(matches) > 0:
        url = matches[0].replace("\/", "/")
        data = httptools.downloadpage(url).data

    patron = r"onclick=\"top.location=atob\('([^']+)'\)\""
    b64_link = scrapertools.find_single_match(data, patron)
    if b64_link != '':
        import base64
        data = httptools.downloadpage(base64.b64decode(b64_link)).data

    patron = r'<a href="(%s/\?p=\d+)">' % host
    link = scrapertools.find_single_match(data, patron)
    if link != '':
        data = httptools.downloadpage(link).data

    data = scrapertools.decodeHtmlentities(data)

    patron = r'</span>([^<]+)</div><div class="su-spoiler-content su-clearfix" style="display:none">(.+?)</div></div></div>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for lang_title, match in matches:
        lang_title = 'SUB ITA' if 'SUB' in lang_title.upper() else 'ITA'
        load_episodios()

    patron = '<li><span style="[^"]+"><a onclick="[^"]+" href="[^"]+">([^<]+)</a>(?:</span>\s*<span style="[^"]+"><strong>([^<]+)</strong>)?</span>(.*?)</div>\s*</li>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for lang_title1, lang_title2, match in matches:
        lang_title = 'SUB ITA' if 'SUB' in (
            lang_title1 + lang_title2).upper() else 'ITA'
        load_episodios()

    if config.get_library_support() and len(itemlist) != 0:
        itemlist.append(
            Item(
                channel=__channel__,
                title="Aggiungi alla libreria",
                url=item.url,
                action="add_serie_to_library",
                extra="episodios" + "###" + item.extra,
                show=item.show))

    return itemlist

def findvideos(item):
    logger.info("[thegroove360.eurostreaming] findvideos")
    itemlist=[]

    # Carica la pagina
    data = item.url

    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        videoitem.title = item.title + videoitem.title
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.show = item.show
        videoitem.plot = item.plot
        videoitem.channel = __channel__

    return itemlist