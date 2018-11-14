# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand-PureITA / XBMC Plugin
# Canale  serietvonline
# http://www.mimediacenter.info/foro/viewtopic.php?f=36&t=7808
# ------------------------------------------------------------
import re
import urlparse

from core import config, httptools
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "serietvonline"
host        = "https://serietvonline.net"
headers     = [['Referer', host]]


def mainlist(item):
    logger.info("[streamondemand-pureita serietvonline] mainlist")

    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Serie tv[COLOR orange] - Novità[/COLOR]",
                     action="lista_novita",
                     url=(host),
                     thumbnail=thumbnail_novita,
                     fanart=thumbnail_lista),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie tv[COLOR orange] -  Animazione[/COLOR]",
                     action="lista_serie",
                     url=("%s/lista-cartoni-animati-e-anime/" % host),
                     thumbnail=thumbnail_animation,
                     fanart=thumbnail_lista),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie tv[COLOR orange] - Documentari[/COLOR]",
                     action="lista_serie",
                     url=("%s/lista-documentari/" % host),
                     thumbnail=thumbnail_doc,
                     fanart=thumbnail_lista),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie tv[COLOR orange] - Anni 50 60 70 80[/COLOR]",
                     action="lista_serie",
                     url=("%s/lista-serie-tv-anni-60-70-80/" % host),
                     thumbnail=thumbnail_classic,
                     fanart=thumbnail_lista),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie tv[COLOR orange] - Alta Definizione[/COLOR]",
                     action="lista_serie",
                     url=("%s/lista-serie-tv-in-altadefinizione/" % host),
                     thumbnail=thumbnail_lista,
                     fanart=thumbnail_lista),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie tv[COLOR orange] - Italiane[/COLOR]",
                     action="lista_serie",
                     url=("%s/lista-serie-tv-italiane/" % host),
                     thumbnail=thumbnail_lista,
                     fanart=thumbnail_lista),
                Item(channel=__channel__,
                     title="[COLOR orange]Cerca...[/COLOR]",
                     action="search",
                     extra='serie',
                     thumbnail=thumbnail_cerca)]
    return itemlist
	
# ==================================================================================================================================================

def search(item, texto):
    logger.info("[streamondemand-pureita serietvonline] search " + texto)

    itemlist = []

    url = host + "/?s= " + texto

    data = httptools.downloadpage(url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = '<a href="([^"]+)"><span[^>]+><[^>]+><\/a>[^h]+h2>(.*?)<'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        scrapedplot = ""
        scrapedthumbnail = ""
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 extra=item.extra,
                 folder=True), tipo='tv'))

    # Extrae el paginador
    patronvideos = '<div class="siguiente"><a href="([^"]+)">'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="serietv",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail=thumbnail_successivo,
                 extra=item.extra,
                 folder=True))

    return itemlist
# ==================================================================================================================================================

def lista_serie(item):
    logger.info("[streamondemand-pureita serietvonline] lista_serie")
    itemlist = []
    PERPAGE = 14
	
    p = 1
    if '{}' in item.url:
        item.url, p = item.url.split('{}')
        p = int(p)
	
	
    data = httptools.downloadpage(item.url, headers=headers).data

    blocco = scrapertools.find_single_match(data, 'id="lcp_instance_0">(.*?)</ul>')
    patron='<a\s*href="([^"]+)" title="([^<]+)">[^<]+</a>'
    matches = re.compile(patron, re.DOTALL).findall(blocco)
    scrapertools.printMatches(matches)

    for i, (scrapedurl,scrapedtitle) in enumerate(matches):
        if (p - 1) * PERPAGE > i: continue
        if i >= p * PERPAGE: break
        scrapedtitle=scrapertools.decodeHtmlentities(scrapedtitle).strip()
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 title=scrapedtitle,
                 fulltitle=scrapedtitle,
                 url=scrapedurl,
                 show=scrapedtitle,
                 folder=True),tipo='tv'))

    # Extrae el paginador
    if len(matches) >= p * PERPAGE:
        scrapedurl = item.url + '{}' + str(p + 1)
        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="lista_serie",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))

    return itemlist
	
# ==================================================================================================================================================

def lista_novita(item):
    logger.info("[streamondemand-pureita serietvonline] lista_novita")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data

    #blocco = scrapertools.find_single_match(data, '<div id="box_movies">(.*?)</span></div></div>')
    patron = '<img\s*src="([^"]+)"\s*alt[^>]+>\s*<a\s*href="([^"]+)">'
    patron += '<span\s*class="player"></span></a>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>\s*<h2>(.*?)</h2>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedthumbnail, scrapedurl,scrapedtitle in matches:
        scrapedtitle=scrapertools.decodeHtmlentities(scrapedtitle).strip()
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 title=scrapedtitle,
                 fulltitle=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 show=scrapedtitle,
                 folder=True),tipo='tv'))
								 
    patron = '<a\s*href="([^"]+)" >Siguiente <span\s*class="icon-caret-right"></span>'
    next_page = scrapertools.find_single_match(data, patron)
    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="lista_novita",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=next_page,
                 thumbnail=thumbnail_successivo))

    return itemlist

# ==================================================================================================================================================

def episodios(item):
    logger.info("[streamondemand-pureita serietvonline] episodios")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data
    blocco = scrapertools.get_match(data, '</table></p>(.*?)</table></p>')
    if not "href" in blocco:
	  return episodios_all(item)


    patron = '<tr><td>(.*?)</td><tr>'
    matches = re.compile(patron, re.DOTALL).findall(blocco)
    scrapertools.printMatches(matches)

    for puntata in matches:
        puntata = "<td class=\"title\">"+puntata

        scrapedtitle=scrapertools.find_single_match(puntata, '<td class="title">(.*?)</td>')
        scrapedtitle=scrapedtitle.replace("avi","")
        scrapedtitle=scrapedtitle.replace(item.title,"").strip()
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=puntata,
                 thumbnail=item.thumbnail,
                 plot="[COLOR orange]" + item.title + "[/COLOR] " + item.plot,
                 folder=True))
				 
    return itemlist	

# ==================================================================================================================================================
	
def episodios_all(item):
    logger.info("[streamondemand-pureita.serietvonline] episodios_all")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data
    patron = r'<iframe\s*src=\'([^"]+)\' FRAMEBORDER=0 MARGINWIDTH=0 MARGINHEIGHT=0 SCROLLING=NO WIDTH=100% HEIGHT=680 allowfullscreen></iframe>'
    url = scrapertools.find_single_match(data, patron)

    data = httptools.downloadpage(url).data.replace('\n', '')


    section_stagione = scrapertools.find_single_match(data, '<b>Stagione.*?</b>(.*?)</div>')
    patron = "<a href='(.*?)' class='selected_btn'>\s*(\d+)\s*</button>"
    seasons = re.compile(patron, re.DOTALL).findall(section_stagione)

    for scrapedseason_url, scrapedseason in seasons:

        season_url = urlparse.urljoin(url, scrapedseason_url)
        data = httptools.downloadpage(season_url).data.replace('\n', '')

        section_episodio = scrapertools.find_single_match(data, "<b>Episodio.*?</b>(.*?)</div><div class='bg-primary'>")
        patron = "<a href='(.*?)'>[^>]+>\s*(\d+)\s*<"
        episodes = re.compile(patron, re.DOTALL).findall(section_episodio)

        for scrapedepisode_url, scrapedepisode in episodes:
            episode_url = urlparse.urljoin(url, scrapedepisode_url)

            title = scrapedseason + "x" + scrapedepisode.zfill(2)

            itemlist.append(
                Item(channel=__channel__,
                     action="findvideos_all",
                     contentType="episode",
                     title=title + " - " + item.title,
                     url=episode_url, 
                     fulltitle=title,
                     show=item.show,
                     plot="[COLOR orange]" + item.title + "[/COLOR] " + item.plot,
                     thumbnail=item.thumbnail))


    return itemlist	
	

# ==================================================================================================================================================

def findvideos(item):
    logger.info("[streamondemand-pureita serietvonline] findvideos")
    itemlist = []

    patron = "<a\s*href='([^']+)[^>]+>[^>]+>([^<]+)<\/a>"
    matches = re.compile(patron, re.DOTALL).findall(item.url)

    for scrapedurl,scrapedserver in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 fulltitle=item.fulltitle,
                 show=item.show,
                 title="[COLOR orange][" + scrapedserver.strip() + "][COLOR azure] " + item.title + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=item.thumbnail,
                 plot=item.plot,
                 folder=True))
				 

    return itemlist

# ==================================================================================================================================================
	
def findvideos_all(item):
    logger.info("[streamondemand-pureita serietvonline] findvideos_all")
    itemlist = []

    # Descarga la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data


    patron = "<IFRAME SRC='(.*?)' FRAMEBORDER=0"
    matches = re.compile(patron, re.DOTALL).findall(data)
	
    for scrapedurl in matches:        
	      itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        videoitem.title = videoitem.title + item.title
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.show = item.show
        videoitem.plot = item.plot
        videoitem.channel = __channel__
        itemlist.append(videoitem)

    return itemlist
	

# ==================================================================================================================================================

def play(item):
    itemlist=[]

    data = item.url
    while 'vcrypt' in item.url:
        item.url = httptools.downloadpage(item.url, only_headers=True, follow_redirects=False).headers.get("location")
        data = item.url

    logger.debug(data)

    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        videoitem.title = item.title
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__

    return itemlist
	
# ==================================================================================================================================================

thumbnail_fanart="https://superrepo.org/static/images/fanart/original/script.artwork.downloader.jpg"
ThumbnailHome = "https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/return_home_P.png"
thumbnail_novita="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/new_tvshows_P.png"
thumbnail_animation="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/animation_P.png"
thumbnail_doc="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/documentary_P.png"
thumbnail_classic="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/classictv_P.png"
thumbnail_lista="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/tv_serie_P.png"
thumbnail_top="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"
thumbnail_cerca="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png"
thumbnail_successivo="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png"
