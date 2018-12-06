# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Thegroove360 - XBMC Plugin
# Canale  per http://animeinstreaming.net/
# ------------------------------------------------------------

import re
import urllib
import urlparse

import xbmc

from core import config, httptools
from platformcode import logger
from core import scrapertools
from core import servertools
from core.item import Item
from core.tmdb import infoSod
from servers.decrypters import expurl

__channel__ = "animeforce"

host = "https://ww1.animeforce.org/"

headers = [['Referer', host]]

PERPAGE = 20

# -----------------------------------------------------------------
def mainlist(item):
    log("mainlist", "mainlist")
    itemlist = [Item(channel=__channel__,
                     action="lista_anime",
                     title="[COLOR azure]Anime [/COLOR]- [COLOR lightsalmon]Lista Completa[/COLOR]",
                     url=host + "/lista-anime/",
                     thumbnail=CategoriaThumbnail,
                     fanart=CategoriaFanart),
                Item(channel=__channel__,
                     action="animeaggiornati",
                     title="[COLOR azure]Anime Aggiornati[/COLOR]",
                     url=host,
                     thumbnail=CategoriaThumbnail,
                     fanart=CategoriaFanart),
                Item(channel=__channel__,
                     action="ultimiep",
                     title="[COLOR azure]Ultimi Episodi[/COLOR]",
                     url=host,
                     thumbnail=CategoriaThumbnail,
                     fanart=CategoriaFanart),
                Item(channel=__channel__,
                     action="search",
                     title="[COLOR yellow]Cerca ...[/COLOR]",
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/search_P.png")]

    return itemlist


# =================================================================

# -----------------------------------------------------------------
def newest(categoria):
    log("newest", "newest" + categoria)
    itemlist = []
    item = Item()
    try:
        if categoria == "anime":
            item.url = host
            item.action = "ultimiep"
            itemlist = ultimiep(item)

            if itemlist[-1].action == "ultimiep":
                itemlist.pop()
    # Continua la ricerca in caso di errore
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist


# =================================================================

# -----------------------------------------------------------------
def search(item, texto):
    log("search", "search")
    item.url = host + "/?s=" + texto
    try:
        return search_anime(item)
    # Continua la ricerca in caso di errore
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


# =================================================================

# -----------------------------------------------------------------
def search_anime(item):
    log("search_anime", "search_anime")
    itemlist = []

    data = httptools.downloadpage(item.url).data

    patron = '<a href="([^"]+)"><img.*?src="([^"]+)".*?title="([^"]+)".*?/>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        if "Sub Ita Download & Streaming" in scrapedtitle or "Sub Ita Streaming":
            itemlist.append(
                Item(channel=__channel__,
                     action="episodios",
                     title=scrapedtitle,
                     url=scrapedurl,
                     fulltitle=scrapedtitle,
                     show=scrapedtitle,
                     thumbnail=scrapedthumbnail))

    return itemlist


# =================================================================

# -----------------------------------------------------------------
def animeaggiornati(item):
    log("animeaggiornati", "animeaggiornati")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data

    patron = r'<img.*?src="([^"]+)"[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+><a href="([^"]+)">([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedthumbnail, scrapedurl, scrapedtitle in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        if 'Streaming' in scrapedtitle:
            # Pulizia titolo
            cleantitle = scrapedtitle.replace("Streaming", "").replace("&", "")
            cleantitle = cleantitle.replace("Download", "")
            cleantitle = cleantitle.replace("Sub Ita", "")
            cleantitle = re.sub(r'Episodio?\s*\d+\s*(?:\(\d+\)|)\s*[\(OAV\)]*', '', cleantitle)
            # Creazione URL
            scrapedurl = re.sub(r'episodio?-?\d+-?(?:\d+-|)[oav]*', '', scrapedurl)
            if 'download' not in scrapedurl:
                scrapedurl = scrapedurl.replace('-streaming', '-download-streaming')
            itemlist.append(infoSod(
                Item(channel=__channel__,
                     action="episodios",
                     title=cleantitle,
                     url=scrapedurl,
                     fulltitle=cleantitle,
                     show=cleantitle,
                     thumbnail=scrapedthumbnail), tipo="tv"))

    return itemlist


# =================================================================

# -----------------------------------------------------------------
def ultimiep(item):
    log("ultimiep", "ultimiep")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data

    patron = r'<img.*?src="([^"]+)"[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+><a href="([^"]+)">([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedthumbnail, scrapedurl, scrapedtitle in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        if 'Streaming' in scrapedtitle:
            # Pulizia titolo
            scrapedtitle = scrapedtitle.replace("Streaming", "").replace("&", "")
            scrapedtitle = scrapedtitle.replace("Download", "")
            scrapedtitle = scrapedtitle.replace("Sub Ita", "").strip()
            eptype = scrapertools.find_single_match(scrapedtitle, "((?:Episodio?|OAV))")
            cleantitle = re.sub(r'%s\s*\d*\s*(?:\(\d+\)|)' % eptype, '', scrapedtitle).strip()
            if '(Fine)' in scrapedtitle:
                scrapedtitle = scrapedtitle.replace('(Fine)', ' ').strip() + " (Fine)"
                cleantitle = cleantitle.replace('(Fine)', '')
            # Creazione URL
            if 'download' not in scrapedurl:
                scrapedurl = scrapedurl.replace('-streaming', '-download-streaming')
            scrapedurl = re.sub(r'%s-?\d*-' % eptype.lower(), '', scrapedurl).replace('-fine', '')

            epnumber = ""
            if 'episodio' in eptype.lower():
                epnumber = scrapertools.find_single_match(scrapedtitle.lower(), r'episodio?\s*(\d+)')
                eptype += ":? " + epnumber

            extra = "<tr>\s*<td[^>]+><strong>(?:[^>]+>|)%s(?:[^>]+>[^>]+>|[^<]*|[^>]+>)</strong>" % eptype
            itemlist.append(infoSod(
                Item(channel=__channel__,
                     action="findvideos",
                     title=scrapedtitle,
                     url=scrapedurl,
                     fulltitle=cleantitle,
                     extra=extra,
                     show=re.sub(r'Episodio\s*', '', scrapedtitle),
                     thumbnail=scrapedthumbnail), tipo="tv"))

    return itemlist


# =================================================================

# -----------------------------------------------------------------
def lista_anime(item):
    log("lista_anime", "lista_anime")

    itemlist = []

    p = 1
    if '{}' in item.url:
        item.url, p = item.url.split('{}')
        p = int(p)

    # Carica la pagina
    data = httptools.downloadpage(item.url).data

    # Estrae i contenuti
    patron = r'<li>\s*<strong>\s*<a\s*href="([^"]+?)">([^<]+?)</a>\s*</strong>\s*</li>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    scrapedplot = ""
    scrapedthumbnail = ""
    for i, (scrapedurl, scrapedtitle) in enumerate(matches):
        if (p - 1) * PERPAGE > i: continue
        if i >= p * PERPAGE: break
        title = scrapertools.decodeHtmlentities(scrapedtitle).strip()
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="episodios",
                 title=title,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=title,
                 show=title,
                 plot=scrapedplot,
                 folder=True), tipo='movie'))

    if len(itemlist) > 0:
        itemlist.append(
            Item(channel=__channel__,
                 action="HomePage",
                 title="[COLOR yellow]Torna Home[/COLOR]",
                 folder=True)),

    if len(matches) >= p * PERPAGE:
        scrapedurl = item.url + '{}' + str(p + 1)
        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="lista_anime",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png",
                 folder=True))

    return itemlist

# =================================================================

# -----------------------------------------------------------------
def episodios(item):
    itemlist = []

    data = httptools.downloadpage(item.url).data

    patron = '<td style="[^"]*?">\s*.*?<strong>(.*?)</strong>.*?\s*</td>\s*<td style="[^"]*?">\s*<a href="([^"]+?)"[^>]+>\s*<img.*?src="([^"]+?)".*?/>\s*</a>\s*</td>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedtitle, scrapedurl, scrapedimg in matches:
        if 'nodownload' in scrapedimg or 'nostreaming' in scrapedimg:
            continue
        if 'vvvvid' in scrapedurl.lower():
            itemlist.append(Item(title='I Video VVVVID Non sono supportati'))
            continue

        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedtitle = re.sub(r'<[^>]*?>', '', scrapedtitle)
        scrapedtitle = '[COLOR azure][B]' + scrapedtitle + '[/B][/COLOR]'
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 contentType="episode",
                 title=scrapedtitle,
                 url=urlparse.urljoin(host, scrapedurl),
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 plot=item.plot,
                 fanart=item.thumbnail,
                 thumbnail=item.thumbnail))

    # Comandi di servizio
    if config.get_library_support() and len(itemlist) != 0:
        itemlist.append(
            Item(channel=__channel__,
                 title="Aggiungi alla libreria",
                 url=item.url,
                 action="add_serie_to_library",
                 extra="episodios",
                 show=item.show))

    return itemlist


# ==================================================================

# -----------------------------------------------------------------
def findvideos(item):
    logger.info("streamondemand.animeforce findvideos")

    itemlist = []

    if item.extra:
        data = httptools.downloadpage(item.url, headers=headers).data

        blocco = scrapertools.get_match(data, r'%s(.*?)</tr>' % item.extra)
        scrapedurl = scrapertools.find_single_match(blocco, r'<a href="([^"]+)"[^>]+>')
        url = scrapedurl
    else:
        url = item.url

    if 'adf.ly' in url:
        url = expurl.expand_url(url)
    elif 'bit.ly' in url:
        url = httptools.downloadpage(url, only_headers=True, follow_redirects=False).headers.get("location")

    if 'animeforce' in url:
        headers.append(['Referer', item.url])
        data = httptools.downloadpage(url, headers=headers).data
        itemlist.extend(servertools.find_video_items(data=data))

        for videoitem in itemlist:
            videoitem.title = item.title + videoitem.title
            videoitem.fulltitle = item.fulltitle
            videoitem.show = item.show
            videoitem.thumbnail = item.thumbnail
            videoitem.channel = __channel__

        url = url.split('&')[0]
        data = httptools.downloadpage(url, headers=headers).data
        patron = """<source\s*src=(?:"|')([^"']+?)(?:"|')\s*type=(?:"|')video/mp4(?:"|')>"""
        matches = re.compile(patron, re.DOTALL).findall(data)
        headers.append(['Referer', url])
        for video in matches:
            itemlist.append(Item(channel=__channel__, action="play", title=item.title,
                                 url=video + '|' + urllib.urlencode(dict(headers)), folder=False))
    else:
        itemlist.extend(servertools.find_video_items(data=url))

        for videoitem in itemlist:
            videoitem.title = item.title + videoitem.title
            videoitem.fulltitle = item.fulltitle
            videoitem.show = item.show
            videoitem.thumbnail = item.thumbnail
            videoitem.channel = __channel__

    return itemlist


# ==================================================================

# =================================================================
# Funzioni di servizio
# -----------------------------------------------------------------
def scrapedAll(url="", patron=""):
    data = httptools.downloadpage(url).data
    MyPatron = patron
    matches = re.compile(MyPatron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    return matches


# =================================================================

# -----------------------------------------------------------------
def scrapedSingle(url="", single="", patron=""):
    data = httptools.downloadpage(url).data
    paginazione = scrapertools.find_single_match(data, single)
    matches = re.compile(patron, re.DOTALL).findall(paginazione)
    scrapertools.printMatches(matches)

    return matches


# =================================================================

# -----------------------------------------------------------------
def Crea_Url(pagina="1", azione="ricerca", categoria="", nome=""):
    # esempio
    # chiamate.php?azione=ricerca&cat=&nome=&pag=
    Stringa = host + "chiamate.php?azione=" + azione + "&cat=" + categoria + "&nome=" + nome + "&pag=" + pagina
    log("crea_Url", Stringa)
    return Stringa


# =================================================================

# -----------------------------------------------------------------
def log(funzione="", stringa="", canale=__channel__):
    logger.debug("[" + canale + "].[" + funzione + "] " + stringa)


# =================================================================

# -----------------------------------------------------------------
def HomePage(item):
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.Stefano/?action=sod)")


# =================================================================

# =================================================================
# riferimenti di servizio
# -----------------------------------------------------------------
AnimeThumbnail = "http://img15.deviantart.net/f81c/i/2011/173/7/6/cursed_candies_anime_poster_by_careko-d3jnzg9.jpg"
AnimeFanart = "https://i.ytimg.com/vi/IAlbvyBdYdY/maxresdefault.jpg"
CategoriaThumbnail = "http://static.europosters.cz/image/750/poster/street-fighter-anime-i4817.jpg"
CategoriaFanart = "https://i.ytimg.com/vi/IAlbvyBdYdY/maxresdefault.jpg"
CercaThumbnail = "http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search"
CercaFanart = "https://i.ytimg.com/vi/IAlbvyBdYdY/maxresdefault.jpg"
HomeTxt = "[COLOR yellow]Torna Home[/COLOR]"
AvantiTxt = "[COLOR orange]Successivo>>[/COLOR]"
AvantiImg = "http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png"
