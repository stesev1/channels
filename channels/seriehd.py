# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# TheGroove360 / XBMC Plugin
# Canale seriehd
# ------------------------------------------------------------

import base64
import re
import urlparse

from core import config
from core import httptools
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "seriehd"
host = "https://www.seriehd.video"
headers = [['Referer', host]]


def mainlist(item):
    logger.info("[thegroove360.seriehd] mainlist")

    itemlist = [Item(channel=__channel__,
                     action="fichas",
                     title="[COLOR azure]Serie TV[COLOR orange] - Lista[/COLOR]",
                     url=host + "/serie-tv-streaming/",
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/new_tvshows_P.png"),
                Item(channel=__channel__,
                     action="fichas",
                     title="[COLOR azure]Serie TV[COLOR orange] - Italiane[/COLOR]",
                     url=host + "/serie-tv-streaming/serie-tv-italiane/",
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/tv_series_P.png"),
                Item(channel=__channel__,
                     action="fichas",
                     title="[COLOR azure]Serie TV[COLOR orange] - Americane[/COLOR]",
                     url=host + "/serie-tv-streaming/serie-tv-americane/",
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/tv_series_P.png"),
                Item(channel=__channel__,
                     action="sottomenu",
                     title="[COLOR azure]Serie TV[COLOR orange]- Categorie[/COLOR]",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/genres_P.png"),
                Item(channel=__channel__,
                     action="search",
                     extra="serie",
                     title="[COLOR orange]Cerca Serie TV...[/COLOR]",
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/search_P.png")]

    return itemlist


# ==============================================================================================================================================================================

def search(item, texto):
    logger.info("[thegroove360.seriehd] search")

    item.url = host + "/?s=" + texto

    try:
        return fichas(item)

    # Se captura la excepción, para no interrumpir al buscador global si un canal falla.
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


# ==============================================================================================================================================================================

def sottomenu(item):
    logger.info("[thegroove360.seriehd] sottomenu")
    itemlist = []

    data = scrapertools.cache_page(item.url)

    patron = '<a href="([^"]+)">([^<]+)</a>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        if "altadefinizione" in scrapedtitle or "Italiane" in scrapedtitle or "Americane" in scrapedtitle:
            continue
        itemlist.append(
            Item(channel=__channel__,
                 action="fichas",
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/genre_P.png"))

    # Elimina 'Serie TV' de la lista de 'sottomenu'
    itemlist.pop(0)

    return itemlist


# ==============================================================================================================================================================================

def fichas(item):
    logger.info("[thegroove360.seriehd] fichas")
    itemlist = []

    data = scrapertools.cache_page(item.url)

    patron = '<h2>(.*?)</h2>\s*'
    patron += '<img src="([^"]+)" alt="[^"]*" />\s*'
    patron += '<A HREF="([^"]+)">'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedtitle, scrapedthumbnail, scrapedurl in matches:
        scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle).strip()
        scrapedplot = ""
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 fulltitle=scrapedtitle,
                 url=scrapedurl,
                 show=scrapedtitle,
                 plot=scrapedplot,
                 thumbnail=scrapedthumbnail), tipo='tv'))

    patron = "<span class='current'>\d+</span><a rel='nofollow' class='page larger' href='([^']+)'>\d+</a>"
    next_page = scrapertools.find_single_match(data, patron)
    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="fichas",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=next_page,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/next_1.png"))

    return itemlist


# ==============================================================================================================================================================================

def episodios(item):
    logger.info("[thegroove360.seriehd] episodios")
    itemlist = []

    data = scrapertools.cache_page(item.url)

    patron = r'<iframe width=".+?" height=".+?" src="([^"]+)" allowfullscreen frameborder="0">'
    url = scrapertools.find_single_match(data, patron).replace("?seriehd", "")

    data = httptools.downloadpage(url).data

    patron = r'<li.*?\s><a href=\"([^\"]+)\">(\d+)<'
    seasons = re.compile(patron, re.MULTILINE).findall(data)

    for scrapedseason_url, scrapedseason in seasons:

        season_url = urlparse.urljoin(url, scrapedseason_url)
        data = httptools.downloadpage(season_url).data

        patron = r'<li.*?\s><a href="([^"]+)">(\d+)<'
        episodes = re.compile(patron, re.MULTILINE).findall(data)

        for scrapedepisode_url, scrapedepisode in episodes:
            episode_url = urlparse.urljoin(url, scrapedepisode_url)

            title = scrapedseason + "x" + scrapedepisode.zfill(2)

            itemlist.append(
                Item(channel=__channel__,
                     action="findvideos",
                     contentType="episode",
                     title=title + " - " + item.show,
                     url=episode_url,
                     fulltitle=item.fulltitle + " - " + title,
                     show=item.show + " - " + title,
                     plot="[COLOR orange]" + item.fulltitle + "[/COLOR] " + item.plot,
                     thumbnail=item.thumbnail))

    return itemlist


# ==============================================================================================================================================================================

def findvideos(item):
    logger.info("[thegroove360.seriehd] findvideos")

    itemlist = []

    # Descarga la página
    data = httptools.downloadpage(item.url).data.replace('\n', '')

    patron = r'<iframe id="iframeVid" width=".+?" height=".+?" src="([^"]+)" allowfullscreen'
    url = scrapertools.find_single_match(data, patron)
    if not url.startswith("https:"):
        url = "https:" + url

    if 'hdpass' in url:
        data = httptools.downloadpage(url, headers=headers).data

        start = data.find('<div class="row mobileRes">')
        end = data.find('<div id="playerFront">', start)
        data = data[start:end]

        patron_res = '<div class="row mobileRes">(.*?)</div>'
        patron_mir = '<div class="row mobileMirrs">(.*?)</div>'
        patron_media = r'<input type="hidden" name="urlEmbed" data-mirror="([^"]+)" id="urlEmbed" value="([^"]+)".*?>'

        res = scrapertools.find_single_match(data, patron_res)

        urls = []
        for res_url, res_video in scrapertools.find_multiple_matches(res,
                                                                     '<option.*?value="([^"]+?)">([^<]+?)</option>'):

            data = httptools.downloadpage(urlparse.urljoin(url, res_url), headers=headers).data.replace('\n', '')

            mir = scrapertools.find_single_match(data, patron_mir)

            for mir_url in scrapertools.find_multiple_matches(mir, '<option.*?value="([^"]+?)">[^<]+?</value>'):

                data = httptools.downloadpage(urlparse.urljoin(url, mir_url), headers=headers).data.replace('\n', '')

                for media_label, media_url in re.compile(patron_media).findall(data):
                    urls.append(url_decode(media_url))

        itemlist = servertools.find_video_items(data='\n'.join(urls))
        for videoitem in itemlist:
            servername = re.sub(r'[-\[\]\s]+', '', videoitem.title)
            videoitem.title = "".join(
                ['[COLOR azure][[COLOR orange]' + servername.capitalize() + '[/COLOR]] - ', item.fulltitle])
            videoitem.fulltitle = item.fulltitle
            videoitem.thumbnail = item.thumbnail
            videoitem.show = item.show
            videoitem.plot = item.plot
            videoitem.channel = __channel__

    return itemlist


# ==============================================================================================================================================================================

def url_decode(url_enc):
    lenght = len(url_enc)
    if lenght % 2 == 0:
        len2 = lenght / 2
        first = url_enc[0:len2]
        last = url_enc[len2:lenght]
        url_enc = last + first
        reverse = url_enc[::-1]
        return base64.b64decode(reverse)

    last_car = url_enc[lenght - 1]
    url_enc[lenght - 1] = ' '
    url_enc = url_enc.strip()
    len1 = len(url_enc)
    len2 = len1 / 2
    first = url_enc[0:len2]
    last = url_enc[len2:len1]
    url_enc = last + first
    reverse = url_enc[::-1]
    reverse = reverse + last_car
    return base64.b64decode(reverse)
