# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# TheGroove360 - XBMC Plugin
# Canale cinemalibero
# ------------------------------------------------------------

import re
import urlparse

from core import config, httptools
from platformcode import logger
from core import scrapertools
from core import servertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "cinemalibero"
host = "https://www.cinemalibero.news/"
headers = [['Referer', host]]


def mainlist(item):
    logger.info("[thegroove360.cinemalibero] mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Film [COLOR orange]- Novita'[/COLOR]",
                     extra="movie",
                     action="peliculas_work",
                     url="%s/category/film/" % host,
                     thumbnail="ttps://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/popcorn_cinema_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film [COLOR orange]- Categorie[/COLOR]",
                     extra="movie",
                     action="categorias",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/popcorn_serie_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film [COLOR orange]- Animazione[/COLOR]",
                     extra="movie",
                     action="peliculas_work",
                     url="%s/category/film-in-streaming/animazione/" % host,
                     thumbnail="ttps://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/anime_P.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca Film...[/COLOR]",
                     action="search",
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/search_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV [COLOR orange]- Novita'[/COLOR]",
                     extra="serie",
                     action="peliculas_work",
                     url="%s/category/serie-tv/" % host,
                     thumbnail="ttps://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/tv_serie_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV [COLOR orange]- Ultime Aggiornate[/COLOR]",
                     extra="serie",
                     action="peliculas_work",
                     url="%s/aggiornamenti-serie-tv/" % host,
                     thumbnail="ttps://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/tv_serie_P.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca Serie TV...[/COLOR]",
                     action="search",
                     extra="serie",
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/search_P.png")]

    return itemlist


# ==================================================================================================================================================

def categorias(item):
    itemlist = []

    # Carica la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Estrae i contenuti
    #patron = '<li><small>[^>]+><a href="(.*?)">(.*?)</a></li>'
    patron = r'<a class="dropdown-item" href="(.*?)".*?">(.*?)<'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        if scrapedtitle.startswith(("Anime Giapponesi")):
            continue
        if scrapedtitle.startswith(("Serie TV")):
            continue
        scrapedplot = ""
        scrapedthumbnail = ""
        scrapedurl = host + scrapedurl
        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="peliculas_work",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/popcorn_serie_P.png",
                 folder=True))

    return itemlist


# ==================================================================================================================================================

def search(item, texto):
    logger.info("[thegroove360.cinemalibero] " + item.url + " search " + texto)
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


# ==================================================================================================================================================

def peliculas(item):
    logger.info("[thegroove360.cinemalibero] peliculas")
    itemlist = []

    # Carica la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Estrae i contenuti
    #patron = '<a href="([^"]+)" class="locandina"[^>]+>\s*<div class="voto">[^=]+=[^>]+>(.*?)<'
    patron = '<a href="([^"]+)" title="[^"]+" alt="[^"]+" class="locandina"\s*'
    patron += 'style[^h]+([^\)]+)[^>]+>(?:<div class="voto">([^<]+)|)[^=]+="titolo">([^<]+)<'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, voto, scrapedtitle in matches:
        scrapedplot = ""
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedtitle = scrapedtitle.replace("[", "(").replace("]", ")")
        if voto:
            voto = " ([COLOR yellow]" + voto + "[/COLOR])"
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="findvideos" if not "serie" in scrapedurl else "episodios",
                 contentType="movie",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]" + voto,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='movie' if not "serie" in scrapedurl else "tv"))

    # Paginazione
    patronvideos = '<a class="next page-numbers" href="(.*?)">'
    # patronvideos = '<link rel=\'next\' href=\'(.*?)\' />'
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
                 extra=item.extra,
                 action="peliculas",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/next_1.png",
                 folder=True))

    return itemlist


# ==================================================================================================================================================

def peliculas_tv(item):
    logger.info("[thegroove360.cinemalibero] peliculas_tv")
    itemlist = []

    # Carica la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Estrae i contenuti
    patron = '<a href="([^"]+)" class="locandina"[^>]+>\s*<div class="voto">[^=]+=[^>]+>(.*?)<'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        scrapedplot = ""
        scrapedthumbnail = ""
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="seasons",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='tv'))

    # Paginazione
    patronvideos = '<a class="next page-numbers" href="(.*?)">'
    # patronvideos = '<link rel=\'next\' href=\'(.*?)\' />'
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
                 extra=item.extra,
                 action="peliculas_tv",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/next_1.png",
                 folder=True))

    return itemlist


def seasons(item):
    logger.info("[thegroove360.cinemalibero] seasons")

    itemlist = []
    data = httptools.downloadpage(item.url, headers=headers).data

    patron = r'<p><strong>(.*?)</strong></p>'
    matches = re.compile(patron, re.MULTILINE).findall(data)

    for scrapedtitle in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="episodios",
                 title="[COLOR azure]%s[/COLOR]" % scrapedtitle,
                 url=item.url,
                 thumbnail=item.thumbnail,
                 extra=item.extra,
                 fulltitle=scrapedtitle,
                 show=item.show))

    return itemlist


# ==================================================================================================================================================
def episodios(item):
    logger.info("[thegroove360.cinemalibero] episodios")

    itemlist = []

    # Download pagina
    data = httptools.downloadpage(item.url, headers=headers).data
    # data = scrapertools.decodeHtmlentities(data)
    # data = scrapertools.get_match(data, '<section id="content">(.*?)<div class="wprc-form">')

    patron = r'</strong></p>(.*?)</a></p>'
    blocco = re.compile(patron, re.IGNORECASE).findall(data)[0]

    patron = r'<p>(.*?)<a|</a><br />(.*?)<a'

    matches = re.compile(patron, re.IGNORECASE).finditer(blocco)
    for match in matches:

        scrapedtitle = match.group(1) if match.group(1) is not None else match.group(2)

        lang_title = ""

        #patron = scrapedtitle.replace("(", "\(").replace(")", "\)") + '(<a href.*?</a>)<br />'
        patron = '(<a href.*?</a>)<br />'

        if scrapedtitle.startswith("Stagione Completa"): break

        itemdata = re.compile(patron, re.IGNORECASE).findall(data)[0]

        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 contentType="episode",
                 title="[COLOR azure]%s[/COLOR]" % (scrapedtitle + " (" + lang_title + ")"),
                 url=itemdata,
                 thumbnail=item.thumbnail,
                 extra=item.extra,
                 fulltitle=scrapedtitle + " (" + lang_title + ")" + ' - ' + item.show,
                 show=item.show))

    if config.get_library_support() and len(itemlist) != 0:
        itemlist.append(
            Item(channel=__channel__,
                 title="Aggiungi alla libreria",
                 url=item.url,
                 action="add_serie_to_library",
                 extra="episodios" + "###" + item.extra,
                 show=item.show))

    return itemlist


# def episodios(item):
#     def load_episodios(html, item, itemlist, lang_title):
#         patron = '.*?<a[^h]+href="[^"]+"[^>]+>[^<]+<\/a>(?:<br \/>|<\/p>)'
#         matches = re.compile(patron).findall(html)
#         for data in matches:
#             # Estrazione
#             scrapedtitle = data.split('-<a ')[0]
#             scrapedtitle = re.sub(r'<[^>]*>', '', scrapedtitle).strip()
#             if scrapedtitle != 'Categorie':
#                 scrapedtitle = scrapedtitle.replace('&#215;', 'x')
#                 scrapedtitle = scrapedtitle.replace('&#215;', 'x')
#                 itemlist.append(
#                     Item(channel=__channel__,
#                          action="findvideos",
#                          contentType="episode",
#                          title="[COLOR azure]%s[/COLOR]" % (scrapedtitle + " (" + lang_title + ")"),
#                          url=data,
#                          thumbnail=item.thumbnail,
#                          extra=item.extra,
#                          fulltitle=scrapedtitle + " (" + lang_title + ")" + ' - ' + item.show,
#                          show=item.show))
#
#     logger.info("[thegroove360.cinemalibero] episodios")
#
#     itemlist = []
#
#     # Download pagina
#     data = httptools.downloadpage(item.url, headers=headers).data
#     data = scrapertools.decodeHtmlentities(data)
#     data = scrapertools.get_match(data, '<section id="content">(.*?)<div class="wprc-form">')
#
#     lang_titles = []
#     starts = []
#     patron = r"Stagione.*?iTA"
#     matches = re.compile(patron, re.IGNORECASE).finditer(data)
#     for match in matches:
#         season_title = match.group()
#         if season_title != '':
#             lang_titles.append('SUB ITA' if 'SUB' in season_title.upper() else 'ITA')
#             starts.append(match.end())
#
#     i = 1
#     len_lang_titles = len(lang_titles)
#
#     while i <= len_lang_titles:
#         inizio = starts[i - 1]
#         fine = starts[i] if i < len_lang_titles else -1
#
#         html = data[inizio:fine]
#         lang_title = lang_titles[i - 1]
#
#         load_episodios(html, item, itemlist, lang_title)
#
#         i += 1
#
#     if config.get_library_support() and len(itemlist) != 0:
#         itemlist.append(
#             Item(channel=__channel__,
#                  title="Aggiungi alla libreria",
#                  url=item.url,
#                  action="add_serie_to_library",
#                  extra="episodios" + "###" + item.extra,
#                  show=item.show))
#
#     return itemlist


def findvideos(item):
    logger.info("[thegroove360.cinemalibero] findvideos")

    data = item.url if item.extra == "serie" else httptools.downloadpage(item.url, headers=headers).data

    itemlist = servertools.find_video_items(data=data)
    for videoitem in itemlist:
        videoitem.title = item.title + videoitem.title
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.show = item.show
        videoitem.plot = item.plot
        videoitem.channel = __channel__

    return itemlist


def HomePage(item):
    import xbmc
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.streamondemand)")


def peliculas_work(item):
    logger.info("[[thegroove360.cinemalibero] peliculas_work")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = '<a href="([^"]+)" title="[^"]+" alt="[^"]+" class="locandina"\s*'
    patron += 'style[^h]+([^\)]+)[^>]+>(?:<div class="voto">([^<]+)|)[^=]+="titolo">([^<]+)<'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, voto, scrapedtitle in matches:
        scrapedplot = ""
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedtitle = scrapedtitle.replace("[", "(").replace("]", ")")
        if voto:
            voto = " ([COLOR yellow]" + voto + "[/COLOR])"
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="findvideos" if not "serie" in scrapedurl else "episodios",
                 contentType="movie",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]" + voto,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='movie' if not "serie" in scrapedurl else "tv"))

    # Extrae el paginador
    patronvideos = '<a class="next page-numbers" href="(.*?)">'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="peliculas",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="ttps://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/next_1.png",
                 folder=True))

    return itemlist
