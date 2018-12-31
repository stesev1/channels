# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Thegroove360 - XBMC Plugin
# Canale  per filmpertutti.co
# # ------------------------------------------------------------

import re
import urlparse

from core import config, httptools
from platformcode import logger
from core import scrapertools
from core import servertools
from core.item import Item
from core.tmdb import infoSod
from lib.unshortenit import unshorten

__channel__ = "filmpertutti"
__category__ = "F,S,A"
__type__ = "generic"
__title__ = "filmpertutti"
__language__ = "IT"

host = "https://www.filmpertutti.uno"


def mainlist(item):
    logger.info("[thegroove360.filmpertutti] mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Ultimi film inseriti[/COLOR]",
                     action="peliculas",
                     extra="movie",
                     url="%s/category/film/" % host,
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Categorie film[/COLOR]",
                     action="categorias",
                     url="%s/category/film/" % host,
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca...[/COLOR]",
                     action="search",
                     extra="movie",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV[/COLOR]",
                     extra="serie",
                     action="peliculas_tv",
                     url="%s/category/serie-tv/" % host,
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca Serie TV...[/COLOR]",
                     action="search",
                     extra="serie",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search")]

    return itemlist


def newest(categoria):
    logger.info("[thegroove360.filmpertutti] newest" + categoria)
    itemlist = []
    item = Item()
    try:
        if categoria == "peliculas":
            item.url = host + "/category/film/"
            item.action = "peliculas"
            item.extra = "movie"
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


def peliculas(item):
    logger.info("[thegroove360.filmpertutti] peliculas")
    itemlist = []

    # Carica la pagina
    data = httptools.downloadpage(item.url).data

    # Estrae i contenuti
    patron = '<li><a href="([^"]+)" data-thumbnail="([^"]+)"><div>\s*<div class="title">(.*?)<.*?IMDb">([^<]+)'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle, scraprate in matches:
        scrapedplot = ""
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 contentType="movie",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR] - IMDb: " + scraprate,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 extra=item.extra,
                 folder=True), tipo='movie'))

    # Paginazione
    patronvideos = '<a href="([^"]+)"[^>]+>Pagina'
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
                 extra=item.extra,
                 folder=True))

    return itemlist


def peliculas_tv(item):
    logger.info("[thegroove360.filmpertutti] peliculas")
    itemlist = []

    # Carica la pagina
    data = httptools.downloadpage(item.url).data

    # Estrae i contenuti
    patron = '<li><a href="([^"]+)" data-thumbnail="([^"]+)"><div>\s*<div class="title">(.*?)<'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        title = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedplot = ""
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 fulltitle=title,
                 show=title,
                 title="[COLOR azure]" + title + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 extra=item.extra,
                 folder=True), tipo='tv'))

    # Paginazione
    patronvideos = '<a href="([^"]+)"[^>]+>Pagina'
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
                 extra=item.extra,
                 folder=True))

    return itemlist


def HomePage(item):
    import xbmc
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.Stefano)")


def categorias(item):
    logger.info("[thegroove360.filmpertutti] categorias")
    itemlist = []

    data = httptools.downloadpage(item.url).data

    # Narrow search by selecting only the combo
    patron = '<option>Scegli per Genere</option>(.*?)</select'
    bloque = scrapertools.get_match(data, patron)

    # The categories are the options for the combo
    patron = '<option data-src="([^"]+)">([^<]+)</option>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        scrapedurl = urlparse.urljoin(item.url, scrapedurl)
        scrapedthumbnail = ""
        scrapedplot = ""
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 extra=item.extra,
                 plot=scrapedplot))

    return itemlist


def search(item, texto):
    logger.info("[thegroove360.filmpertutti] " + item.url + " search " + texto)
    item.url = host + "/?s=" + texto
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


def episodios(item):
    def load_episodios(html, item, itemlist, lang_title):
        patron = '.*?<a[^h]+href="[^"]+"[^>]+>[^<]+<\/a>(?:<br \/>|<\/p>|-)'
        matches = re.compile(patron).findall(html)
        for data in matches:
            # Estrae i contenuti
            scrapedtitle = data.split('<a ')[0]
            scrapedtitle = re.sub(r'<[^>]*>', '', scrapedtitle).strip()
            if scrapedtitle != 'Categorie':
                scrapedtitle = scrapedtitle.replace('&#215;', 'x')
                itemlist.append(
                    Item(channel=__channel__,
                         action="findvideos",
                         contentType="episode",
                         title="[COLOR azure]%s[/COLOR]" % (scrapedtitle + " (" + lang_title + ")"),
                         url=data,
                         thumbnail=item.thumbnail,
                         extra=item.extra,
                         fulltitle=scrapedtitle + " (" + lang_title + ")" + ' - ' + item.show,
                         show=item.show))

    logger.info("[filmpertutti.py] episodios")

    itemlist = []

    # Carica la pagina
    data = httptools.downloadpage(item.url).data
    data = scrapertools.decodeHtmlentities(data)

    lang_titles = []
    starts = []
    patron = r"Stagione.*?ITA"
    matches = re.compile(patron, re.IGNORECASE).finditer(data)
    for match in matches:
        season_title = match.group()
        if season_title != '':
            lang_titles.append('SUB ITA' if 'SUB' in season_title.upper() else 'ITA')
            starts.append(match.end())

    i = 1
    len_lang_titles = len(lang_titles)

    while i <= len_lang_titles:
        inizio = starts[i - 1]
        fine = starts[i] if i < len_lang_titles else -1

        html = data[inizio:fine]
        lang_title = lang_titles[i - 1]

        load_episodios(html, item, itemlist, lang_title)

        i += 1

    if config.get_library_support() and len(itemlist) != 0:
        itemlist.append(
            Item(channel=__channel__,
                 title="Aggiungi alla libreria",
                 url=item.url,
                 action="add_serie_to_library",
                 extra="episodios" + "###" + item.extra,
                 show=item.show))

    return itemlist


def findvideos(item):
    def add_myitem(sitemlist,scontentType,stitle,surl):
        sitemlist.append(
            Item(channel=__channel__,
                 action="play",
                 contentType=scontentType,
                 title=stitle,
                 fulltitle=item.fulltitle,
                 server=stitle,
                 url=surl,
                 thumbnail=item.thumbnail,
                 extra=item.extra))

    logger.info("[thegroove360.filmpertutti] findvideos")
    itemlist=[]
    logger.debug(item)

    # Carica la pagina
    if item.extra == 'serie':
        patron = '<a\s*href="(.*?)\s*".*?[^>]+>([^<]+)<\/a>'
        matches = re.compile(patron).findall(item.url)

        for lurl,lsrv in matches:

            if lsrv == 'HD': lsrv = lsrvo + ' HD'
            lsrvo=lsrv

            add_myitem(itemlist,"episodios","[COLOR azure]%s[/COLOR]" % lsrv,lurl)
    else:
        # Carica la pagina
        data = httptools.downloadpage(item.url).data
        patron='<strong>\s*(Versione.*?)<p><strong>Download'
        data = re.compile(patron,re.DOTALL).findall(data)

        if data:
            vqual = re.compile('ersione:.*?>\s*(.*?)<').findall(data[0])
            sect=re.compile('Streaming',re.DOTALL).split(data[0])

            ## SD links
            links=re.compile('<a\s*href="([^",\s]+).*?>([^<]+)',re.DOTALL).findall(sect[1])
            for link,srv in links:
                uri, status = unshorten(link)
                if status == 200:
                    add_myitem(itemlist,"movie","[COLOR azure]%s (SD)[/COLOR] - %s" % (srv,vqual[0]),link)

            ## HD Links
            if len(sect) > 2:
                links=re.compile('<a\s*href="([^",\s]+).*?>([^<]+)',re.DOTALL).findall(sect[2])

                for link,srv in links:
                    uri, status = unshorten(link)
                    if status == 200:
                        add_myitem(itemlist,"movie","[COLOR azure]%s (HD)[/COLOR] - %s" % (srv,vqual[0]),link)
        else:
            itemlist = servertools.find_video_items(item=item)

    for item in itemlist:
        logger.info(item)

    return itemlist

def play(item):
    logger.info("[thegroove360.filmpertutti] play: %s" % item.url)

    if 'vcrypt' in item.url:
        idata = httptools.downloadpage(item.url).data
        patron = r"document.cookie\s=\s.*?'(.*?);\s(.*?);\s(.*?)'\s.*\s.*?URL=([^\"]+)"
        matches = re.compile(patron, re.IGNORECASE).findall(idata)

        for cookie1, cookie2, cookie3, dest in matches:
            import requests
            c1, v1 = cookie1.split('=')
            c2, v2 = cookie2.split('=')
            c3, v3 = cookie3.split('=')

            mcookie = {c1: v1, c2: v2, c3: v3}

            r = requests.post(dest, cookies=mcookie)

            desturl = r.url.replace("/out/", "/outlink/")
            import os
            par = os.path.basename(desturl)

            rdata = requests.post(desturl, data={'url': par})

            if "wstream" in rdata.url:
                item.url = rdata.url.replace("/video/", "/")
            else:
                item.url = rdata.url


    itemlist = servertools.find_video_items(data=item.url)

    for videoitem in itemlist:
        servername = re.sub(r'[-\[\]\s]+', '', videoitem.title)
        videoitem.title = "".join(
            ['[COLOR azure][[COLOR orange]' + servername.capitalize() + '[/COLOR]] - ', item.show])
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__

    return itemlist
