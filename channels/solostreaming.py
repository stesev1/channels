# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# TheGroove360 / XBMC Plugin
# Canale 
# ------------------------------------------------------------

import re

from core import config, httptools, scrapertools, servertools
from core.item import Item
from core.tmdb import infoSod
from platformcode import logger
from servers.decrypters import link4me

__channel__ = "solostreaming"

host = "http://solo-streaming.com"
host_2 = "http://serietv.solo-streaming.com/elenco/serietv/"

PERPAGE = 10


def mainlist(item):
    logger.info("Stefano.channels.solostreaming mainlist")

    itemlist = [Item(channel=__channel__,
                     action="lista_serie",
                     title="[COLOR azure]Novità[/COLOR]",
                     url=host,
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png",
                     folder=True),
                Item(channel=__channel__,
                     action="elenco",
                     title="[COLOR azure]Elenco SerieTV[/COLOR]",
                     url=host_2,
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png",
                     folder=True),
                Item(channel=__channel__,
                     action="search",
                     extra="serie",
                     title="[COLOR yellow]Cerca...[/COLOR]",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search",
                     folder=True)]
    return itemlist


def search(item, texto):
    logger.info("Stefano.channels.solostreaming search")
    item.url = host + "/search/" + texto

    try:
        return serie_src(item)
    # Stop search in case of fault
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


# Newest ----------------------------------------------------------------------
def newest(categoria):
    logger.info("Stefano.channels.solostreaming newest" + categoria)
    itemlist = []
    item = Item()
    try:
        if categoria == "series":
            item.url = host
            item.action = "lista_serie_newest"
            itemlist = lista_serie_newest(item)

            if itemlist[-1].action == "lista_serie_newest":
                itemlist.pop()

    # Continua la ricerca in caso di errore 
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist


def lista_serie_newest(item):
    logger.info("Stefano.channels.solostreaming lista_serie_newest")
    itemlist = []

    data = httptools.downloadpage(item.url).data
    blocco = scrapertools.find_single_match(data, r'<ul class="recent-update"[^>]+>(.*?)</ul>')

    patron = '<h2[^>]+>\s*<a class="post-data" title="(.*?)" data="(.*?)" href="([^"]+)" style[^>]+>'
    matches = re.compile(patron, re.DOTALL).findall(blocco)

    for scrapedtitle, scrapedtitle_2, scrapedurl in matches:
        scrapedurl += "/episodi/"
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle).strip()
        scrapedtitle_2 = re.sub(r'\s+', ' ', scrapertools.decodeHtmlentities(scrapedtitle_2)).strip()
        complete_title = '%s %s' % (scrapedtitle, scrapedtitle_2)

        patron_extra = r'<br>.*?%s[^<]+(.*?)<br>' % scrapertools.find_single_match(scrapedtitle_2, r'(\d+x\d+)')

        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos_single_ep",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 extra=patron_extra,
                 contentSerieName=complete_title,
                 title=complete_title,
                 url=scrapedurl,
                 folder=True), tipo='tv'))

    return itemlist


def findvideos_single_ep(item):
    logger.info("Stefano.channels.solostreaming findvideos_single_ep")

    # Download Pagina
    data = httptools.downloadpage(item.url).data

    # Estraggo l'episodio
    data = scrapertools.find_single_match(data, item.extra)

    matches = re.compile(r'href="([^"]+)"', re.DOTALL).findall(data)
    urls = ''
    for url in matches:
        if 'link4' in url:
            urls += link4me.get_long_url(url, item.url)
        else:
            urls += url
    itemlist = servertools.find_video_items(data=urls)

    for videoitem in itemlist:
        server = re.sub(r'[-\[\]\s]+', '', videoitem.title).capitalize()
        videoitem.title = " ".join(["[[COLOR orange]%s[/COLOR]]" % server, item.title])
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.show = item.show
        videoitem.plot = item.plot
        videoitem.channel = __channel__

    return itemlist


# =============================================================================

def serie_src(item):
    logger.info("Stefano.channels.solostreaming src")
    itemlist = []

    p = 1
    if '{}' in item.url:
        item.url, p = item.url.split('{}')
        p = int(p)

    data = httptools.downloadpage(item.url).data

    patron = '<h1 class="serie-title"><a[\s\S]*href="([^"]+)">(.*?)<\/a><\/h1>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for i, (scrapedurl, scrapedtitle) in enumerate(matches):
        if (p - 1) * PERPAGE > i: continue
        if i >= p * PERPAGE: break
        scrapedplot = ""
        scrapedthumbnail = ""
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedtitle = scrapedtitle.replace("streaming", "")
        scrapedurl = scrapedurl + "/episodi/"
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

    # Per page
    if len(matches) >= p * PERPAGE:
        scrapedurl = item.url + '{}' + str(p + 1)
        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="serie_src",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png",
                 folder=True))

    return itemlist


def elenco(item):
    logger.info("Stefano.channels.solostreaming elenco")
    itemlist = []

    p = 1
    if '{}' in item.url:
        item.url, p = item.url.split('{}')
        p = int(p)

    data = httptools.downloadpage(item.url).data
    bloque = scrapertools.get_match(data, '<div id="content">(.*?)</div>')

    patron = '<a href="([^"]+)" title=[^>]+>(.*?)</a><br>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for i, (scrapedurl, scrapedtitle) in enumerate(matches):
        if (p - 1) * PERPAGE > i: continue
        if i >= p * PERPAGE: break
        scrapedplot = ""
        scrapedthumbnail = ""
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedtitle = scrapedtitle.replace("streaming", "")
        scrapedurl = scrapedurl + "/episodi/"
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

    # Per page
    if len(matches) >= p * PERPAGE:
        scrapedurl = item.url + '{}' + str(p + 1)
        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="elenco",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png",
                 folder=True))

    return itemlist


def lista_serie(item):
    logger.info("Stefano.channels.solostreaming lista_serie")
    itemlist = []

    p = 1
    if '{}' in item.url:
        item.url, p = item.url.split('{}')
        p = int(p)

    data = httptools.downloadpage(item.url).data

    patron = '<div class="update"[^>]+>\s*<a class="post-data" title="(.*?)" data="(.*?)" href="([^"]+)">'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for i, (scrapedtitle_1, scrapedtitle_2, scrapedurl) in enumerate(matches):
        if (p - 1) * PERPAGE > i: continue
        if i >= p * PERPAGE: break
        scrapedplot = ""
        scrapedthumbnail = ""
        scrapedurl = scrapedurl + "/episodi/"
        scrapedtitle = scrapedtitle_1
        scrapedtitle_2 = scrapedtitle_2.replace("  ", " ")
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios_new",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]" + " " + scrapedtitle_2,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='tv'))

    # Per page
    if len(matches) >= p * PERPAGE:
        scrapedurl = item.url + '{}' + str(p + 1)
        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="lista_serie",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png",
                 folder=True))

    return itemlist


def episodios(item):
    logger.info("Stefano.channels.solostreaming episodios")

    itemlist = []

    data = httptools.downloadpage(item.url).data

    patron = r'<span class="stagione-icon su-spoiler-icon"></span>([^<]+?)</div>(.*?)<br>\s*</div>\s*</div>\s*<br>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for season, data in matches:
        subs = ' [SUB ITA]' if 'SUB' in season else ' [ITA]'
        for epi in data.split('<br>'):
            title = re.compile('title="([^"]+?)" h', re.DOTALL).findall(epi)[0]
            title += subs
            itemlist.append(
                Item(channel=__channel__,
                     action="findvideos",
                     contentType="episode",
                     title=title,
                     url=item.url,
                     extra=epi,
                     fulltitle=title + ' - ' + item.show,
                     show=item.show,
                     thumbnail=item.thumbnail))

    if config.get_library_support() and len(itemlist) != 0:
        itemlist.append(
            Item(channel=__channel__,
                 title="Aggiungi alla libreria",
                 url=item.url,
                 action="add_serie_to_library",
                 extra="episodios",
                 show=item.show))

    return itemlist


def episodios_new(item):
    logger.info("Stefano.channels.solostreaming episodios")

    itemlist = []

    data = httptools.downloadpage(item.url).data

    patron = r'<span class="stagione-icon su-spoiler-icon"></span>([^<]+?)</div>(.*?)<br>\s*</div>\s*</div>\s*<br>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for season, data in matches:
        subs = ' [SUB ITA]' if 'SUB' in season else ' [ITA]'
        for epi in data.split('<br>'):
            title = re.compile('title="([^"]+?)" h', re.DOTALL).findall(epi)[0]
            title += subs
            itemlist.append(
                Item(channel=__channel__,
                     action="findvideos",
                     contentType="episode",
                     title=title,
                     url=item.url,
                     extra=epi,
                     fulltitle=title + ' - ' + item.show,
                     show=item.show,
                     thumbnail=item.thumbnail))

    return list(reversed(itemlist))


def findvideos(item):
    logger.info("Stefano.channels.solostreaming findvideos")

    data = item.extra
    links = set()

    for link in re.compile('href="([^"]+?)">', re.DOTALL).findall(data):
        if 'link4.me' not in link: continue
        links.add(link4me.get_long_url(link, item.url))

    itemlist = servertools.find_video_items(data=str(links) + data)
    for videoitem in itemlist:
        videoitem.title = item.title + videoitem.title
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.show = item.show
        videoitem.plot = item.plot
        videoitem.channel = __channel__

    return itemlist
