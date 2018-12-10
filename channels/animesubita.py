# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Thegroove360 - XBMC Plugin
# Canale per AnimeSubIta
# ------------------------------------------------------------

import re, urllib, urlparse

from core import servertools, httptools, scrapertools, config
from platformcode import logger
from core.item import Item
from core.tmdb import infoSod

__channel__ = "animesubita"
host = "http://www.animesubita.org"
headers = [['Referer', host]]

# ----------------------------------------------------------------------------------------------------------------
def mainlist(item):
    logger.info()
    itemlist = [Item(channel=__channel__,
                     action="lista_anime_completa",
                     title=color("Lista Anime (%s)" % color("Slow", "red"), "azure"),
                     url="%s/lista-anime/" % host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/popcorn_cinema_movie_.png"),
                Item(channel=__channel__,
                     action="ultimiep",
                     title=color("Ultimi Episodi", "azure"),
                     url="%s/category/ultimi-episodi/" % host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/popcorn_cinema_movie_.png"),
                Item(channel=__channel__,
                     action="lista_anime",
                     title=color("Anime in corso", "azure"),
                     url="%s/category/anime-in-corso/" % host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/popcorn_cinema_movie_.png"),
                Item(channel=__channel__,
                     action="categorie",
                     title=color("Categorie", "azure"),
                     url="%s/generi/" % host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/popcorn_cinema_movie_.png"),
                Item(channel=__channel__,
                     action="search",
                     title=color("Cerca anime ...", "yellow"),
                     extra="anime",
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/search_P.png")
                ]

    return itemlist

# ================================================================================================================
# ----------------------------------------------------------------------------------------------------------------
def newest(categoria):
    logger.info()
    itemlist = []
    item = Item()
    try:
        if categoria == "anime":
            item.url = host
            item.action = "ultimiep"
            itemlist = ultimiep(item)

            if itemlist[-1].action == "ultimiep":
                itemlist.pop()
    # Continua l'esecuzione in caso di errore 
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist

# ================================================================================================================
# ----------------------------------------------------------------------------------------------------------------
def search(item, texto):
    logger.info()
    item.url = host + "/?s=" + texto
    try:
        return lista_anime(item)
    # Continua la ricerca in caso di errore 
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def categorie(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    patron = r'<li><a title="[^"]+" href="([^"]+)">([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        itemlist.append(
                Item(channel=__channel__,
                     action="lista_anime",
                     title=scrapedtitle.replace('Anime', '').strip(),
                     url=scrapedurl,
                     extra="tv",
                     thumbnail=item.thumbnail,
                     folder=True))

    return itemlist

# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def ultimiep(item):
    logger.info("ultimiep")
    itemlist = lista_anime(item, False, False)

    for itm in itemlist:
        title = scrapertools.decodeHtmlentities(itm.title)
        # Pulizia titolo
        title = title.replace("Streaming", "").replace("&", "")
        title = title.replace("Download", "")
        title = title.replace("Sub Ita", "").strip()
        eptype = scrapertools.find_single_match(title, "((?:Episodio?|OAV))")
        cleantitle = re.sub(r'%s\s*\d*\s*(?:\(\d+\)|)' % eptype, '', title).strip()
        # Creazione URL
        url = re.sub(r'%s-?\d*-' % eptype.lower(), '', itm.url)
        if "-streaming" not in url:
            url = url.replace("sub-ita", "sub-ita-streaming")

        epnumber = ""
        if 'episodio' in eptype.lower():
            epnumber = scrapertools.find_single_match(title.lower(), r'episodio?\s*(\d+)')
            eptype += ":? " + epnumber

        extra = "<tr>\s*<td[^>]+><strong>(?:[^>]+>|)%s(?:[^>]+>[^>]+>|[^<]*|[^>]+>)</strong>" % eptype
        itm.title = color(title, 'azure')
        itm.action = "findvideos"
        itm.url = url
        itm.fulltitle = cleantitle
        itm.extra = extra
        itm.show = re.sub(r'Episodio\s*', '', title)
        itm.thumbnail = item.thumbnail

    return itemlist

# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def lista_anime(item, nextpage=True, show_lang=True):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data
    blocco = scrapertools.find_single_match(data, r'<div class="post-list group">(.*?)</nav><!--/.pagination-->')
    # patron = r'<a href="([^"]+)" title="([^"]+)">\s*<img[^s]+src="([^"]+)"[^>]+>' # Patron con thumbnail, Kodi non scarica le immagini dal sito
    patron = r'<a href="([^"]+)" title="([^"]+)">'
    matches = re.compile(patron, re.DOTALL).findall(blocco)

    for scrapedurl, scrapedtitle in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle.strip()).replace("Streaming", "")
        scrapedtitle = re.sub(r'\s+', ' ', scrapedtitle)

        lang = scrapertools.find_single_match(scrapedtitle, r"([Ss][Uu][Bb]\s*[Ii][Tt][Aa])")

        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodi",
                 contentType="tv",
                 title=color(scrapedtitle.replace(lang, "(%s)" % color(lang, "red") if show_lang else "").strip(), 'azure'),
                 fulltitle=scrapedtitle.replace(lang, ""),
                 url=scrapedurl,
                 extra="tv",
                 folder=True), tipo="tv"))

    if nextpage:
        patronvideos = r'<link rel="next" href="([^"]+)"\s*/>'
        matches = re.compile(patronvideos, re.DOTALL).findall(data)

        if len(matches) > 0:
            scrapedurl = matches[0]
            itemlist.append(
                Item(channel=__channel__,
                    action="HomePage",
                    title=color("Torna Home", "yellow"),
                    folder=True)),
            itemlist.append(
                Item(channel=__channel__,
                    action="lista_anime",
                    title=color("Successivo >>", "orange"),
                    url=scrapedurl,
                    thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/next_1.png",
                    folder=True))

    return itemlist

# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def lista_anime_completa(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data
    blocco = scrapertools.find_single_match(data, r'<ul class="lcp_catlist"[^>]+>(.*?)</ul>')
    patron = r'<a href="([^"]+)"[^>]+>([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(blocco)

    for scrapedurl, scrapedtitle in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle.strip())

        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodi",
                 contentType="tv",
                 title=color(scrapedtitle, 'azure'),
                 fulltitle=scrapedtitle,
                 url=scrapedurl,
                 extra="tv",
                 folder=True), tipo="tv"))

    return itemlist

# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def episodi(item):
    logger.info()
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

# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def findvideos(item):
    logger.info()
    itemlist = []

    if item.extra:
        data = httptools.downloadpage(item.url, headers=headers).data

        blocco = scrapertools.get_match(data, r'%s(.*?)</tr>' % item.extra)
        scrapedurl = scrapertools.find_single_match(blocco, r'<a href="([^"]+)"[^>]+>')
        url = scrapedurl
    else:
        url = item.url

    if 'animesubita' in url:
        headers.append(['Referer', item.url])
        data = httptools.downloadpage(url, headers=headers).data
        itemlist.extend(servertools.find_video_items(data=data))

        for videoitem in itemlist:
            videoitem.title = item.title + videoitem.title
            videoitem.fulltitle = item.fulltitle
            videoitem.show = item.show
            videoitem.thumbnail = item.thumbnail
            videoitem.channel = __channel__

        url = "%s/%s" % (host, url.split('/')[-1])
        data = httptools.downloadpage(url, headers=headers).data
        patron = r'<source\s*src=(?:"|\')([^"\']+?)(?:"|\')\s*type=(?:"|\')video/mp4(?:"|\')>'
        matches = re.compile(patron, re.DOTALL).findall(data)
        headers.append(['Referer', url])
        for video in matches:
            print "EE: %s" % video
            itemlist.append(Item(channel=__channel__, action="play", title=color("[%s] %s" % (color("Diretto", 'orange'), item.title), 'azure'),
                                 url=video + '|' + urllib.urlencode(dict(headers)), folder=False))
    else:
        itemlist.extend(servertools.find_video_items(data=url))

        for videoitem in itemlist:
            server = re.sub(r'[-\[\]\s]+', '', videoitem.title)
            videoitem.title = "".join([color("[%s] " % color(server.capitalize(), 'orange'), 'azure'), item.title])
            videoitem.fulltitle = item.fulltitle
            videoitem.show = item.show
            videoitem.thumbnail = item.thumbnail
            videoitem.channel = __channel__
    return itemlist

# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def color(text, color):
    return "[COLOR %s]%s[/COLOR]" % (color, text)

def HomePage(item):
    import xbmc
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.Stefano/?action=sod)")

# ================================================================================================================
