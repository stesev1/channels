# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Thegroove360 - XBMC Plugin
# Canale cineblog01
# ------------------------------------------------------------

import re
import urlparse

from core import config, httptools
from platformcode import logger
from core import scrapertools
from core import servertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "cineblog01"

host = "https://cb01.pink/"

headers = [['Referer', host]]
thumbUA = "|User-Agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36"


def mainlist(item):
    logger.info("[thegroove360.cineblog01] mainlist")

    # Main options
    itemlist = [Item(channel=__channel__,
                     action="peliculas",
                     title="[COLOR azure]Film[COLOR orange] - Novita'[/COLOR]",
                     url=host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/popcorn_cinema_movie_.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film[COLOR orange] - Aggiornamenti[/COLOR]",
                     action="peliculas_lastupdate",
                     url="%s/lista-film-ultimi-100-film-aggiornati/" % host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/movie_new_P.png"),
                Item(channel=__channel__,
                     action="peliculas_lastupdate",
                     title="[COLOR azure]Film[COLOR orange] - Alta Definizione [HD][/COLOR]",
                     url="%slista-film-completa-hd-alta-definizione" % host,
                     extra="movie",
                     thumbnail="http://jcrent.com/apple%20tv%20final/HD.png"),
                Item(channel=__channel__,
                     action="menuhd",
                     title="[COLOR azure]Film[COLOR orange] - Menù HD[/COLOR]",
                     url=host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/Blu-Ray.png"),
                Item(channel=__channel__,
                     action="menugeneros",
                     title="[COLOR azure]Film[COLOR orange] - Per Genere[/COLOR]",
                     url=host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/popcorn_cinema_movie_.png"),
                Item(channel=__channel__,
                     action="menuanyos",
                     title="[COLOR azure]Film[COLOR orange] - Per Anno[/COLOR]",
                     url=host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/popcorn_cinema_movie_.png"),
                Item(channel=__channel__,
                     action="search",
                     title="[COLOR yellow]Cerca Film[/COLOR]",
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/search_P.png"),
                Item(channel=__channel__,
                     action="listserie",
                     title="[COLOR azure]Serie Tv[COLOR orange] - Novita'[/COLOR]",
                     url="%s/serietv/" % host,
                     extra="serie",
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/popcorn_cinema_movie_.png"),
                Item(channel=__channel__,
                     action="search",
                     title="[COLOR yellow]Cerca Serie Tv[/COLOR]",
                     extra="serie",
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/search_P.png")]

    return itemlist


def peliculas(item):
    logger.info("[thegroove360.cineblog01] peliculas")
    itemlist = []

    if item.url == "":
        item.url = host

    # Carica la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    patronvideos = r"class=card-image>.*?\s+<a\shref=([^\>]+)>\s+<img\ssrc=([^\s>]+).*?card-title\">.*?>(.*?)</a>"
    matches = re.compile(patronvideos, re.MULTILINE | re.S).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 contentType="movie",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail + thumbUA,
                 plot=scrapedtitle,
                 extra=item.extra,
                 viewmode="movie_with_plot"), tipo='movie'))

    # Next page mark
    try:
        patronvideos = 'href=([^\>]+)><i\sclass=\"fa fa-angle-right\"></i>'
        matches = re.compile(patronvideos, re.DOTALL).findall(data)

        if len(matches) > 0:
            next_page(itemlist, matches[0], "peliculas", item.extra)

    except:
        pass

    return itemlist


def next_page(itemlist, np_url, np_action, np_extra):
    scrapedtitle = "[COLOR orange]Successivo>>[/COLOR]"
    itemlist.append(
        Item(channel=__channel__,
             action=np_action,
             title=scrapedtitle,
             url=np_url,
             thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/next_1.png",
             extra=np_extra,
             plot=""))
    itemlist.append(
        Item(channel=__channel__,
             action="HomePage",
             title="[COLOR yellow]Torna Home[/COLOR]",
             folder=True))


def updates(item):
    logger.info("[thegroove360.cineblog01] updates")
    return menulist(item, '<select name="select1"(.*?)</select>')


def menugeneros(item):
    logger.info("[thegroove360.cineblog01] menugeneros")
    return menulist(item, 'Film per Genere<span\sclass=mega-indicator>.*?<ul\s(.*?)<a\sclass=mega-menu-link aria-haspopup=true')


def menuhd(item):
    logger.info("[thegroove360.cineblog01] menuhd")
    return menulist(item, 'Film HD Streaming<span\sclass=mega-indicator>.*?<ul\s(.*?)<a\sclass=mega-menu-link aria-haspopup=true')


def menuanyos(item):
    logger.info("[thegroove360.cineblog01] menuvk")
    return menulist(item, 'Film per Anno<span\sclass=mega-indicator>.*?<ul.*?>(.*?)</ul>')


def menulist(item, re_txt):
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data

    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data, re_txt)

    # The categories are the options for the combo
    patron = r'<a\s.*?href=([^>]+)>(.*?)</a>'
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
                 thumbnail=scrapedthumbnail,
                 extra=item.extra,
                 plot=scrapedplot))

    return itemlist


# Al llamarse "search" la función, el launcher pide un texto a buscar y lo añade como parámetro
def search(item, texto):
    logger.info("[thegroove360.cineblog01] " + item.url + " search " + texto)

    try:

        if item.extra == "movie":
            item.url = host + "/?s=" + texto
            return peliculas(item)
        if item.extra == "serie":
            item.url = host + "/serietv/?s=" + texto
            return listserie(item)

    # Continua la ricerca in caso di errore
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def listserie(item):
    logger.info("[thegroove360.cineblog01] listaserie")
    itemlist = []

    # Carica la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Estrae i contenuti
    patronvideos = r'class=\"card-image\">.*?\s+<a\shref=\"([^\"]+)\">\s+<img\ssrc=\"([^\"]+)\".*?card-title\">.*?>(.*?)</a>'
    matches = re.compile(patronvideos, re.S | re.MULTILINE).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="season_serietv",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail + thumbUA,
                 extra=item.extra,
                 plot=scrapedtitle), tipo='tv'))

    # Put the next page mark
    try:
        next_pagetxt = scrapertools.get_match(data, 'href=\"([^\"]+)\"><i class=\"fa fa-angle-right\"></i>')
        next_page(itemlist, next_pagetxt, "listserie", item.extra)

    except:
        pass

    return itemlist


def season_serietv(item):
    def load_season_serietv(html, item, itemlist, season_title):
        if len(html) > 0 and len(season_title) > 0:
            itemlist.append(
                Item(channel=__channel__,
                     action="episodios",
                     title="[COLOR azure]%s[/COLOR]" % season_title.replace("</", ""),
                     contentType="episode",
                     url=html,
                     extra='serie',
                     show=item.show))

    itemlist = []

    # Carica la pagina
    data = httptools.downloadpage(item.url, headers=headers).data
    data = scrapertools.decodeHtmlentities(data)

    patron = r'title=\"Espandi\">\s(.*?)</div>(.*?)</div>\s</div>'
    matches = re.compile(patron, re.MULTILINE | re.S).findall(data)

    for season_title, html in matches:
        load_season_serietv(html, item, itemlist, season_title)

    return itemlist


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


def episodios_serie_new(item):
    def load_episodios(html, item, itemlist, lang_title):
        # for data in scrapertools.decodeHtmlentities(html).splitlines():
        patron = r'(<p>.*?</a>)</p>'
        matches = re.compile(patron, re.MULTILINE).findall(html)
        for data in matches:
            # Estrae i contenuti
            scrapedtitle = scrapertools.find_single_match(data.replace("<strong>", ""), r'<p>([\d].*?)<a')
            if scrapedtitle != 'Categorie':
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

    logger.info("[thegroove360.cineblog01] episodios")

    itemlist = []

    lang_title = item.title
    if lang_title.upper().find('SUB') > 0:
        lang_title = 'SUB ITA'
    else:
        lang_title = 'ITA'

    html = item.url

    load_episodios(html, item, itemlist, lang_title)

    return itemlist


def findvideos(item):
    if item.extra == "movie":
        return findvid_film(item)
    if item.extra == 'serie':
        return findvid_serie(item)
    return []


def findvid_film(item):
    def load_links(itemlist, re_txt, color, desc_txt):
        streaming = scrapertools.find_single_match(data, re_txt)
        patron = r'<td><a\shref=([^\s]+)[^>]+>([^<]+)<'
        matches = re.compile(patron, re.DOTALL).findall(streaming)
        for scrapedurl, scrapedtitle in matches:
            logger.debug("##### findvideos %s ## %s ## %s ##" % (desc_txt, scrapedurl, scrapedtitle))
            title = "[COLOR " + color + "]" + desc_txt + ":[/COLOR] " + item.title + " [COLOR grey]" + QualityStr + "[/COLOR] [COLOR blue][" + scrapedtitle + "][/COLOR]"
            itemlist.append(
                Item(channel=__channel__,
                     action="play",
                     title=title,
                     url=scrapedurl,
                     server=scrapedtitle,
                     fulltitle=item.fulltitle,
                     thumbnail=item.thumbnail,
                     show=item.show,
                     plot=item.title + " [COLOR blue][" + scrapedtitle + "][/COLOR]",
                     folder=False))

    logger.info("[thegroove360.cineblog01] findvid_film")

    itemlist = []

    # Carica la pagina
    data = httptools.downloadpage(item.url, headers=headers).data
    data = scrapertools.decodeHtmlentities(data)

    # Extract the quality format
    patronvideos = '>([^<]+)</strong></div>'
    matches = re.compile(patronvideos, re.DOTALL).finditer(data)
    QualityStr = ""
    for match in matches:
        QualityStr = scrapertools.unescape(match.group(1))[6:]

    # STREAMANGO
    # matches = []
    # u = scrapertools.find_single_match(data, '(?://|\.)streamango\.com/(?:f/|embed/)?[0-9a-zA-Z]+')
    # if u: matches.append((u, 'Streamango'))

    # Estrae i contenuti - Streaming
    load_links(itemlist, r'<strong>Streaming:</strong>(.*?)<td\svalign=bottom>', "orange", "Streaming")

    # Estrae i contenuti - Streaming HD
    load_links(itemlist, r'<strong>Streaming HD[^<]+</strong>(.*?)<td\svalign=bottom>', "yellow", "Streaming HD")

    # Estrae i contenuti - Streaming 3D
    load_links(itemlist, r'<strong>Streaming 3D[^<]+</strong>(.*?)<td\svalign=bottom>', "pink", "Streaming 3D")

    # Estrae i contenuti - Download
    load_links(itemlist, r'<strong>Download:</strong>(.*?)<td\svalign=bottom>', "aqua", "Download")

    # Estrae i contenuti - Download HD
    load_links(itemlist, r'<strong>Download HD[^<]+</strong>(.*?)<td\svalign=bottom>>', "azure",
               "Download HD")

    if len(itemlist) == 0:
        itemlist = servertools.find_video_items(item=item)

    return itemlist


def findvid_serie(item):
    def load_vid_series(html, item, itemlist, blktxt):
        if len(blktxt) > 2:
            vtype = scrapertools.remove_htmltags(blktxt.strip()[:-1]) + " - "
        else:
            vtype = ''
        patron = r'<a href=\"([^\"]+)\"\starget=\"_blank\".*?>(.*?)<'
        # Estrae i contenuti
        matches = re.compile(patron, re.DOTALL).finditer(html)
        for match in matches:
            scrapedurl = match.group(1)
            scrapedtitle = match.group(2)
            title = item.title + " [COLOR blue][" + vtype + scrapedtitle + "][/COLOR]"
            itemlist.append(
                Item(channel=__channel__,
                     action="play",
                     title=title,
                     url=scrapedurl,
                     fulltitle=item.fulltitle,
                     show=item.show,
                     folder=False))

    logger.info("[thegroove360.cineblog01] findvid_serie")

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
    patron = '</a>(.*?)<a'
    matches = re.compile(patron, re.DOTALL).finditer(data)
    for match in matches:
        sep = match.group(1)
        if sep != ' – ':
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


def play(item):
    logger.info("[thegroove360.cineblog01] play")
    itemlist = []

    item.url = item.url.replace('"', "")

    ### Handling new cb01 wrapper
    if host[9:] + "/film/" in item.url:
        iurl = httptools.downloadpage(item.url, only_headers=True, follow_redirects=False).headers.get("location", "")
        logger.info("/film/ wrapper: %s" % iurl)
        if iurl:
            item.url = iurl

    if '/goto/' in item.url:
        item.url = item.url.split('/goto/')[-1].decode('base64')

    logger.debug("##############################################################")
    if "go.php" in item.url:
        data = httptools.downloadpage(item.url, headers=headers).data
        try:
            data = scrapertools.get_match(data, 'window.location.href = "([^"]+)";')
        except IndexError:
            try:
                # data = scrapertools.get_match(data, r'<a href="([^"]+)">clicca qui</a>')
                # In alternativa, dato che a volte compare "Clicca qui per proseguire":
                data = scrapertools.get_match(data, r'<a href="([^"]+)".*?class="btn-wrapper">.*?licca.*?</a>')
            except IndexError:
                data = httptools.downloadpage(item.url, only_headers=True, follow_redirects=False).headers.get(
                    "location", "")
        logger.debug("##### play go.php data ##\n%s\n##" % data)
    elif "/link/" in item.url:
        data = httptools.downloadpage(item.url, headers=headers).data
        from lib import jsunpack

        try:
            data = scrapertools.get_match(data, "(eval\(function\(p,a,c,k,e,d.*?)</script>")
            data = jsunpack.unpack(data)
            logger.debug("##### play /link/ unpack ##\n%s\n##" % data)
        except IndexError:
            logger.debug("##### The content is yet unpacked ##\n%s\n##" % data)

        data = scrapertools.find_single_match(data, 'var link(?:\s)?=(?:\s)?"([^"]+)";')

        if data.startswith('/'):
            data = urlparse.urljoin("http://swzz.xyz", data)
            data = httptools.downloadpage(data, headers=headers).data
        logger.debug("##### play /link/ data ##\n%s\n##" % data)
    else:
        data = item.url
        logger.debug("##### play else data ##\n%s\n##" % data)
    logger.debug("##############################################################")

    try:
        itemlist = servertools.find_video_items(data=data)

        for videoitem in itemlist:
            videoitem.title = item.show
            videoitem.fulltitle = item.fulltitle
            videoitem.show = item.show
            videoitem.thumbnail = item.thumbnail
            videoitem.channel = __channel__
    except AttributeError:
        logger.error("vcrypt data doesn't contain expected URL")

    return itemlist

def HomePage(item):
    import xbmc
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.Stefano)")


# ==================================================================================================================================================

def peliculas_lastupdate(item):
    logger.info("[thegroove360.cineblog01] peliculas_update")

    itemlist = []
    numpage = 14

    p = 1
    if '{}' in item.url:
        item.url, p = item.url.split('{}')
        p = int(p)

    # Descarga la pagina

    data = httptools.downloadpage(item.url, headers=headers).data

    # Estrae i contenuti
    patron = r'<a\shref=([^<]+)>([^<]+)</a><br>-'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for i, (scrapedurl, scrapedtitle) in enumerate(matches):
        if (p - 1) * numpage > i: continue
        if i >= p * numpage: break
        scrapedthumbnail = ""
        scrapedplot = ""

        scrapedtitle = scrapedtitle.replace("&#8211;", "-").replace("&#215;", "").replace("[Sub-ITA]", "(Sub Ita)")
        scrapedtitle = scrapedtitle.replace("/", " - ").replace("&#8217;", "'").replace("&#8230;", "...").replace("#",
                                                                                                                  "# ")
        scrapedtitle = scrapedtitle.strip()
        title = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="findvideos",
                 contentType="movie",
                 title=title,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=title,
                 show=title,
                 plot=scrapedplot,
                 folder=True), tipo='movie'))

    # Extrae el paginador
    if len(matches) >= p * numpage:
        scrapedurl = item.url + '{}' + str(p + 1)
        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="peliculas_lastupdate",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/next_1.png",
                 folder=True))

    return itemlist

# ==================================================================================================================================================
