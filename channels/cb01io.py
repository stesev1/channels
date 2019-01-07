# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Thegroove360 - XBMC Plugin
# Canale cineblog01_video
# ------------------------------------------------------------

import base64
import re
import urlparse

from core import httptools
from core import config
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "cb01io"
host = "https://cb01.video"
headers = [['Referer', host]]


def mainlist(item):
    logger.info("[thegroove360.cb01io] mainlist")
    itemlist = [
        Item(channel=__channel__,
             title="[COLOR azure]Film[COLOR orange] - Novita'[/COLOR]",
             action="peliculas",
             url=host,
             extra="movie",
             thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/popcorn_cinema_P.png"),
        Item(channel=__channel__,
             title="[COLOR azure]Film[COLOR orange] - Cetogorie[/COLOR]",
             action="menu_movie",
             url=host,
             extra="movie",
             thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/genres_P.png"),
        Item(channel=__channel__,
             title="[COLOR azure]Film[COLOR orange] - HD[/COLOR]",
             action="peliculas",
             url=host + "/?s=%5BHD%5D",
             extra="movie",
             thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/movie_new_P.png"),
        Item(channel=__channel__,
             action="peliculas_serie",
             title="[COLOR azure]Serie Tv[COLOR orange] - Novita'[/COLOR]",
             url="%s/category/serie-tv/" % host,
             extra="serie",
             thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/tv_serie_P.png"),
        Item(channel=__channel__,
             action="peliculas_update",
             title="[COLOR azure]Serie Tv[COLOR orange] - Aggiornamenti[/COLOR]",
             url="%s/aggiornamenti-serie-tv/" % host,
             extra="serie",
             thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/new_tvshows_P.png"),
        Item(channel=__channel__,
             title="[COLOR azure]Serie TV[COLOR orange] - Lista A-Z[/COLOR]",
             action="series_az",
             url=host,
             extra="serie",
             thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/a-z_P.png"),
        Item(channel=__channel__,
             action="menu_search",
             title="[COLOR yellow]Cerca ...[/COLOR]",
             extra="serie",
             thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/search_P.png")]

    return itemlist


# ==================================================================================================================================================

def menu_movie(item):
    logger.info("[thegroove360.cb01io] menu_movie")

    # Main options
    itemlist = [
        Item(channel=__channel__,
             action="menugeneros",
             title="[COLOR azure]Film[COLOR orange] - Per Genere[/COLOR]",
             url=host,
             extra="movie",
             thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/genres_P.png"),
        Item(channel=__channel__,
             action="menuanyos",
             title="[COLOR azure]Film[COLOR orange] - Per Anno[/COLOR]",
             url=host,
             extra="movie",
             thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/movie_year_P.png"),
        Item(channel=__channel__,
             action="search",
             title="[COLOR yellow]Cerca Film ...[/COLOR]",
             extra="movie",
             thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/search_P.png")]

    return itemlist


# ==================================================================================================================================================

def menugeneros(item):
    logger.info("[thegroove360.cb01io] menugeneros")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data

    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data, '<select name="select1"(.*?)</select>')

    # The categories are the options for the combo
    patron = '<option\s*value="([^"]+)"\s*>([^<]+)<\/option>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for url, titulo in matches:
        scrapedtitle = titulo
        scrapedurl = urlparse.urljoin(item.url, url)
        scrapedthumbnail = ""
        scrapedplot = ""

        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/genre_P.png",
                 extra=item.extra,
                 plot=scrapedplot))

    return itemlist


# ==================================================================================================================================================

def menuanyos(item):
    logger.info("[thegroove360.cb01io] menuanyos")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data

    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data, '<option value="-1">Film per Anno</option>(.*?)</select>')

    # The categories are the options for the combo
    patron = '<option value="([^"]+)"\s*>([^<]+)</option>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for url, titulo in matches:
        scrapedtitle = titulo
        scrapedurl = urlparse.urljoin(item.url, url)
        scrapedthumbnail = ""
        scrapedplot = ""

        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/movie_year_P.png",
                 extra=item.extra,
                 plot=scrapedplot))
    itemlist.reverse()
    return itemlist


# ==================================================================================================================================================

def peliculas(item):
    logger.info("[thegroove360.cb01io] peliculas")
    itemlist = []

    # Descarga la página
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patronvideos = '<div class="span4">\s*<a href="[^"]+">\s*(?:<p><img src="([^"]+)[^>]+></p>|).*?'
    patronvideos += '<div class="span8">\s*<a href="([^"]+)">\s*<h1>([^<]+)<\/h1>'
    patronvideos += '.*?</strong>\s*<br>\s*(?:<p[^>]+>|)(.*?)<'
    matches = re.compile(patronvideos, re.DOTALL).finditer(data)

    for match in matches:
        scrapedplot = scrapertools.unescape(match.group(4))
        scrapedtitle = scrapertools.unescape(match.group(3))
        scrapedurl = urlparse.urljoin(item.url, match.group(2))
        scrapedthumbnail = urlparse.urljoin(item.url, match.group(1))
        scrapedthumbnail = scrapedthumbnail.replace(" ", "%20")
        # scrapedplot = "" #scrapertools.unescape("[COLOR orange]" + match.group(4) + "[/COLOR]\n" + match.group(5).strip())
        # scrapedplot = "" #scrapertools.htmlclean(scrapedplot).strip()
        scrapedtitle = scrapedtitle.replace("&#8211;", "-").replace("&#215;", "x").replace("[Sub-ITA]", "(Sub Ita)")
        scrapedtitle = scrapedtitle.replace("/", " - ").replace("&#8217;", "'").replace("&#8230;", "...").replace("ò",
                                                                                                                  "o")
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)
        if "serie" in match.group(2):
            type = "tv"
        else:
            type = "movie"
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvid" if not "tv" in type else "season_serietv",
                 contentType="movie",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 extra=item.extra,
                 folder=True), tipo='movie' if not "tv" in type else "tv"))
    # Paginación
    next_page = scrapertools.find_single_match(data, '<a class="nextpostslink" rel="next" href="([^"]+)">&raquo;</a>')
    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=next_page,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/next_1.png"))

    return itemlist


# ==================================================================================================================================================


def menu_search(item):
    logger.info("[thegroove360.cb01io] menu_search")
    itemlist = [Item(channel=__channel__,
                     action="search",
                     title="[COLOR yellow]Cerca Film ...[/COLOR]",
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/search_P.png"),
                Item(channel=__channel__,
                     action="search",
                     title="[COLOR yellow]Cerca Serie Tv ...[/COLOR]",
                     extra="serie",
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/search_P.png")]

    return itemlist


# ==================================================================================================================================================

# Al llamarse "search" la función, el launcher pide un texto a buscar y lo añade como parámetro
def search(item, texto):
    logger.info("[cb01_video] " + item.url + " search " + texto)

    try:

        if item.extra == "movie":
            item.url = host + "/?s=" + texto
            return peliculas_searchmovie(item)
        if item.extra == "serie":
            item.url = host + "/?s=" + texto
            return peliculas_searchtv(item)

    # Continua la ricerca in caso di errore
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


# ==================================================================================================================================================

def peliculas_searchtv(item):
    logger.info("[thegroove360.cb01io] peliculas")
    itemlist = []

    # Descarga la página
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patronvideos = '<div class="span4">\s*<a href="[^"]+">\s*(?:<p><img src="([^"]+)[^>]+><\/p>|)'
    patronvideos += '.*?<div class="span8">\s*<a href="([^"]+)">\s*<h1>([^<]+)<\/h1>'
    # patronvideos += '</div>\s*</div>\s*<div class="span8">'
    matches = re.compile(patronvideos, re.DOTALL).finditer(data)

    for match in matches:
        scrapedtitle = scrapertools.unescape(match.group(3))
        scrapedurl = urlparse.urljoin(item.url, match.group(2))
        scrapedthumbnail = urlparse.urljoin(item.url, match.group(1))
        scrapedthumbnail = scrapedthumbnail.replace(" ", "%20")
        # scrapedplot = "" #scrapertools.unescape("[COLOR orange]" + match.group(4) + "[/COLOR]\n" + match.group(5).strip())
        scrapedplot = ""  # scrapertools.htmlclean(scrapedplot).strip()
        scrapedtitle = scrapedtitle.replace("&#8211;", "-").replace("&#215;", "x").replace("[Sub-ITA]", "(Sub Ita)")
        scrapedtitle = scrapedtitle.replace("/", " - ").replace("&#8217;", "'").replace("&#8230;", "...").replace("ò",
                                                                                                                  "o")
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)
        if not "serie" in match.group(2):
            continue
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="season_serietv",
                 contentType="tvshow",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 extra=item.extra,
                 folder=True), tipo='tv'))

    return itemlist


# ==================================================================================================================================================

def peliculas_searchmovie(item):
    logger.info("[thegroove360.cb01io] peliculas")
    itemlist = []

    # Descarga la página
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patronvideos = '<div class="span4">\s*<a href="[^"]+">\s*(?:<p><img src="([^"]+)[^>]+></p>|).*?'
    patronvideos += '<div class="span8">\s*<a href="([^"]+)">\s*<h1>([^<]+)<\/h1>'
    # patronvideos += '</div>\s*</div>\s*<div class="span8">'
    matches = re.compile(patronvideos, re.DOTALL).finditer(data)

    for match in matches:
        scrapedtitle = scrapertools.unescape(match.group(3))
        scrapedurl = urlparse.urljoin(item.url, match.group(2))
        scrapedthumbnail = urlparse.urljoin(item.url, match.group(1))
        scrapedthumbnail = scrapedthumbnail.replace(" ", "%20")
        # scrapedplot = "" #scrapertools.unescape("[COLOR orange]" + match.group(4) + "[/COLOR]\n" + match.group(5).strip())
        scrapedplot = ""  # scrapertools.htmlclean(scrapedplot).strip()
        scrapedtitle = scrapedtitle.replace("&#8211;", "-").replace("&#215;", "x").replace("[Sub-ITA]", "(Sub Ita)")
        scrapedtitle = scrapedtitle.replace("/", " - ").replace("&#8217;", "'").replace("&#8230;", "...").replace("ò",
                                                                                                                  "o")
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)
        if "serie" in match.group(2):
            continue
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvid",
                 contentType="movie",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 extra=item.extra,
                 folder=True), tipo='movie'))

    return itemlist


# ==================================================================================================================================================

def series_az(item):
    logger.info("[thegroove360.cb01io] serie_categorias")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data

    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data, 'Serie TV A-Z</option>(.*?)</select>')

    # The categories are the options for the combo
    patron = '<option value="([^"]+)"\s*>([^<]+)<\/option>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for url, titulo in matches:
        scrapedtitle = titulo
        scrapedurl = urlparse.urljoin(item.url, url)
        scrapedthumbnail = ""
        scrapedplot = ""
        if "Lista Completa" in scrapedtitle:
            continue
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_serie",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/a-z_P.png",
                 extra=item.extra,
                 plot=scrapedplot))

    return itemlist


# ==================================================================================================================================================

def peliculas_serie(item):
    logger.info("[thegroove360.cb01io] peliculas_serie")
    itemlist = []

    # Descarga la página
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patronvideos = '<div class="span4">\s*<a href="[^"]+">\s*(?:<p><img src="([^"]+)[^>]+><\/p>|)'
    patronvideos += '.*?<div class="span8">\s*<a href="([^"]+)">\s*<h1>([^<]+)<\/h1>'
    patronvideos += '.*?<p[^>]+>(.*?)<'
    matches = re.compile(patronvideos, re.DOTALL).finditer(data)

    for match in matches:
        scrapedplot = scrapertools.unescape(match.group(4))
        scrapedtitle = scrapertools.unescape(match.group(3))
        scrapedurl = urlparse.urljoin(item.url, match.group(2))
        scrapedthumbnail = urlparse.urljoin(item.url, match.group(1))
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle).strip()
        scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)
        if "film" in match.group(1):
            type = "movie"
        else:
            type = "tv"
        itemlist.append(
            Item(channel=__channel__,
                 action="season_serietv",
                 contentType="tvshow",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 extra=item.extra,
                 folder=True))
    # Paginación
    next_page = scrapertools.find_single_match(data, '<a class="nextpostslink" rel="next" href="([^"]+)">&raquo;</a>')
    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_serie",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=next_page,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/next_1.png"))

    return itemlist


# ==================================================================================================================================================

def peliculas_update(item):
    logger.info("[thegroove360.cb01io] peliculas_update")
    itemlist = []
    numpage = 14

    p = 1
    if '{}' in item.url:
        item.url, p = item.url.split('{}')
        p = int(p)

    # Descarga la pagina

    data = httptools.downloadpage(item.url, headers=headers).data

    # Estrae i contenuti
    patron = '<li><a href="([^"]+)"\s*><div style="background[^(]+\((.*?)\)">\s*<div class[^>]+>([^<]+)<\/div>[^=]+=[^>]+>([^<]+)<'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for i, (scrapedurl, scrapedthumbnail, scrapedtitle, ep) in enumerate(matches):
        if (p - 1) * numpage > i: continue
        if i >= p * numpage: break
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle).replace("Privato: ", "")
        scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)
        scrapedplot = ""
        ep = ep.replace("||", "").replace("/", " - ").strip()
        ep = "  ([COLOR orange]" + ep + "[/COLOR])"
        title = scrapedtitle.strip()  # .title()
        # title = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="season_serietv",
                 contentType="tv",
                 title=title + ep,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail.strip(),
                 fulltitle=title,
                 show=title,
                 plot=scrapedplot,
                 folder=True), tipo='tv'))

    # Extrae el paginador
    if len(matches) >= p * numpage:
        scrapedurl = item.url + '{}' + str(p + 1)
        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="peliculas_update",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/next_1.png",
                 folder=True))

    return itemlist


# ==================================================================================================================================================

def season_serietv(item):
    def load_season_serietv(html, item, itemlist, season_title):
        if len(html) > 0 and len(season_title) > 0:
            itemlist.append(
                Item(channel=__channel__,
                     action="episodios",
                     title="[COLOR azure]%s[/COLOR]" % season_title,
                     contentType="episode",
                     fulltitle=item.fulltitle,
                     url=html,
                     extra='serie',
                     plot="[COLOR orange]" + item.fulltitle + "[/COLOR]  " + item.plot,
                     thumbnail=item.thumbnail,
                     show=item.show))

    itemlist = []

    # Descarga la página
    data = httptools.downloadpage(item.url, headers=headers).data
    data = scrapertools.decodeHtmlentities(data)
    data = scrapertools.get_match(data, '<div class="post_content">(.*?)<div class="clearfix"></div>')

    blkseparator = chr(32) + chr(226) + chr(128) + chr(147) + chr(32)
    data = data.replace(blkseparator, ' - ')

    starts = []
    season_titles = []
    patron = 'strong>(?:<span style[^>]+>|)([^<]+tagione[^<]+).*?<\/strong>'
    matches = re.compile(patron, re.MULTILINE | re.IGNORECASE).finditer(data)
    for match in matches:
        if match.group() != '':
            season_titles.append(match.group(1))

            starts.append(match.end())

    i = 1
    len_season_titles = len(season_titles)

    while i <= len_season_titles:
        inizio = starts[i - 1]
        fine = starts[i] if i < len_season_titles else -1

        html = data[inizio:fine]
        season_title = season_titles[i - 1]

        load_season_serietv(html, item, itemlist, season_title)
        i += 1

    return itemlist


# ==================================================================================================================================================

def episodios(item):
    itemlist = []

    if item.extra == 'serie':
        itemlist.extend(episodios_serie_new(item))

    if config.get_library_support() and len(itemlist) != 0:
        itemlist.append(
            Item(channel=__channel__,
                 title="Aggiungi alla libreria",
                 url=item.url,
                 action="add_serie_to_library",
                 extra="episodios" + "###" + item.extra,
                 show=item.show))

    return itemlist


# ==================================================================================================================================================

def episodios_serie_new(item):
    def load_episodios(html, item, itemlist, lang_title):
        # for data in scrapertools.decodeHtmlentities(html).splitlines():
        # patron = '((?:.*?<a[^h]+href=".*?"[^=]+=[^>]+>.*?<\/a>)+)'
        patron = '((?:.*?<a[^h]+href="[^"]+[^>]+>\s*[^<]+<\/a>)+)'
        matches = re.compile(patron).findall(html)
        for data in matches:
            # Extrae las entradas
            scrapedtitle = data.split('<a ')[0]
            scrapedtitle = re.sub(r'<[^>]*>', '', scrapedtitle).strip()
            if scrapedtitle != 'Categorie':
                scrapedtitle = scrapedtitle.replace('&#215;', 'x')
                if scrapedtitle.find(' - ') > 0:
                    scrapedtitle = scrapedtitle[0:scrapedtitle.find(' - ')]
                itemlist.append(
                    Item(channel=__channel__,
                         action="findvid_serie",
                         contentType="episode",
                         title="[COLOR azure]%s[/COLOR]" % (scrapedtitle + " (" + lang_title + ")"),
                         url=data,
                         thumbnail=item.thumbnail,
                         extra=item.extra,
                         plot=item.plot,
                         fulltitle=item.show + ' - ' + scrapedtitle + " (" + lang_title + ")",
                         show=item.show + ' - ' + scrapedtitle + " (" + lang_title + ")"))

    logger.info("[thegroove360.cb01io] episodios_serie_new")

    itemlist = []

    lang_title = item.title
    if lang_title.upper().find('SUB') > 0:
        lang_title = 'SUB ITA'
    else:
        lang_title = 'ITA'

    html = item.url
    load_episodios(html, item, itemlist, lang_title)

    return itemlist


# ==================================================================================================================================================

def findvideos(item):
    if item.extra == "movie":
        return findvid(item)
    if item.extra == 'serie':
        return findvid_serie(item)
    return []


# ==================================================================================================================================================

def findvid_serie(item):
    def load_vid_series(html, item, itemlist, blktxt):
        if len(blktxt) > 2:
            vtype = blktxt.strip()[:-1] + " - "
        else:
            vtype = ''
        patron = '<a target="_blank"\s*rel="nofollow"\s*href="[^\/]+\/\/[^\/]+\/[^\/]+\/([^"]+)[^>]+>([^<]+)<\/a>'
        # Extrae las entradas
        matches = re.compile(patron, re.DOTALL).finditer(html)
        for match in matches:
            scrapedurl = match.group(1)
            scrapedtitle = match.group(2)
            scrapedurl = scrapedurl.decode("base64")
            title = "[COLOR azure][[COLOR orange]" + vtype + scrapedtitle + "[/COLOR]] " + item.title + "[/COLOR]"
            itemlist.append(
                Item(channel=__channel__,
                     action="play",
                     title=title,
                     url=scrapedurl.strip(),
                     fulltitle=item.fulltitle,
                     show=item.show,
                     thumbnail=item.thumbnail,
                     plot=item.plot,
                     folder=False))

        patron = '<a\s*href="([^"]+)[^>]+>([^<]+)<\/a>'
        # Extrae las entradas
        matches = re.compile(patron, re.DOTALL).finditer(html)
        for match in matches:
            scrapedurl = match.group(1)
            scrapedtitle = match.group(2)
            # scrapedurl=scrapedurl.decode("base64")

            title = "[COLOR azure][[COLOR orange]" + scrapedtitle + "[/COLOR]] " + item.title + "[/COLOR]"
            itemlist.append(
                Item(channel=__channel__,
                     action="play",
                     title=title,
                     url=scrapedurl.strip(),
                     fulltitle=item.fulltitle,
                     show=item.show,
                     thumbnail=item.thumbnail,
                     plot=item.plot,
                     folder=False))

    logger.info("[thegroove360.cb01io] findvid_serie")

    itemlist = []
    lnkblk = []
    lnkblkp = []

    data = item.url

    # First blocks of links
    if data[0:data.find('<a')].find(':') > 0:
        lnkblk.append(data[data.find(' - ') + 3:data[0:data.find('<a')].find(':') + 1])
        lnkblkp.append(data.find(' - ') + 3)
    else:
        lnkblk.append(' ')
        lnkblkp.append(data.find('<a'))

    # Find new blocks of links
    patron = '<a\s[^>]+>[^<]+</a>([^<]+)'
    matches = re.compile(patron, re.DOTALL).finditer(data)
    for match in matches:
        sep = match.group(1)
        if sep != ' - ':
            lnkblk.append(sep)

    i = 0
    if len(lnkblk) > 1:
        for lb in lnkblk[1:]:
            lnkblkp.append(data.find(lb, lnkblkp[i] + len(lnkblk[i])))
            i = i + 1

    for i in range(0, len(lnkblk)):
        if i == len(lnkblk) - 1:
            load_vid_series(data[lnkblkp[i]:], item, itemlist, lnkblk[i])
        else:
            load_vid_series(data[lnkblkp[i]:lnkblkp[i + 1]], item, itemlist, lnkblk[i])

    return itemlist


# =========================================================================================================================================

def findvid(item):
    logger.info("[thegroove360.cb01io] menugeneros")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data
    if not "Streaming:<br />" in data:
        return season_serietv(item)
    else:
        bloque = scrapertools.get_match(data, 'Streaming:<br \/>(.*?)<\/strong><\/p>')

        # Narrow search by selecting only the combo

        # The categories are the options for the combo
        patron = '<a target="_blank"\s*rel="nofollow"\s*href="[^\/]+\/\/[^\/]+\/[^\/]+\/([^"]+)[^>]+>([^<]+)<\/a>'
        matches = re.compile(patron, re.DOTALL).findall(bloque)
        scrapertools.printMatches(matches)

        for scrapedurl, scrapedtitle in matches:
            scrapedurl = scrapedurl.decode("base64")
            scrapedthumbnail = ""
            scrapedplot = ""
            itemlist.append(
                Item(channel=__channel__,
                     action="play",
                     fulltitle=item.fulltitle,
                     show=item.show,
                     title="[[COLOR orange]" + scrapedtitle + "[/COLOR]] - " + item.title,
                     url=scrapedurl.strip(),
                     thumbnail=item.thumbnail,
                     extra=item.extra,
                     plot=item.plot))

        patron = '<a href="([^"]+)[^>]+>([^<]+)</a>'
        matches = re.compile(patron, re.DOTALL).findall(bloque)
        scrapertools.printMatches(matches)

        for scrapedurl, scrapedtitle in matches:
            # scrapedurl=scrapedurl.decode("base64")
            scrapedthumbnail = ""
            scrapedplot = ""
            itemlist.append(
                Item(channel=__channel__,
                     action="play",
                     fulltitle=item.fulltitle,
                     show=item.show,
                     title="[[COLOR orange]" + scrapedtitle + "[/COLOR]] - " + item.title,
                     url=scrapedurl.strip(),
                     thumbnail=item.thumbnail,
                     extra=item.extra,
                     plot=item.plot))
    return itemlist


# =========================================================================================================================================

def play(item):
    itemlist = []

    data = item.url

    if "rapidcrypt" in item.url:
        data = httptools.downloadpage(item.url).data

    while 'nodmca' in item.url:
        item.url = httptools.downloadpage(item.url, only_headers=True, follow_redirects=False).headers.get("location")
        data = item.url

    # logger.debug(data)
    itemlist = servertools.find_video_items(data=data)
    for videoitem in itemlist:
        videoitem.title = item.title
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.plot = item.plot
        videoitem.channel = __channel__

    return itemlist