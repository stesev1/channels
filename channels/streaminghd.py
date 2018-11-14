# -*-  coding: utf-8  -*-
# ------------------------------------------------------------
# StreamOnDemand-PureITA / XBMC Plugin
# Canale  streaminghd
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

__channel__ = "streaminghd"
host = "https://streaminghd.online"
headers = [['Referer', host]]

def mainlist(item):
    logger.info("streamondemand-pureita streaminghd mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Film [COLOR orange]- Novita'[/COLOR]",
                     action="peliculas",
                     url="%s/film/" % host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/popcorn_cinema_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film [COLOR orange]- Aggiornati[/COLOR]",
                     action="peliculas_new",
                     url="%s/aggiornamenti-film/" % host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/movie_new_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film [COLOR orange]- Top IMDb[/COLOR]",
                     action="peliculas_tmdb",
                     url="%s/piu-votati/" % host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/movie_sub_P.png"),
                #Item(channel=__channel__,
                     #title="[COLOR azure]Film [COLOR orange]- Novita'[/COLOR]",
                     #action="peliculas_update",
                     #url=host,
                     #extra="movie",
                     #thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/movie_new_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film [COLOR orange]- Categorie[/COLOR]",
                     action="categorias",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genres_P.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca Film...[/COLOR]",
                     action="search",
                     url=host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV [COLOR orange]- Aggiornamenti[/COLOR]",
                     action="peliculas_new_tv",
                     url="%s/serietv/aggiornamenti-serie-tv/" % host,
                     extra="serie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/tv_series_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV[/COLOR]",
                     action="peliculas_tv",
                     url="%s/serietv/serie/" % host,
                     extra="serie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/tv_series_P.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca Serie TV...[/COLOR]",
                     action="search",
                     url="%s/serietv/" % host,
                     extra="serie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png")]

    return itemlist

# ==================================================================================================================================================
	
def categorias(item):
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url).data
    bloque = scrapertools.get_match(data, '<h2>Genere</h2>(.*?)</ul>')

    # Extrae las entradas (carpetas)
    patron = '<a href="([^"]+)">([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genre_P.png",
                 folder=True))

    return itemlist

# ==================================================================================================================================================
	
def search(item, texto):
    logger.info("streamondemand-pureita streaminghd " + item.url + " search " + texto)
    
    try:
        if item.extra == "movie":
          item.url = host + "/?s=" + texto
          return peliculas_search(item)
	  
        else:
          item.url = host + "/serietv/?s=" + texto
          return peliculas_search(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

# ==================================================================================================================================================		
		
def peliculas(item):
    logger.info("streamondemand-pureita streaminghd peliculas")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url).data

    # Extrae las entradas (carpetas)
    patron = '<img src="([^"]+)" alt="([^<]+)">\s*<div class="mepo"><span class="quality">\s*([^<]+).*?'
    patron += '</div><div class="rating"><span class="icon-star2"></span>\s*(.*?)</div>\s*'
    patron += '<a href="([^"]+)">.*?</span></div><div class="texto">(.*?)</div>'
    matches = re.compile(patron, re.DOTALL).finditer(data)

    for match in matches:
        scrapedplot = scrapertools.unescape(match.group(6))
        scrapedurl = urlparse.urljoin(item.url, match.group(5))
        votes = scrapertools.unescape(match.group(4))
        quality = scrapertools.unescape(match.group(3))
        scrapedtitle = scrapertools.unescape(match.group(2))
        scrapedthumbnail = urlparse.urljoin(item.url, match.group(1))
        scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)
        if "SUB-ITA" in scrapedtitle or "sub-ita" in scrapedtitle:
           lang= " ([COLOR yellow]Sub-Ita[/COLOR])"
        else:
           lang=""
        if votes:
           votes=" ([COLOR yellow]" + votes.strip() + "[/COLOR])"
        if quality:
           quality =" ([COLOR yellow]" + quality.lower().strip() + "[/COLOR])"

        scrapedtitle = scrapedtitle.replace("’", "'").replace(" &amp; ", " ").replace("[SUN-ITA]", "").strip()
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 contentType="movie",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title=scrapedtitle + lang + quality + votes,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True))

    # Extrae el paginador
    patronvideos = '<a href="([^"]+)"><span class="icon-chevron-right">'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))

    return itemlist

# ==================================================================================================================================================

def peliculas_tmdb(item):
    logger.info("streamondemand-pureita streaminghd peliculas")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url).data

    # Extrae las entradas (carpetas)
    patron = '<img src="([^"]+)" alt="([^<]+)">\s*<div class="mepo"><span class="quality">\s*([^<]+).*?'
    patron += '</div><div class="rating"><span class="icon-star2"></span>\s*(.*?)</div>\s*'
    patron += '<a href="([^"]+)">'
    matches = re.compile(patron, re.DOTALL).finditer(data)

    for match in matches:

        scrapedurl = urlparse.urljoin(item.url, match.group(5))
        votes = scrapertools.unescape(match.group(4))
        quality = scrapertools.unescape(match.group(3))
        scrapedtitle = scrapertools.unescape(match.group(2))
        scrapedthumbnail = urlparse.urljoin(item.url, match.group(1))
        scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)

        if "SUB-ITA" in scrapedtitle or "sub-ita" in scrapedtitle:
           lang= " ([COLOR yellow]Sub-Ita[/COLOR])"
        else:
           lang=""
        if votes:
           votes=" ([COLOR yellow]" + votes.strip() + "[/COLOR])"
        if quality:
           quality =" ([COLOR yellow]" + quality.lower().strip() + "[/COLOR])"

        scrapedtitle = scrapedtitle.replace("’", "'").replace(" &amp; ", " ").replace("[SUN-ITA]", "").strip()
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 contentType="movie",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title=scrapedtitle + quality + votes,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot="",
                 folder=True), tipo='movie'))

				 
    # Extrae el paginador
    patronvideos = '<a href="([^"]+)"><span class="icon-chevron-right">'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))
    return itemlist

# ==================================================================================================================================================
		
def peliculas_new(item):
    logger.info("streamondemand-pureita streaminghd peliculas_new")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url).data

    # Extrae las entradas (carpetas)
    patron = '<img src="([^"]+)">\s*<div class="mepo">\s*[^>]+>([^<]+)</span></div>\s*'
    patron += '<a href="([^"]+)"><div class="see"></div></a>\s*</div><div class[^>]+><h3><a href="[^"]+">([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).finditer(data)

    for match in matches:

        scrapedtitle = scrapertools.unescape(match.group(4))
        scrapedurl = urlparse.urljoin(item.url, match.group(3))
        date = scrapertools.unescape(match.group(2))
        scrapedthumbnail = urlparse.urljoin(item.url, match.group(1))
        scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)
        scrapedtitle = scrapedtitle.replace("’", "'").replace(" &amp; ", " ").replace("&#8217;", "")
        scrapedplot = ""		
        date="  ([COLOR yellow]" + date.strip().lower() + "[/COLOR])"	
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 contentType="movie",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title=scrapedtitle + date,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='movie'))

    # Extrae el paginador
    patronvideos = '<a href="([^"]+)"><span class="icon-chevron-right">'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_new",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))

    return itemlist

# ==================================================================================================================================================

def peliculas_update(item):
    logger.info("streamondemand-pureita streaminghd peliculas_update")

    itemlist = []

    # Descarga la pagina 
    data = httptools.downloadpage(item.url).data
    bloque = scrapertools.get_match(data, '<h2>Ultime Uscite</h2>(.*?)<h2>Films</h2>')	
	
    patron = '<img src="([^"]+)" alt="([^<]+)"><div class="rating"><span class="icon-star2">'
    patron += '</span>\s*([^<]+)</div><div class="featu">.*?</div><a href="([^"]+)">'

    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedthumbnail, scrapedtitle, votes, scrapedurl in matches:
        votes=" [[COLOR yellow]" + votes + "[/COLOR]]"
        if "0" in votes:
         votes ="  [[COLOR yellow]" + "N/A" + "[/COLOR]]"
        scrapedtitle = scrapedtitle.replace("’", "'").replace(" &amp; ", " ").replace("&#8217;", "")
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 contentType="movie",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title=scrapedtitle + votes,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 folder=True))


    next_page = scrapertools.find_single_match(data, '<a href="([^"]+)" ><span class="icon-chevron-right">')
    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=next_page,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png"))

    return itemlist

# ==================================================================================================================================================	

def peliculas_tv(item):
    logger.info("streamondemand-pureita streaminghd peliculas")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url).data

    # Extrae las entradas (carpetas)
    patron = '<img src="([^"]+)" alt="([^<]+)">\s*<div class="mepo"><span class="quality">\s*([^<]+).*?'
    patron += '</div><div class="rating"><span class="icon-star2"></span>\s*(.*?)</div>\s*<a href="([^"]+)">.*?'
    patron += '<\/h3>[^>]+>[^>]+>[^>]+>([^<]+)<\/span>.*?</span></div><div class="texto">(.*?)</div>'
    matches = re.compile(patron, re.DOTALL).finditer(data)

    for match in matches:
        scrapedplot = scrapertools.unescape(match.group(7))
        year = scrapertools.unescape(match.group(6))
        scrapedurl = urlparse.urljoin(item.url, match.group(5))
        votes = scrapertools.unescape(match.group(4))
        quality = scrapertools.unescape(match.group(3))
        scrapedtitle = scrapertools.unescape(match.group(2))
        scrapedthumbnail = urlparse.urljoin(item.url, match.group(1))
        scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)

        if votes:
           votes=" ([COLOR yellow]" + votes.strip() + "[/COLOR])"
        if quality:
           quality =" ([COLOR yellow]" + quality.strip() + "[/COLOR])"
        if year:
           year =" ([COLOR yellow]" + year.strip() + "[/COLOR])"
        scrapedtitle = scrapedtitle.replace("’", "'").replace(" &amp; ", " ").replace("&#8217;", "")
        itemlist.append(
            Item(channel=__channel__,
                 action="episodios",
                 contentType="tv",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title=scrapedtitle + year + quality + votes,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True))

    # Extrae el paginador
    patronvideos = '<a href="([^"]+)"><span class="icon-chevron-right">'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_tv",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))

    return itemlist
				 
# ==================================================================================================================================================

def peliculas_new_tv(item):
    logger.info("streamondemand-pureita streaminghd peliculas")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url).data

    # Extrae las entradas (carpetas)
    patron = '<img src="([^"]+)" alt="[^>]+">.*?<div class="rating"><span class="icon-star2">'
    patron += '<\/span>\s*([^<]+)<\/div>.*?[^>]+>.*?<span class="quality">([^<]+).*?<a\s*href="([^"]+)">([^<]+)<\/a><\/h3>\s*<span>([^<]+)<\/span>'
    matches = re.compile(patron, re.DOTALL).finditer(data)

    for match in matches:
        scrapedplot = ""
        date = scrapertools.unescape(match.group(6))
        scrapedtitle = scrapertools.unescape(match.group(5))
        scrapedurl = scrapertools.unescape(match.group(4))
        quality = scrapertools.unescape(match.group(3))
        scrapedep = scrapertools.unescape(match.group(2))
        scrapedthumbnail = urlparse.urljoin(item.url, match.group(1))
        scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)
        scrapedep=scrapedep.replace("[sub-ita]", "- Sub").replace("[ita]", "")
        scrapedep=" ([COLOR yellow]" + scrapedep.strip() + "[/COLOR])"
        if quality:
           quality =" ([COLOR yellow]" + quality.strip() + "[/COLOR])"
        if date:
           date =" ([COLOR orange][I]" + date.strip() + "[/I][/COLOR] )"

        scrapedtitle = scrapedtitle.replace("’", "'").replace(" &amp; ", " ").replace("&#8217;", "")
        itemlist.append(
            Item(channel=__channel__,
                 action="episodios",
                 contentType="tv",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title=scrapedtitle + scrapedep + quality + date,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True))

    # Extrae el paginador
    patronvideos = '<a href="([^"]+)"><span class="icon-chevron-right">'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_tv",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))

    return itemlist
# ==================================================================================================================================================

def peliculas_search(item):
    logger.info("streamondemand-pureita streaminghd peliculas_update")

    itemlist = []

    # Descarga la pagina 
    data = httptools.downloadpage(item.url).data
    #bloque = scrapertools.get_match(data, '<h1>Risultati.*?</h1>(.*?)<div class="sidebar scrolling">')	
	
    patron = '<a href="([^"]+)">\s*<img src="([^"]+)"\s*alt="([^<]+)"\s*\/>'
    patron += '.*?"meta">[^>]+>\s*([^<]+)<\/span>.*?<div class="contenido"><p>(.*?)<\/p>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle, date, scrapedplot  in matches:
        scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)
        scrapedtitle = scrapedtitle.replace("’", "'").replace(" &amp; ", " ").replace("&#8217;", "")
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos" if item.extra == "movie" else "episodios",
                 contentType="movie" if item.extra == "movie" else "tv",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title='[COLOR azure]' + scrapedtitle + ' ([COLOR yellow]' + date + "[/COLOR])",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True))

    return itemlist

# ==================================================================================================================================================
	
def episodios(item):
    logger.info("streamondemand-pureita streaminghd episodios")
    itemlist = []

    data = httptools.downloadpage(item.url).data

    patron = 'src="([^"]+)"></a></div><div class="numerando">([^<]+)'
    patron += '</div><div class="episodiotitle">\s*<a\s*href="([^"]+)">([^<]+)</a>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedthumbnail, scrapedep, scrapedurl, scrapedtitle  in matches:
        scrapedthumbnail = "https:" + scrapedthumbnail
        scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)
        scrapedplot = ""
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 fulltitle=item.fulltitle + " - " + scrapedtitle,
                 show=item.show + " - " + scrapedtitle,
                 title="[COLOR azure]" + scrapedep + " " + scrapedtitle + "[/COLOR]",
                 contentType="episode",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot="[COLOR orange]" + item.fulltitle + "[/COLOR] " + item.plot,
                 folder=True))

    if config.get_library_support() and len(itemlist) != 0:
        itemlist.append(
            Item(channel=__channel__,
                 title="Aggiungi alla libreria",
                 url=item.url,
                 action="add_serie_to_library",
                 extra="episodios",
                 show=item.show))
        itemlist.append(
            Item(channel=__channel__,
                 title="Scarica tutti gli episodi della serie",
                 url=item.url,
                 action="download_all_episodes",
                 extra="episodios",
                 show=item.show))

    return itemlist

# ==================================================================================================================================================	
	
def findvideos(item):

    data = httptools.downloadpage(item.url, headers=headers).data

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



