# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# StreamOnDemand-PureITA / XBMC Plugin
# Canale Filmpertutti
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

__channel__ = "filmpertutti"
host = "https://www.filmpertutti.uno/"
headers = [['Referer', host]]


def mainlist(item):
    logger.info("streamondemand-pureita.filmpertutti mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Film - [COLOR orange]Prime Visioni[/COLOR]",
                     action="peliculas",
                     extra="movie",
                     url="%s/prime-visioni/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/popcorn_new.png"),
	           Item(channel=__channel__,
                     title="[COLOR azure]Film - [COLOR orange]Novita'[/COLOR]",
                     action="peliculas",
                     extra="movie",
                     url="%s/category/film/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/movie_new_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film - [COLOR orange]Categorie[/COLOR]",
                     action="categorias",
                     extra="movie",
                     url="%s/category/film/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genres_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV - [COLOR orange]Novita'[/COLOR]",
                     extra="serie",
                     action="peliculas_tv",
                     url="%s/category/serie-tv/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/popcorn_new.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV - [COLOR orange]Aggiornamenti[/COLOR]",
                     extra="serie",
                     action="peliculas_update",
                     url="%s/aggiornamenti-serie-tv/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/tv_serie_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV - [COLOR orange]Archivio A-Z[/COLOR]",
                     action="categorias_tvshow",
                     url="%s/category/serie-tv/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/a-z_P.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow][I]Cerca Film...[/I][/COLOR]",
                     action="search",
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow][I]Cerca Serie TV...[/I][/COLOR]",
                     action="search",
                     extra="serie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png")]

    return itemlist

# ==================================================================================================================================================

def peliculas(item):
    logger.info("streamondemand-pureita.filmpertutti peliculas")
    itemlist = []


    # Descarga la pagina
    data = httptools.downloadpage(item.url).data

    # Extrae las entradas (carpetas)
    patron = '<li><a href="([^"]+)" data-thumbnail="([^"]+)"><div>\s*<div class="title">(.*?)</div>\s*<div[^>]+>(.*?)</div>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle, rating in matches:
        if "HD" in scrapedtitle:
          quality = " ([COLOR yellow]HD[/COLOR])"
        else:
          quality = ""
        rating = " ([COLOR yellow]" + rating + "[/COLOR])"
        scrapedtitle=scrapedtitle.replace(" [HD]", "").replace("&#8211;", "-")
        
        scrapedplot = ""
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos_movie",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]" + quality + rating,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 extra=item.extra,
                 folder=True), tipo='movie'))

    # Extrae el paginador
    patronvideos = '<li><a href="([^"]+)" >Pagina successiva &raquo;</a></li>'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])

        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 extra=item.extra,
                 folder=True))

    return itemlist

# ==================================================================================================================================================

def categorias(item):
    logger.info("streamondemand-pureita.filmpertutti categorias")
    itemlist = []

    data = httptools.downloadpage(item.url).data

    # Narrow search by selecting only the combo
    patron = '<option>Scegli per Genere</option>(.*?)</select>'
    bloque = scrapertools.get_match(data, patron)

    # The categories are the options for the combo  
    patron = '<option data-src="([^"]+)">([^<]+)</option>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        scrapedurl = urlparse.urljoin(item.url, scrapedurl)
        scrapedthumbnail = ""
        scrapedplot = ""
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genre_P.png",
                 folder=True))

    return itemlist

# ==================================================================================================================================================

def categorias_tvshow(item):
    logger.info("streamondemand-pureita.filmpertutti categorias")
    itemlist = []

    data = httptools.downloadpage(item.url).data

    # Narrow search by selecting only the combo
    patron = '<select class="cats mobile"><option>Scegli per Genere</option>(.*?)</select>'
    bloque = scrapertools.get_match(data, patron)

    # The categories are the options for the combo  
    patron = '<option data-src="([^"]+)">([^<]+)</option>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        scrapedurl = urlparse.urljoin(item.url, scrapedurl)
        scrapedthumbnail = ""
        scrapedplot = ""
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_tv",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/a-z_P.png",
                 folder=True))

    return itemlist

# ==================================================================================================================================================

def search(item, texto):
    logger.info("streamondemand-pureita.filmpertutti " + item.url + " search " + texto)
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
	
def peliculas_tv(item):
    logger.info("streamondemand-pureita.filmpertutti peliculas")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url).data

    # Extrae las entradas (carpetas)
    patron = '<li><a href="([^"]+)" data-thumbnail="([^"]+)"><div>\s*<div class="title">(.*?)</div>\s*[^>]+>([^<]+)</div>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle, rating in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        if rating:
          rating = " ([COLOR yellow]" + rating + "[/COLOR])"
        if "[HD]" in scrapedtitle:
          lang = " ([COLOR yellow]HD[/COLOR])"
        else:
          lang=""
        scrapedtitle=scrapedtitle.replace("[HD]", "")

        scrapedplot = ""
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]" + lang + rating,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 extra=item.extra,
                 folder=True), tipo='tv'))
		
    # Extrae el paginador
    patronvideos = '<li><a href="([^"]+)" >Pagina successiva &raquo;</a></li>'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_tv",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 extra=item.extra,
                 folder=True))

    return itemlist

# ==================================================================================================================================================

def peliculas_update(item):
    logger.info("streamondemand-pureita.filmpertutti peliculas")
    itemlist = []

    numpage = 14
	
    p = 1
    if '{}' in item.url:
        item.url, p = item.url.split('{}')
        p = int(p)
	
    # Descarga la pagina
    data = httptools.downloadpage(item.url).data

    # Extrae las entradas (carpetas)
    patron = '<li><a\s*href="([^\/]+\/\/[^\/]+\/([^"]+))" data-\s*thumbnail="([^"]+)">'
    patron += '<div>\s*<div class="title">(.*?)<\/div>\s*<div class="episode"[^>]+>(.*?)<\/div>'
    matches = re.compile(patron, re.DOTALL).findall(data)


    for i, (scrapedurl, titolo, scrapedthumbnail, scrapedtitle, episode) in enumerate(matches):

        if (p - 1) * numpage > i: continue
        if i >= p * numpage: break

        if scrapedtitle=="":
           scrapedtitle=titolo.title()
		   
        episode = episode.replace("<br>", " ")
		
        scrapedtitle = scrapedtitle.replace("<br>", " ").replace("&amp;", "e")
        scrapedtitle = scrapedtitle.replace("-", " ").replace("6", "")
        scrapedtitle = scrapedtitle.replace("/", " ").replace("Serie Tv", "")
        scrapedtitle = scrapedtitle.replace("serie tv", "").replace("Serie TV", "")
        scrapedtitle = scrapedtitle.replace("SERIE TV", "")

        scrapedtitle = scrapedtitle.strip()
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)

        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + " ([COLOR yellow]" + episode + "[/COLOR])",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot="",
                 extra=item.extra,
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
    def load_episodios(html, item, itemlist, lang_title):
        patron = '((?:.*?<a\s*href="[^"]+"[^>]+>[^<]+<\/a>)+)'
        matches = re.compile(patron).findall(html)

        for data in matches:
            scrapedtitle = data.split('<a ')[0]
            scrapedtitle = re.sub(r'<[^>]*>', '', scrapedtitle).strip()
            if scrapedtitle != 'Categorie':
                scrapedtitle = scrapedtitle.replace('&#215;', 'x')
                scrapedtitle = scrapedtitle.replace(";", "")
                itemlist.append(
                    Item(channel=__channel__,
                         action="findvideos_tv",
                         contentType="episode",
                         title="[COLOR azure]%s[/COLOR]" % (scrapedtitle + " (" + lang_title + ")"),
                         url=data,
                         thumbnail=item.thumbnail,
                         extra=item.extra,
                         plot="[COLOR orange][B]" + item.show + "[/B][/COLOR] " + item.plot,
                         fulltitle=item.fulltitle +  ' - ' + scrapedtitle + " (" + lang_title + ")",
                         show=item.show +  ' - ' + scrapedtitle + " (" + lang_title + ")"))

    logger.info("[streamondemand-pureita filmpertutti] episodios")
    itemlist = []

    # Descarga la pagina 
    data = httptools.downloadpage(item.url).data
    data = scrapertools.decodeHtmlentities(data)

    lang_titles = []
    starts = []
    patron = r"(?:tagione[^>]+.*?</strong>|)(?:Edizione|).*?"
    matches = re.compile(patron, re.IGNORECASE).finditer(data)
    for match in matches:
        season_title = match.group()
        if season_title != '':
            lang_titles.append('SUB ITA' if 'SUB' in season_title.upper() else 'ITA')
            starts.append(match.end())

    i = 1
    len_lang_titles = len(lang_titles)

    while i <= len_lang_titles:
        inizio = starts[i - 1]
        fine = starts[i] if i < len_lang_titles else -1

        html = data[inizio:fine]
        lang_title = lang_titles[i - 1]

        load_episodios(html, item, itemlist, lang_title)

        i += 1


    return itemlist

# ==================================================================================================================================================
	
def findvideos_tv(item):
    logger.info("[streamondemand-pureita filmpertutti] findvideos_tv")
    itemlist = []

    patron = '<a href="([^"]+)"\s*target="_blank"\s*rel="[^>]+>(?:<strong>|)([^<]+)<\/'

    matches = re.compile(patron, re.DOTALL).findall(item.url)

    for scrapedurl, scrapedtitle in matches:
        scrapedtitle = scrapedtitle.title()
        if "Rapidgator" in scrapedtitle or "Nitroflare" in scrapedtitle or "Rockfile" in scrapedtitle:
         continue
        if "Tu" in scrapedtitle or "Easy" in scrapedtitle or "Nowd" in scrapedtitle:
         continue
        if "Blood" in scrapedtitle or "Mov"in scrapedtitle:
         continue
        itemlist.append(
            Item(
                channel=__channel__,
                action="play",
                fulltitle=item.fulltitle,
                show=item.show,
                title="[COLOR azure]" + item.title + " [[COLOR orange]" + scrapedtitle + "[/COLOR]]",
                url=scrapedurl,
                thumbnail=item.thumbnail,
                plot=item.plot,
                folder=True))

    return itemlist

# ==================================================================================================================================================

def findvideos_movie(item):
    logger.info("[streamondemand-pureita filmpertutti] findvideos_movie")
    itemlist = []

    data = httptools.downloadpage(item.url).data

    # Narrow search by selecting only the combo
    patron = 'Streaming:<(.*?)</div>'
    bloque = scrapertools.get_match(data, patron)

	
    # The categories are the options for the combo
    patron = '<a href="([^"]+)"[^>]+>(?:<strong>|)([^<]+)</'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        scrapedtitle = scrapedtitle.title()
        if "Rapidgator" in scrapedtitle or "Nitroflare" in scrapedtitle or "Rockfile" in scrapedtitle:
         continue
        if "Tu" in scrapedtitle or "Easy" in scrapedtitle or "Nowd" in scrapedtitle:
         continue
        if "Blood" in scrapedtitle or "Mov"in scrapedtitle or "Parte" in scrapedtitle:
         continue
        scrapedthumbnail = ""
        scrapedplot = ""
        scrapedtitle = scrapedtitle.replace("<strong>", "").replace("</strong>", "")
        scrapedtitle = scrapedtitle.title()

        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 title="[COLOR azure][[COLOR orange]" + scrapedtitle + "[/COLOR]] " + item.title,
                 url=scrapedurl,
                 fulltitle=item.fulltitle,
                 show=item.show,
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

    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        videoitem.title = item.title
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.plot = item.plot
        videoitem.channel = __channel__

    return itemlist

# ==================================================================================================================================================
# ==================================================================================================================================================
# ==================================================================================================================================================
'''	
def findvideos(item):
    logger.info("streamondemand-pureita.filmpertutti findvideos")

    # Descarga la página
    data = item.url if item.extra == 'serie' else scrapertools.cache_page(item.url)

    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        videoitem.title = item.title + videoitem.title
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.show = item.show
        videoitem.plot = item.plot
        videoitem.channel = __channel__

    return itemlist
'''