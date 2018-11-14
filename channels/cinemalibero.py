# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# StreamOnDemand-PureITA / XBMC Plugin
# Canale cinemalibero
# http://www.mimediacenter.info/foro/viewtopic.php?f=36&t=7808
# ------------------------------------------------------------
import re
import urlparse

from core import config
from core import httptools
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "cinemalibero"
host = "https://www.cinemalibero.red"
headers = [['Referer', host]]


def mainlist(item):
    logger.info("streamondemand-pureita cinemalibero mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Film [COLOR orange]- Novita'[/COLOR]",
                     extra="movie",
                     action="peliculas",
                     url="%s/category/film-in-streaming/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/popcorn_cinema_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film [COLOR orange]- Categorie[/COLOR]",
                     extra="movie",
                     action="categorias",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genre_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film [COLOR orange]- Animazione[/COLOR]",
                     extra="movie",
                     action="peliculas",
                     url="%s/category/film-in-streaming/animazione/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/anime_P.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca Film...[/COLOR]",
                     action="search",
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV [COLOR orange]- Aggiornate[/COLOR]",
                     extra="serie",
                     action="peliculas_tv",
                     url="%s/category/serie-tv-in-streaming/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/tv_serie_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV [COLOR orange]- Ultime Aggiornate[/COLOR]",
                     extra="serie",
                     action="peliculas_update",
                     url="%s/aggiornamenti-serie-tv/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/tv_serie_P.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca Serie TV...[/COLOR]",
                     action="search",
                     extra="serie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png")]

    return itemlist

# ==================================================================================================================================================
	
def categorias(item):
    logger.info("[streamondemand-pureita.cinemalibero] categorias")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = '<li><small>[^>]+><a href="(.*?)">(.*?)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        if scrapedtitle.startswith(("Anime Giapponesi")):
            continue
        if scrapedtitle.startswith(("Serie TV")):
            continue
        scrapedplot = ""
        scrapedthumbnail = ""
        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genre_P.png",
                 folder=True))

    return itemlist

# ==================================================================================================================================================

def search(item, texto):
    logger.info("[streamondemand-pureita cinemalibero] " + item.url + " search " + texto)
    item.url = host + "/?s=" + texto
    try:
        if item.extra == "movie":
            return peliculas(item)
        if item.extra == "serie":
            return peliculas_tv(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

# ==================================================================================================================================================

def peliculas(item):
    logger.info("[streamondemand-pureita.cinemalibero] peliculas")
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
        scrapedtitle=scrapedtitle.replace("[", "(").replace("]", ")")
        if voto:
           voto=" ([COLOR yellow]" + voto + "[/COLOR])"
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="findvideos_movie" if not "serie" in scrapedurl else "episodios",
                 contentType="movie",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]" + voto,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='movie'if not "serie" in scrapedurl else "tv" ))

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
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))

    return itemlist

# ==================================================================================================================================================

def peliculas_tv(item):
    logger.info("[streamondemand-pureita cinemalibero] peliculas_tv")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = '<a href="([^"]+)" title="[^"]+" alt="[^"]+" class="locandina" style[^h]+([^\)]+)[^>]+>[^>]+>([^<]+)<\/div><div class[^>]+>([^<]+)'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, voto, scrapedtitle in matches:
        scrapedplot = ""
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        if voto:
           voto=" ([COLOR yellow]" + voto + "[/COLOR])"
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="episodios",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]" + voto,
                 url=scrapedurl.strip(),
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='tv'))

    # Extrae el paginador
    patronvideos = '<a class="next page-numbers" href="(.*?)">'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="peliculas_tv",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))

    return itemlist

# ==================================================================================================================================================

def peliculas_update(item):
    logger.info("[streamondemand-pureita cinemalibero] peliculas_update")
    itemlist = []
    numpage = 14
	
    p = 1
    if '{}' in item.url:
        item.url, p = item.url.split('{}')
        p = int(p)
	
    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = '<a href="([^"]+)" title="[^"]+" alt="[^"]+" class="locandina" style[^h]+([^\)]+)[^>]+>[^>]+>([^<]+)<\/div><div class[^>]+>([^<]+)'
    matches = re.compile(patron, re.DOTALL).findall(data)


    for i, (scrapedurl, scrapedthumbnail, scrapedtitle, episodio) in enumerate(matches):
        if (p - 1) * numpage > i: continue
        if i >= p * numpage: break
        scrapedplot = ""
        episodio = episodio.replace("(", "").replace(")", "").replace("iTA", "- ITA")
        scrapedtitle =scrapedtitle.replace("(SubITA)", "").strip()
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="episodios" if not "film" in scrapedtitle else "findvideos_movie",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + " ([COLOR yellow]" + episodio + "[/COLOR])",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
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
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))

    return itemlist

# ==================================================================================================================================================

def episodios(item):
    logger.info("[streamondemand-pureita cinemalibero] episodios")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data
    blocco = scrapertools.get_match(data, '<section id="content">(.*?)<div class="wprc-form">')

    patron = '>(.*?)\/a>(?:</p>|)<'
    matches = re.compile(patron, re.DOTALL).findall(blocco)
    scrapertools.printMatches(matches)

    for puntata in matches:
        scrapedtitle=scrapertools.find_single_match(puntata, '([^<]+)<a\s*href="[^"]+"')
		
        if "<u>DOWNLOAD:</u>" in blocco:
          return findvideos_movie(item)

        if "/i>" in scrapedtitle:
		 scrapedtitle=scrapertools.find_single_match(puntata, '([^<]+)<i>[^>]+><a\s*href="[^"]+"')
		 		
        if "Stagione" in scrapedtitle:
          scrapedtitle = "[COLOR yellow]" + scrapedtitle + "[/COLOR]" 			 
        scrapedtitle = scrapedtitle.replace("p>", "").replace("/span>", "")
        scrapedtitle = scrapedtitle.replace("-", "").replace("–", "").replace("/a>", "").replace("br />", "")
        scrapedtitle = scrapedtitle.replace("/strong>", "").replace("</strong></span>", "")

        if "Stagione Completa" in scrapedtitle or "STAGIONE COMPLETA" in scrapedtitle:
		 continue		
        if "Cartella" in puntata or "Cartelle" in puntata:
		 continue		
        if scrapedtitle.startswith(" &#8211;"):
           continue
        if "Extended" in blocco or "By_" in blocco or "by_gemini" in blocco or "a>-" in scrapedtitle:
           continue
        if scrapedtitle=="":
           continue	
		
        itemlist.append(
            Item(channel=__channel__,
                 action="episodios_all" if not "lipwatching" in blocco else "play",
                 fulltitle=item.fulltitle + " - " + scrapedtitle,
                 show=item.show + " - " + scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=puntata,
                 thumbnail=item.thumbnail,
                 plot="[COLOR orange][B]" + item.fulltitle + "[/B][/COLOR]  " + item.plot,
                 folder=True))

    patron = '>(.*?)<\/a>(?:</p>|)<'
    matches = re.compile(patron, re.DOTALL).findall(blocco)
    scrapertools.printMatches(matches)
				 
    for puntata in matches:
        scrapedtitle=scrapertools.find_single_match(puntata, '\/>([^<]+)<a href="[^"]+\s*" target="_blank" rel="noopener" class="external">[^>]+<')
        if "Extended" in blocco:
          scrapedtitle=scrapertools.find_single_match(puntata, '<a href="[^"]+" target="_blank" .*?>([^<]+)')
          scrapedtitle=scrapedtitle.replace("-", " / ")
          if "Easybytez" in scrapedtitle:
            scrapedtitle=scrapertools.find_single_match(puntata, '<span class="txt_dow">([^<]+)</span><br />')	
          if scrapedtitle.startswith("Vidto"):
            scrapedtitle=scrapertools.find_single_match(puntata, 'href="[^"]+" rel="nofollow external">([^<]+)')

          if scrapedtitle.startswith("EB") or scrapedtitle.startswith("AKVideo"):
             continue
			 
        if "Piece" in item.title:
          scrapedtitle=scrapertools.find_single_match(puntata, 'target="_blank[^>]+>([^<]+)')
          if scrapedtitle.startswith("Vidto"):
            scrapedtitle=scrapertools.find_single_match(puntata, 'href="[^"]+" rel="nofollow external">([^<]+)')			
		  
        if "By_" in blocco:
          scrapedtitle=scrapertools.find_single_match(puntata, '<a href="[^"]+" target="_blank" rel="noopener" class="external">([^<]+)')
          if "Easybytez" in scrapedtitle:
            continue		  
        if "by_gemini" in puntata:
          scrapedtitle=scrapertools.find_single_match(puntata, '<a href="[^"]+" target="_blank" class="external">([^<]+)')					   
				   
        if "Stagione" in scrapedtitle:
           scrapedtitle = "[COLOR yellow]" + scrapedtitle + "[/COLOR]"
		   
        scrapedtitle = scrapedtitle.replace("p>", "").replace("/span>", "")
        scrapedtitle = scrapedtitle.replace("-", "").replace("–", "")
        scrapedtitle = scrapedtitle.replace("/strong>", "").replace("</strong></span>", "")
		
        if scrapedtitle.startswith(" &#8211;"):
           continue		
        if "Stagione Completa" in scrapedtitle or "STAGIONE COMPLETA" in scrapedtitle:
		 continue
        if "Cartella" in puntata or "Cartelle" in puntata:
		 continue		
        if "a>-" in scrapedtitle:
           continue
        if scrapedtitle=="":
           continue	
        itemlist.append(
            Item(channel=__channel__,
                 action="episodios_all" if not "lipwatching" in blocco or ")" in scrapedtitle else "play",
                 fulltitle=item.fulltitle + " - " + scrapedtitle,
                 show=item.show + " - " + scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=puntata,
                 thumbnail=item.thumbnail,
                 plot="[COLOR orange][B]" + item.fulltitle + "[/B][/COLOR]  " + item.plot,
                 folder=True))
				 
    return itemlist
# ==================================================================================================================================================

def episodios_all(item):
    logger.info("[streamondemand-pureita cinemalibero] episodios_all")
    itemlist = []

    patron = 'href="([^"]+)"[^>]+>([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(item.url)

    for scrapedurl,scrapedserver in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 fulltitle=item.fulltitle,
                 show=item.show,
                 title="[COLOR azure][[COLOR orange]" + scrapedserver + "[/COLOR]] - " + item.title + "[/COLOR]",
                 url=scrapedurl.strip(),
                 thumbnail=item.thumbnail,
                 plot=item.plot,
                 folder=True))
				 
    return itemlist
	
# ==================================================================================================================================================
	
def findvideos_movie(item):
    logger.info("[streamondemand-pureita cinemalibero] findvideos_movies")
    itemlist = []
	
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)

    # The categories are the options for the combo
    patron = ' <a href="([^"]+)\s*" target="_blank" [^>]+>([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        if "Parte" in scrapedtitle:
          continue
        scrapedthumbnail = ""
        scrapedplot = ""
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 fulltitle=item.fulltitle,
                 show=item.show,
                 title="[COLOR azure][[COLOR orange]" + scrapedtitle + "[/COLOR]] - " + item.title + "[/COLOR]",
                 url=scrapedurl.strip(),
                 thumbnail=item.thumbnail,
                 plot=item.plot,
                 folder=True))
				 
    patron = '<a href="([^"]+)\s*" target="_blank">([^<]+)<\/a><br \/>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        if "Parte" in scrapedtitle:
          continue
        scrapedthumbnail = ""
        scrapedplot = ""
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 fulltitle=item.fulltitle,
                 show=item.show,
                 title="[COLOR azure][[COLOR orange]" + scrapedtitle + "[/COLOR]] - " + item.title + "[/COLOR]",
                 url=scrapedurl.strip(),
                 thumbnail=item.thumbnail,
                 plot=item.plot,
                 folder=True))
				 				 
    return itemlist

# ==================================================================================================================================================
	
def play(item):
    itemlist=[]

    data = item.url

    if "rapidcrypt" in item.url:
       data = httptools.downloadpage(item.url).data
	  
    while 'vcrypt' in item.url:
        item.url = httptools.downloadpage(item.url, only_headers=True, follow_redirects=False).headers.get("location")
        data = item.url
		
    #logger.debug(data)

    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        servername = re.sub(r'[-\[\]\s]+', '', videoitem.title)
        videoitem.title = "".join(['[COLOR azure][[COLOR orange]' + servername.capitalize() + '[/COLOR]] - ', item.fulltitle])
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.plot = item.plot
        videoitem.channel = __channel__

    return itemlist	
	
# ==================================================================================================================================================
