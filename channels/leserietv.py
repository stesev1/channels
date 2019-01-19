# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# TheGroove360 / XBMC Plugin
# Canale 
# ------------------------------------------------------------
import re
import urlparse
import xbmc
from core import config, httptools
from platformcode import logger
from core import scrapertools
from core import servertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "leserietv"
host = 'http://www.guardareserie.tv'
headers = [['Referer', host]]

# -----------------------------------------------------------------
def mainlist(item):
    logger.info("Stefano.leserietv mainlist")
    itemlist = [Item(channel=__channel__,
                     action="novita",
                     title="[COLOR yellow]Novità[/COLOR]",
                     url=("%s/streaming/" % host),
                     thumbnail=thumbnail_novita,
                     fanart=FilmFanart),
                Item(channel=__channel__,
                     action="lista_serie",
                     title="[COLOR azure]Tutte le serie[/COLOR]",
                     url=("%s/streaming/" % host),
                     thumbnail=thumbnail_lista,
                     fanart=FilmFanart),
                Item(channel=__channel__,
                     title="[COLOR azure]Categorie[/COLOR]",
                     action="categorias",
                     url=host,
                     thumbnail=thumbnail_categoria,
                     fanart=FilmFanart),
                Item(channel=__channel__,
                     action="top50",
                     title="[COLOR azure]Top 50[/COLOR]",
                     url=("%s/top50.html" % host),
                     thumbnail=thumbnail_top,
                     fanart=FilmFanart),
                Item(channel=__channel__,
                     extra="serie",
                     action="search",
                     title="[COLOR orange]Cerca...[/COLOR][I](minimo 3 caratteri)[/I]",
                     thumbnail=thumbnail_cerca,
                     fanart=FilmFanart)]
    return itemlist
# =================================================================


# -----------------------------------------------------------------
def novita(item):
    logger.info("Stefano.leserietv novità")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data
    patron = '<div class="video-item-cover"[^<]+<a href="(.*?)">[^<]+<img src="(.*?)" alt="(.*?)">'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        scrapedthumbnail = host + scrapedthumbnail
        logger.info("title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle, viewmode="movie"), tipo='tv'))

    # Paginazione
    # ===========================================================
    patron = '<div class="pages">(.*?)</div>'
    paginazione = scrapertools.find_single_match(data, patron)
    patron = '<span>.*?</span>.*?href="([^"]+)".*?</a>'
    matches = re.compile(patron, re.DOTALL).findall(paginazione)
    scrapertools.printMatches(matches)
    # ===========================================================

    if len(matches) > 0:
        paginaurl = matches[0]
        itemlist.append(Item(channel=__channel__, action="novita"  , title="[COLOR orange]Successivo>>[/COLOR]", url=paginaurl, thumbnail=thumbnail_successivo, folder=True))
        itemlist.append(Item(channel=__channel__, action="HomePage", title="[COLOR yellow]Torna Home[/COLOR]"  ,thumbnail=ThumbnailHome, folder=True))

    return itemlist
# =================================================================

# -----------------------------------------------------------------
def lista_serie(item):
    logger.info("Stefano.leserietv lista_serie")
    itemlist = []

    post = "dlenewssortby=title&dledirection=asc&set_new_sort=dle_sort_cat&set_direction_sort=dle_direction_cat"
    data = httptools.downloadpage(item.url, post=post, headers=headers).data
    patron = '<div class="video-item-cover"[^<]+<a href="(.*?)">[^<]+<img src="(.*?)" alt="(.*?)">'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        scrapedthumbnail = host + scrapedthumbnail
        logger.info(scrapedurl + " " + scrapedtitle + scrapedthumbnail)
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle, viewmode="movie"), tipo='tv'))

    # Paginazione
    # ===========================================================
    patron = '<div class="pages">(.*?)</div>'
    paginazione = scrapertools.find_single_match(data, patron)
    patron = '<span>.*?</span>.*?href="([^"]+)".*?</a>'
    matches = re.compile(patron, re.DOTALL).findall(paginazione)
    scrapertools.printMatches(matches)
    # ===========================================================

    if len(matches) > 0:
        paginaurl = matches[0]
        itemlist.append(Item(channel=__channel__, action="novita", title="[COLOR orange]Successivo>>[/COLOR]", url=paginaurl,thumbnail=thumbnail_successivo, folder=True))
        itemlist.append(Item(channel=__channel__, action="HomePage", title="[COLOR yellow]Torna Home[/COLOR]", thumbnail=ThumbnailHome, folder=True))

    return itemlist
# =================================================================

# -----------------------------------------------------------------
def categorias(item):
    logger.info("Stefano.leserietv categorias")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data
    bloque = scrapertools.get_match(data, '<ul class="dropdown-menu cat-menu">(.*?)</ul>')
    patron = '<li ><a href="([^"]+)">(.*?)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        scrapedurl = urlparse.urljoin(item.url, scrapedurl)
        scrapedthumbnail = ""
        scrapedplot = ""
        itemlist.append(
            Item(channel=__channel__,
                 action="lista_serie",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot))

    return itemlist
# =================================================================

# -----------------------------------------------------------------
def search(item, texto):
    logger.info("Stefano.leserietv " + host + " search " + texto)

    itemlist = []

    post = "do=search&subaction=search&story=" + texto
    data = httptools.downloadpage(host, post=post, headers=headers).data

    patron = '<div class="video-item-cover"[^<]+<a href="(.*?)">[^<]+<img src="(.*?)" alt="(.*?)">'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        scrapedthumbnail = host + scrapedthumbnail
        logger.info(scrapedurl + " " + scrapedtitle + scrapedthumbnail)
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle), tipo='tv'))

    return itemlist
# =================================================================

# -----------------------------------------------------------------
def top50(item):
    logger.info("Stefano.leserietv top50")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data
    patron = 'class="top50item">\s*<[^>]+>\s*<.*?="([^"]+)">([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedtitle in matches:
        scrapedthumbnail = ""
        logger.debug(scrapedurl + " " + scrapedtitle)
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle, viewmode="movie"), tipo='tv'))

    return itemlist
# =================================================================

# -----------------------------------------------------------------
def episodios(item):
    logger.info("Stefano.leserietv episodios")
    itemlist = []
    data = httptools.downloadpage(item.url, headers=headers).data

    patron = '<li id[^<]+<[^<]+<.*?class="serie-title">(.*?)</span>[^>]+>[^<]+<.*?megadrive-(.*?)".*?data-link="([^"]+)">Megadrive</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedlongtitle, scrapedtitle, scrapedurl in matches:
        scrapedtitle = scrapedtitle.split('_')[0] + "x" + scrapedtitle.split('_')[1].zfill(2)

        scrapedtitle = scrapedtitle + " [COLOR orange]" + scrapedlongtitle + "[/COLOR]"
        itemlist.append(Item(channel=__channel__,
                             action="findvideos",
                             title=scrapedtitle,
                             fulltitle=scrapedtitle,
                             url=scrapedurl,
                             thumbnail=item.thumbnail,
                             fanart=item.fanart if item.fanart != "" else item.scrapedthumbnail,
                             show=item.fulltitle))

    if config.get_library_support() and len(itemlist) != 0:
        itemlist.append(
            Item(channel=__channel__,
                 title="Aggiungi alla libreria",
                 url=item.url,
                 action="add_serie_to_library",
                 extra="episodios",
                 contentType="episode",
                 show=item.show))

    return itemlist
# =================================================================

# ------------------------------------------------------------------
def findvideos(item):
    logger.info("Stefano.leserietv findvideos "+item.url)
    itemlist = []

    itemlist = servertools.find_video_items(data=item.url)

    for videoitem in itemlist:
        videoitem.title = "".join([item.title, '[COLOR green][B]' + videoitem.title + '[/B][/COLOR]'])
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__

    return itemlist
# =================================================================

def HomePage(item):
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.Stefano)")


# =================================================================
FilmFanart = "https://superrepo.org/static/images/fanart/original/script.artwork.downloader.jpg"
ThumbnailHome = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/81/Dynamic-blue-up.svg/580px-Dynamic-blue-up.svg.png"
thumbnail_novita="http://www.ilmioprofessionista.it/wp-content/uploads/2015/04/TVSeries3.png"
thumbnail_lista="http://www.ilmioprofessionista.it/wp-content/uploads/2015/04/TVSeries3.png"
thumbnail_categoria="https://farm8.staticflickr.com/7562/15516589868_13689936d0_o.png"
thumbnail_top="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"
thumbnail_cerca="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search"
thumbnail_successivo="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png"