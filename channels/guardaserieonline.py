# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Thegroove360 - XBMC Plugin
# Canale per guardaserieonline
# ------------------------------------------------------------

import re
import urlparse
import xbmc

from core import config
from core import httptools
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "guardaserieonline"
host = 'http://www.guardaserie.watch/'
headers = [['Referer', host]]

fanart_tvshow = "https://raw.githubusercontent.com/orione7/Pelis_images/master/fanart/tvshow_fanart.jpg"
thumb_tvnew = "https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/new_tvshows_P.png"
thumb_tvlist = "https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/tv_serie_P.png"
thumb_genres = "https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/genres_P.png"
thumb_genre = "https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/genres_P.png"
thumb_tvsub = "https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/tv_series_sub_P.png"
thumb_animation = "https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/animation_P.png"
thumb_top = "https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/popcorn_cinema_P.png"
thumb_search = "https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/search_P.png"
thumb_next = "https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/next_1.png"


def mainlist(item):
    logger.info("[thegroove360.guardaserieonline] mainlist")
    itemlist = [Item(channel=__channel__,
                     action="peliculas_update",
                     title="[COLOR azure]Serie TV - [COLOR orange]Aggiornate[/COLOR]",
                     url="%s/lista-serie-tv" % host,
                     thumbnail=thumb_tvnew,
                     fanart=fanart_tvshow),
                Item(channel=__channel__,
                     action="peliculas_sub",
                     title="[COLOR azure]Serie TV - [COLOR orange]Novita'[/COLOR]",
                     url="%s/lista-serie-tv" % host,
                     extra="Serie",
                     thumbnail=thumb_tvnew,
                     fanart=fanart_tvshow),
                Item(channel=__channel__,
                     action="categorias",
                     title="[COLOR azure]Serie TV - [COLOR orange]Categorie[/COLOR]",
                     url=host,
                     thumbnail=thumb_genres,
                     fanart=fanart_tvshow),
                Item(channel=__channel__,
                     action="peliculas",
                     title="[COLOR azure]Serie TV - [COLOR orange]Animazione[/COLOR]",
                     url="%s/category/animazione/" % host,
                     thumbnail=thumb_animation,
                     fanart=fanart_tvshow),
                Item(channel=__channel__,
                     action="peliculas_sub",
                     title="[COLOR azure]Serie TV - [COLOR orange]Inedite ([COLOR azure]Sub Ita[/COLOR])",
                     url="%s/lista-serie-tv" % host,
                     extra="Intedite",
                     thumbnail=thumb_tvsub,
                     fanart=fanart_tvshow),
                Item(channel=__channel__,
                     extra="serie",
                     action="search",
                     title="[COLOR orange]Cerca...[/COLOR]",
                     thumbnail=thumb_search,
                     fanart=fanart_tvshow)]
    return itemlist


# ==================================================================================================================================================

def search(item, texto):
    logger.info("[thegroove360.guardaserieonline] search")
    item.url = host + "/?s=" + texto
    try:
        return peliculas(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


# ==================================================================================================================================================

def categorias(item):
    logger.info("[thegroove360.guardaserieonline] categorias")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data
    bloque = scrapertools.get_match(data, 'SFOGLIA</span>(.*?)</ul>')
    patron = '<a\s*href="([^"]+)" title[^>]+>([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        scrapedurl = urlparse.urljoin(item.url, scrapedurl).strip()
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=thumb_genre,
                 folder=True))

    return itemlist


# ==================================================================================================================================================

def peliculas_update(item):
    logger.info("[thegroove360.guardaserieonline] peliculas_update")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data
    bloque = scrapertools.get_match(data,'text-color-grey">Ultimi episodi Aggiunti</h2>(.*?)text-color-grey">Nuove Serie</h2>')

    patron = r'<a\s*rel="nofollow" href="([^"]+)" class="box-link-serie">\s*<img\s*'
    patron += r'class="[^"]+"\s*title="[^"]+"\s*alt="([^"]+)"\s*[^s]+src="([^"]+)".*?'
    patron += r'<span\s*class="pull-right text-aqua">([^<]+)\s*</span>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedtitle, scrapedthumbnail, scraped_ep in matches:
        scrapedtitle = scrapedtitle.replace("locandina", "").replace("serie tv", "")
        scraped_ep = scraped_ep.replace("(", "").replace(")", "").strip()
        scraped_ep = "  ([COLOR yellow]" + scraped_ep + "[/COLOR])"
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle).strip()
        scrapedplot = ""
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]" + scraped_ep,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 plot=scrapedplot,
                 folder=True), tipo='tv'))

    return itemlist


# ==================================================================================================================================================

def peliculas_sub(item):
    logger.info("[thegroove360.guardaserieonline] peliculas_new")
    itemlist = []
    vxpage = 12

    p = 1
    if '{}' in item.url:
        item.url, p = item.url.split('{}')
        p = int(p)

    # Descarga la pagina
    data = httptools.downloadpage(item.url).data
    bloque = scrapertools.get_match(data, '%s</h2>(.*?)mostra altre serie tv' % item.extra)

    # Estrae i contenuti
    patron = r'<a\s*href="([^"]+)" class="box-link-serie">\s*<img\s*'
    patron += r'class="[^"]+"\s*title="[^"]+"\s*alt="([^"]+)"\s*[^s]+src="([^"]+)"'

    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for i, (scrapedurl, scrapedtitle, scrapedthumbnail) in enumerate(matches):
        if (p - 1) * vxpage > i: continue
        if i >= p * vxpage: break
        scrapedplot = ""
        scrapedtitle = scrapedtitle.replace("locandina", "").replace("serie tv", "")
        title = scrapertools.decodeHtmlentities(scrapedtitle).strip()
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="episodios",
                 contentType="tv",
                 title="[COLOR azure]" + title + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=title,
                 show=title,
                 plot=scrapedplot,
                 folder=True), tipo='tv'))

    # Extrae el paginador
    if len(matches) >= p * vxpage:
        scrapedurl = item.url + '{}' + str(p + 1)
        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="peliculas_sub",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail=thumb_next,
                 folder=True))

    return itemlist


# ==================================================================================================================================================

def peliculas(item):
    logger.info("[thegroove360.guardaserieonline] peliculas")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data

    patron = r'<a\s*href="([^"]+)" class="box-link-serie">\s*<img\s*'
    patron += r'class="[^"]+"\s*title="[^"]+"\s*alt="([^"]+)"\s*[^s]+src="([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        scrapedtitle = scrapedtitle.replace("locandina", "").replace("serie tv", "")
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle).strip()
        scrapedplot = ""
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 plot=scrapedplot,
                 folder=True), tipo='tv'))

    patron = '<a\s*class="nextpostslink" rel="next" href="([^"]+)">&raquo;</a>'
    next_page = scrapertools.find_single_match(data, patron)
    if len(matches) > 0:
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=next_page,
                 thumbnail=thumb_next,
                 folder=True))

    return itemlist


# ==================================================================================================================================================

def episodios(item):
    logger.info("[thegroove360.guardaserieonline] episodios")
    itemlist = []
    data = httptools.downloadpage(item.url, headers=headers).data

    #patron = '"number-episodes-on-img">.(.*?)<'
    #patron += '.*?meta-embed="([^"]+)" meta-embed2[^>]+>'
    patron = r'<a\s.*\s.*\s.*\s.*?>(.*?)</div>.*\s.*\s.*\s.*?>(.*?)<.*\s.*\s.*\s.*?(<span\s.*)\s</a>'
    matches = re.compile(patron, re.MULTILINE).findall(data)
    scrapertools.printMatches(matches)

    for scrapedep, scrapedtitle, scrapedurl in matches:
        scrapedthumbnail = ""
        itemlist.append(Item(channel=__channel__,
                             action="findvideos",
                             title= item.title + " - " + scrapedep + "[COLOR azure] " + scrapedtitle + "[/COLOR]",
                             fulltitle=item.fulltitle + " - " + scrapedtitle,
                             url=scrapedurl,
                             thumbnail=item.thumbnail,
                             plot="[COLOR orange][B]" + item.fulltitle + "[/B][/COLOR] " + item.plot,
                             fanart=item.fanart if item.fanart != "" else item.scrapedthumbnail,
                             show=item.show + " - " + scrapedtitle))

    return itemlist


# ==================================================================================================================================================

def findvideos(item):
    logger.info("[thegroove360.guardaserieonline] findvideos")

    itemlist = []

    itemlist = servertools.find_video_items(data=item.url)

    for videoitem in itemlist:
        servername = re.sub(r'[-\[\]\s]+', '', videoitem.title)
        videoitem.title = "".join([item.fulltitle, ' - [[COLOR orange]' + servername.capitalize() + '[/COLOR]]'])
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.plot = item.plot
        videoitem.channel = __channel__

    return itemlist


# ==================================================================================================================================================

def newest(categoria):
    logger.info("[thegroove360.guardaserieonline] newest" + categoria)
    itemlist = []
    item = Item()
    try:
        if categoria == "series":
            item.url = "%s/lista-serie-tv" % host
            item.action = "peliculas_update"
            itemlist = peliculas_update(item)

        if "Successiv" in itemlist[-1].title:
            itemlist.pop()
    # Se captura la excepción, para no interrumpir al canal novedades si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist


# ==================================================================================================================================================
# ==================================================================================================================================================
# ==================================================================================================================================================

def peliculas_new(item):
    logger.info("[thegroove360.guardaserieonline] peliculas_new")
    itemlist = []
    vxpage = 14

    p = 1
    if '{}' in item.url:
        item.url, p = item.url.split('{}')
        p = int(p)

    # Descarga la pagina
    data = httptools.downloadpage(item.url).data
    bloque = scrapertools.get_match(data,
                                    'text-color-grey">Nuove Serie</h2></div>(.*?)text-color-grey">Nuove Serie Intedite</h2></div>')

    # Estrae i contenuti
    patron = r'<a\s*href="([^"]+)" class="box-link-serie">\s*<img\s*'
    patron += r'class="[^"]+"\s*title="[^"]+"\s*alt="([^"]+)"\s*[^s]+src="([^"]+)"'

    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for i, (scrapedurl, scrapedtitle, scrapedthumbnail) in enumerate(matches):
        if (p - 1) * vxpage > i: continue
        if i >= p * vxpage: break
        scrapedplot = ""
        scrapedtitle = scrapedtitle.replace("locandina", "").replace("serie tv", "")
        title = scrapertools.decodeHtmlentities(scrapedtitle).strip()
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="episodios",
                 contentType="tv",
                 title="[COLOR azure]" + title + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=title,
                 show=title,
                 plot=scrapedplot,
                 folder=True), tipo='tv'))

    # Extrae el paginador
    if len(matches) >= p * vxpage:
        scrapedurl = item.url + '{}' + str(p + 1)
        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="peliculas_new",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail=thumb_next,
                 folder=True))

    return itemlist

# ==================================================================================================================================================