# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand-pureita / XBMC Plugin
# Canale Tantifilm
# http://www.mimediacenter.info/foro/viewtopic.php?f=36&t=7808
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


__channel__ = "tantifilm"
host = "https://www.tantifilm.gratis"

headers = [['User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:38.0) Gecko/20100101 Firefox/38.0'],
           ['Accept-Encoding', 'gzip, deflate'],
           ['Referer', host]]


def mainlist(item):
    logger.info("[streamondemand-pureita tantifilm] mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Film - [COLOR orange]Menu' >>>[/COLOR]",
                     action="menu_movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/popcorn_new.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film - [COLOR orange]Novita'[/COLOR]",
                     action="peliculas",
                     url="%s/watch-genre/al-cinema/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/movie_new_P.png"),
	            Item(channel=__channel__,
                     title="[COLOR azure]Film - [COLOR orange]Ultimi inseriti[/COLOR]",
                     action="peliculas_last",
                     url="%s/film/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/movies_P.png"),
	            Item(channel=__channel__,
                     title="[COLOR azure]Serie TV - [COLOR orange]Menu' >>>[/COLOR]",
                     action="menu_tvshow",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/popcorn_new.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV - [COLOR orange]Novita[/COLOR]",
                     extra="series",
                     action="peliculas_tv",
                     url="%s/watch-genre/series-tv-featured/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/new_tvshows_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV - [COLOR orange]Ultimi Episodi[/COLOR]",
                     extra="series",
                     action="peliculas_series",
                     url="%s/aggiornamenti-giornalieri-serie-tv-2/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/new_tvshows_P.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow][I]Cerca ...[/I][/COLOR]",
                     action="search",
                     extra="series",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png")]

    return itemlist

# ==================================================================================================================================================

def menu_movie(item):
    logger.info("[streamondemand-pureita tantifilm] menu_movie")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Film - [COLOR orange]Al Cinema[/COLOR]",
                     action="peliculas",
                     url="%s/watch-genre/al-cinema/" % host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/popcorn_cinema_P.png"),
	            Item(channel=__channel__,
                     title="[COLOR azure]Film - [COLOR orange]Ultimi inseriti[/COLOR]",
                     action="peliculas_last",
                     url="%s/film/" % host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/movie_new_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film - [COLOR orange]Alta Definizione[/COLOR]",
                     action="peliculas",
                     url="%s/watch-genre/altadefinizione/" % host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/hd_movies_P.png"),
                Item(channel=__channel__,	 
                     title="[COLOR azure]Film - [COLOR orange]3D[/COLOR]",
                     action="peliculas",
                     url="%s/watch-genre/3d/" % host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/movie_3D_P.png"),
                Item(channel=__channel__,	 
                     title="[COLOR azure]Film - [COLOR orange]Sub-ITA[/COLOR]",
                     action="peliculas",
                     url="%s/watch-genre/sub-ita/" % host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/movie_sub_P.png"),
	            Item(channel=__channel__,
                     title="[COLOR azure]Film - [COLOR orange]Categorie[/COLOR]",
                     action="categorias",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genres_P.png"),
               Item(channel=__channel__,
                     title="[COLOR yellow][I]Cerca ...[/I][/COLOR]",
                     action="search",
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png")]


    return itemlist

# ==================================================================================================================================================

def menu_tvshow(item):
    logger.info("[streamondemand-pureita tantifilm] menu_tvshow")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Serie TV - [COLOR orange]Aggiornamenti per data[/COLOR]",
                     extra="series",
                     action="cat_date",
                     url="%s/aggiornamenti-giornalieri-serie-tv-2/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/new_tvshows_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV - [COLOR orange]Ultime Episodi[/COLOR]",
                     extra="anime",
                     action="peliculas_series",
                     url="%s/aggiornamenti-giornalieri-serie-tv-2/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/new_tvshows_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV - [COLOR orange]Novita'[/COLOR]",
                     extra="series",
                     action="peliculas_tv",
                     url="%s/watch-genre/series-tv-featured/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/new_tvshows_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV - [COLOR orange]HD[/COLOR]",
                     extra="series",
                     action="peliculas_tv",
                     url="%s/watch-genre/serie-altadefinizione/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/tv_series_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV - [COLOR orange]Mini Serie[/COLOR]",
                     extra="series",
                     action="peliculas_tv",
                     url="%s/watch-genre/miniserie/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/tv_series_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Anime - [COLOR orange]Novita'[/COLOR]",
                     extra="anime",
                     action="peliculas_tv",
                     url="%s/watch-genre/anime/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/animation_P.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow][I]Cerca...[/I][/COLOR]",
                     action="search",
                     extra="series",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png")]

    return itemlist

# ==================================================================================================================================================
	
def categorias(item):
    logger.info("[streamondemand-pureita tantifilm] categorias")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url).data
    bloque = scrapertools.get_match(data, '</span>Anime</a></li>(.*?)</ul>')

    # Extrae las entradas
    patron = "<li><a href='(.*?)'><span></span>(.*?)</a>"
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        if "Serie" in scrapedtitle or "Miniserie" in scrapedtitle:
               continue
         
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genre_P.png",
                 folder=True))

    return itemlist

# ==================================================================================================================================================

def peliculas(item):
    logger.info("[streamondemand-pureita tantifilm] peliculas")
    itemlist = []

    # Descarga la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data
	

    patron = '<div class="mediaWrap mediaWrapAlt"><a href="([^"]+)">'
    patron += '<img[^>]+src="([^"]+)"\s*class[^>]+[^>]+></a><div[^>]+>[^>]+><p>([^<]+)</p>'
    patron += '.*?<p>\s*([^<]+)\s*</p>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle, quality in matches:
        if not "http" in scrapedthumbnail:
          scrapedthumbnail = "https:" + scrapedthumbnail
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedtitle=scrapedtitle.replace("streaming", "")
        if quality:
           quality=" ([COLOR yellow]" + quality.strip() + "[/COLOR])"
           quality=quality.replace("HD720", "HD")
        else:
           quality=""
        scrapedplot = ""
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 contentType="movie",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]" + quality,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=scrapedtitle,
                 plot=scrapedplot,
                 show=scrapedtitle), tipo="movie"))

    # Paginación
    next_page = scrapertools.find_single_match(data, '<a class="nextpostslink" rel="next" href="([^"]+)">»</a>')
    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=next_page,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png"))

    return itemlist


# ==================================================================================================================================================

def peliculas_last(item):
    logger.info("[streamondemand-pureita tantifilm] peliculas_last")
    itemlist = []

    # Descarga la pagina 
    data = httptools.downloadpage(item.url).data
    bloque = scrapertools.get_match(data, 'Ultimi Film</h1>(.*?)<h3>Navigation</h3>')
	

    patron = '<img width="\d+" height="\d+" src="([^"]+)" class=[^>]+>\s*'
    patron += '<\/a>\s*<div class="title-film">\s*<a href="([^"]+)" title[^>]+>'
    patron += '<p>([^<]+)<\/p>.*?<p>\s*([^<]+)<\/p>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedthumbnail, scrapedurl, scrapedtitle, quality in matches:
        if not "http" in scrapedthumbnail:
          scrapedthumbnail = "https:" + scrapedthumbnail
        scrapedthumbnail=scrapedthumbnail.replace("’", "%E2%80%99").replace("-–-", "-%E2%80%93-")
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedtitle=scrapedtitle.replace("streaming", "")
        scrapedplot = ""
        if quality:
           quality ="([COLOR yellow]" + quality.strip() + "[/COLOR])"
           quality = quality.replace("HD720", "HD")
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 contentType="movie",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]" + quality,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=scrapedtitle,
                 plot=scrapedplot,
                 show=scrapedtitle), tipo="movie"))

    # Paginación
    next_page = scrapertools.find_single_match(data, '<a class="nextpostslink" rel="next" href="([^"]+)">»</a>')
    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=next_page,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png"))

    return itemlist


# ==================================================================================================================================================

def cat_date(item):
    logger.info("[streamondemand-pureita tantifilm] cat_date")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url).data


    # Extrae las entradas
    patron = '<div class="sp-head" title="Expand">\s*([^<]+)\s*</div>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedtitle in matches:
        if "Serie" in scrapedtitle or "Miniserie" in scrapedtitle:
               continue
         
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_series",
                 title="[COLOR yellow]" + scrapedtitle + "[/COLOR]",
                 url=item.url,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 extra="date",
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/new_tvshows_P.png",
                 folder=True))

    return itemlist

# ==================================================================================================================================================

def peliculas_series(item):
    logger.info("[streamondemand-pureita tantifilm] peliculas_series")
    itemlist = []
    minpage = 28

    p = 1
    if '{}' in item.url:
        item.url, p = item.url.split('{}')
        p = int(p)
		
    # Descarga la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data
    bloque = scrapertools.get_match(data, '%s(.*?)</div>\s*</div>' % item.fulltitle)
	
    patron = '<p>([^<]+)<a href="([^"]+)" target="_blank" rel="noopener">([^<]+)<\/a><\/p>'
    if item.extra=="date":
       matches = re.compile(patron, re.DOTALL).findall(bloque)
    else:
       matches = re.compile(patron, re.DOTALL).findall(data)


    for i, (scrapedtitle, scrapedurl, ep) in enumerate(matches):
        if (p - 1) * minpage > i: continue
        if i >= p * minpage: break

        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedtitle=scrapedtitle.replace("streaming –", "").replace("’", "'")
        scrapedtitle=scrapedtitle.replace("-)", ")")
        scrapedititle=scrapedtitle.strip()
        ep=" ([COLOR orange]" + ep + "[/COLOR])"
        scrapedplot = ""
        scrapedthumbnail = ""
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 contentType="tv",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]" + ep,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle), tipo='tv'))

    # Extrae el paginador
    if len(matches) >= p * minpage:
        scrapedurl = item.url + '{}' + str(p + 1)
        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="peliculas_series",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))

    return itemlist

# ==================================================================================================================================================

def peliculas_tv(item):
    logger.info("[streamondemand-pureita tantifilm] peliculas_tv")
    itemlist = []

    # Descarga la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data
	

    patron = '<div class="mediaWrap mediaWrapAlt"><a href="([^"]+)">'
    patron += '<img[^>]+src="([^"]+)"\s*class[^>]+[^>]+></a><div[^>]+>[^>]+><p>([^<]+)</p>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
	
        if not "https:" in scrapedthumbnail:
          scrapedthumbnail = "".join(['http:', scrapedthumbnail])        
        scrapedthumbnail = scrapedthumbnail.replace("’", "%E2%80%99").replace("-–-", "-%E2%80%93-")
		
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedtitle=scrapedtitle.replace("streaming", "").replace("’", "'")
        scrapedtitle=scrapedtitle.replace("-)", ")").replace("–", "-")
        scrapedplot = ""
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios" if not "anime" in item.extra else "episodios_anime",
                 contentType="tv",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 extra=item.extra,
                 fulltitle=scrapedtitle,
                 plot=scrapedplot,
                 show=scrapedtitle), tipo="tv"))

    # Paginación
    next_page = scrapertools.find_single_match(data, '<a class="nextpostslink" rel="next" href="([^"]+)">»</a>')
    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_tv",
                 extra=item.extra,
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=next_page,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png"))

    return itemlist

# ==================================================================================================================================================

# ==================================================================================================================================================

def search(item, texto):
    logger.info("[streamondemand-pureita tantifilm] " + item.url + " search " + texto)
    item.url = host + "/?s=" + texto

    try:
       return peliculas_search(item)


    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
		
# ==================================================================================================================================================

def peliculas_search(item):
    logger.info("[streamondemand-pureita tantifilm] peliculas_search")
    itemlist = []

    # Descarga la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data
	

    patron = '<div class=".*?genre-(.*?)"\s*id[^>]+>\s*[^>]+>.*?'
    patron += '<a href="([^"]+)"\s*title="(.*?)"\s*rel="bookmark">\s*<img[^>]+src="([^"]+)"[^>]+>.*?<p>(.*?)<\/p>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for type, scrapedurl, scrapedtitle, scrapedthumbnail, scrapedplot in matches:
        if not "http:" in scrapedthumbnail:
         scrapedthumbnail = "https:" + scrapedthumbnail
        scrapedthumbnail=scrapertools.decodeHtmlentities(scrapedthumbnail)
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedtitle=scrapedtitle.replace("streaming", "")
        scrapedtitle=scrapedtitle.replace("Permalink to", "")
        scrapedtitle = scrapedtitle.replace("-)", ")").replace("’", "'").replace("–", "-")
        #scrapedplot = ""
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos" if not "serie" in type else "episodios",
                 contentType="movie" if not "serie" in type else "tv",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=scrapedtitle,
                 plot=scrapedplot,
                 show=scrapedtitle), tipo="movie" if not "serie" in type else "tv"))

    return itemlist

# ==================================================================================================================================================

def episodios(item):
    def load_episodios(html, item, itemlist):
        for data in html.splitlines():
            # Extrae las entradas
            end = data.find('<a ')
            if end > 0:
                scrapedtitle = re.sub(r'<[^>]*>', '', data[:end]).strip()
            else:
                scrapedtitle = ''
            if scrapedtitle == '':
                patron = '<a\s*href="[^"]+"(?:\s*target="_blank)?>([^<]+)</a>'
                scrapedtitle = scrapertools.find_single_match(data, patron).strip()
            title = scrapertools.find_single_match(scrapedtitle, '\d+[^\d]+\d+')
            if title == '':
                title = scrapedtitle.replace("–", "")
            if title != '':
                itemlist.append(
                    Item(channel=__channel__,
                         action="findvideos_tv",
                         title="[COLOR azure]" + title + "[/COLOR]",
                         url=item.url,
                         thumbnail=item.thumbnail,
                         extra=data,
                         fulltitle=title + " - " + item.fulltitle,
                         plot= "[COLOR orange]" + item.fulltitle + "[/COLOR]  " + item.plot,
                         show=title + " - " + item.show))

    logger.info("[streamondemand-pureita tantifilm] episodios")
	

    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data
    data = scrapertools.decodeHtmlentities(data)

    start = data.find('<div class="sp-wrap sp-wrap-blue">')
    end = data.find('<div id="disqus_thread">', start)

    data_sub = data[start:end]

    starts = []
    patron = r".*?Stagione|STAGIONE|MINISERIE|WEBSERIE|SERIE"
    matches = re.compile(patron, re.IGNORECASE).finditer(data_sub)
    for match in matches:
        season_title = match.group()
        if season_title != '':
            starts.append(match.end())

    i = 1
    len_starts = len(starts)

    while i <= len_starts:
        inizio = starts[i - 1]
        fine = starts[i] if i < len_starts else -1

        html = data_sub[inizio:fine]

        load_episodios(html, item, itemlist)

        i += 1

    if len(itemlist) == 0:
        patron = '<a href="(#wpwm-tabs-\d+)">([^<]+)</a></li>'
        seasons_episodes = re.compile(patron, re.DOTALL).findall(data)

        end = None
        for scrapedtag, scrapedtitle in seasons_episodes:
            if "Player" in scrapedtitle:
                return episodios_all(item)
            start = data.find(scrapedtag, end)
            end = data.find('<div class="clearfix"></div>', start)
            html = data[start:end]
            scrapedtitle=scrapedtitle.replace("–", "").strip() 
            itemlist.append(
                Item(channel=__channel__,
                     action="findvideos_tv",
                     title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                     url=item.url,
                     thumbnail=item.thumbnail,
                     extra=html,
                     fulltitle=scrapedtitle + " - " + item.fulltitle,
                     plot= "[COLOR orange]" + item.fulltitle + "[/COLOR]  " + item.plot,
                     show=scrapedtitle + " - " + item.show))


    return itemlist

# ==================================================================================================================================================

def episodios_all(item):
    logger.info("[streamondemand-pureita tantifilm] episodios_all")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data
    patron = r'<iframe src="([^"]+)" scrolling="no" frameborder="0" width="626" height="550" allowfullscreen="true" webkitallowfullscreen="true" mozallowfullscreen="true"></iframe>'
    url = scrapertools.find_single_match(data, patron)

    data = httptools.downloadpage(url).data.replace('\n', '')


    section_stagione = scrapertools.find_single_match(data, '<i class="fa fa-home fa-fw"></i> Stagioni</a>(.*?)<select name="sea_select" class="dynamic_select">')
    patron = '<a href="([^"]+)" ><i class="fa fa-tachometer fa-fw"></i>\s*(\d+)</a></li>'
    seasons = re.compile(patron, re.DOTALL).findall(section_stagione)

    for scrapedseason_url, scrapedseason in seasons:

        season_url = urlparse.urljoin(url, scrapedseason_url)
        data = httptools.downloadpage(season_url).data.replace('\n', '')

        section_episodio = scrapertools.find_single_match(data, '<i class="fa fa-home fa-fw"></i> Episodio</a>(.*?)<select name="ep_select" class="dynamic_select">')
        patron = '<a href="([^"]+)" ><i class="fa fa-tachometer fa-fw"></i>\s*(\d+)</a>'
        episodes = re.compile(patron, re.DOTALL).findall(section_episodio)

        for scrapedepisode_url, scrapedepisode in episodes:
            episode_url = urlparse.urljoin(url, scrapedepisode_url)

            title = scrapedseason + "x" + scrapedepisode

            itemlist.append(
                Item(channel=__channel__,
                     action="findvideos_tv",
                     contentType="episode",
                     title="[COLOR azure]" + title  + "[/COLOR]",
                     url=episode_url, 
                     fulltitle=title + " - " + item.fulltitle ,
                     show=title + " - " + item.show,
                     plot="[COLOR orange]" + item.fulltitle + "[/COLOR]  " + item.plot,
                     thumbnail=item.thumbnail))


    return itemlist

# ==================================================================================================================================================

def episodios_anime(item):
    logger.info("[streamondemand-pureita tantifilm] episodios_anime")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data
    if not "Stagione" in data:
      return findvideos(item)
    blocco = scrapertools.get_match(data, '.*?Stagione([^+]+)<\/div>\s*<\/div>\s*<p>')
	

    patron = '(.*?)</a>\s*</p>'
    matches = re.compile(patron, re.DOTALL).findall(blocco)
    scrapertools.printMatches(matches)

    for episode in matches:
        scrapedtitle=scrapertools.find_single_match(episode, '>([^<]+)<a href="[^"]+" target[^>]+>[^<]+')
        if scrapedtitle=="":
          continue
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos_anime",
                 fulltitle=item.fulltitle + " - " + scrapedtitle,
                 show=item.show + " - " + scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=episode,                
                 thumbnail=item.thumbnail,
                 plot="[COLOR orange]" + item.fulltitle + "[/COLOR]  " + item.plot,
                 folder=True))
			 
    patron = '<a class(.*?)<(?:br /|)(?:/p|)>'
    matches = re.compile(patron, re.DOTALL).findall(blocco)
    scrapertools.printMatches(matches)    

    for episode in matches:
        scrapedtitle=scrapertools.find_single_match(episode, 'Episodio\s*([^<]+)')

        if scrapedtitle=="":
          continue
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos_anime",
                 fulltitle=item.fulltitle + " - " + scrapedtitle,
                 show=item.show + " - " + scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=episode,
                 extra="anime",
                 thumbnail=item.thumbnail,
                 plot="[COLOR orange]" + item.fulltitle + "[/COLOR]  " + item.plot,
                 folder=True))
			 
			 
			 
    return itemlist

# ==================================================================================================================================================	

def findvideos_tv(item):
    logger.info("[streamondemand-pureita tantifilm] findvideos_tv")

    # Descarga la página
    data = item.extra if item.extra != '' else scrapertools.cache_page(item.url, headers=headers)

    itemlist = servertools.find_video_items(data=data)
    for videoitem in itemlist:
        servername = re.sub(r'[-\[\]\s]+', '', videoitem.title)
        videoitem.title = "".join(['[COLOR azure][[COLOR orange]' + servername.capitalize()+ '[/COLOR]] - ' +item.title, '[/COLOR]'])
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.plot = item.plot
        videoitem.channel = __channel__
		
    # Extrae las entradas
    patron = r'<a href="([^"]+)" target="_blank[^>]+>([^<]+)'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedtitle in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 title="[COLOR azure][[COLOR orange]" + scrapedtitle + "[/COLOR]] - " + item.title + "[/COLOR]",
                 url=scrapedurl.replace(r'\/', '/').replace('%3B', ';'),
                 thumbnail=item.thumbnail,
                 fulltitle=item.fulltitle,
                 show=item.show,
                 server='',
                 plot=item.plot,
                 folder=False))

    patron = '<a class="post[^"]+" href="([^\/]+\/\/([^.]+)[^"]+)" target="_blank[^>]+>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 title="[COLOR azure][[COLOR orange]" + scrapedtitle + "[/COLOR]] - " + item.title + "[/COLOR]",
                 url=scrapedurl.replace(r'\/', '/').replace('%3B', ';'),
                 thumbnail=item.thumbnail,
                 fulltitle=item.fulltitle,
                 show=item.show,
                 server='',
                 plot=item.plot,
                 folder=False))
				 
    patron = '<a class="" href="[^"]+"><i class="fa fa-home fa-fw"><\/i>([^<]+)<\/a>.*?<iframe src=".*?\/\/.*?=([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedtitle, scrapedurl in matches:
        url = scrapedurl.decode('base64')
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 title="[COLOR azure][[COLOR orange]" + scrapedtitle + "[/COLOR]] - " + item.title + "[/COLOR]",
                 url=url.strip(),
                 fulltitle=item.fulltitle,
                 show=item.show,
                 plot=item.plot,
                 thumbnail=item.thumbnail,
                 folder=True))
				 
    return itemlist

# ==================================================================================================================================================

def findvideos(item):
    logger.info("[streamondemand-pureita tantifilm] findvideos")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = '<div\s*id="wpwm-tabs-(\d+)">\s*<ul class="wpwm-movie-links">\s*[^>]+>\s*[^>]+>\s*<iframe src="(.*?)"[^>]+>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for option, scrapedurl in matches:

        if "protectlink" in scrapedurl:
          scrapedurl=scrapertools.find_single_match(data, '<div\s*id="wpwm-tabs-%s">\s*<ul class="wpwm-movie-links">\s*[^>]+>\s*[^>]+>\s*<iframe src="[^\/]+\/\/[^=]+=([^"]+)"[^>]+>' % option)
          scrapedurl=''.join(scrapedurl.split())
          scrapedurl=scrapedurl.decode("base64")

        scrapedtitle=scrapertools.find_single_match(data, '<li\s*id="wpwm-tabmob[^>]+><a href="#wpwm-tabs-%s">([^<]+)</a></li>' % option)
        if scrapedtitle=="-":
           continue
        if "Player" in scrapedtitle:
           return episodios(item)

        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 fulltitle=item.fulltitle,
                 show=item.show,
                 title="[COLOR azure][[COLOR orange]" + scrapedtitle + "[/COLOR]] - " + item.title,
                 url=scrapedurl.strip(),
                 thumbnail=item.thumbnail,
                 plot=item.plot,
                 folder=True))

    return itemlist
	
# ==================================================================================================================================================

def findvideos_anime(item):
    logger.info("[streamondemand-pureita tantifilm] findvideos_anime")
    itemlist = []

    # Descarga la pagina 

    if "anime" in item.extra:
       patron = 'href="([^\/]+\/\/([^.]+)[^"]+)" target="_blank[^>]+>'
    else:
       patron = 'href="([^"]+)[^>]+>([^<]+)'
    matches = re.compile(patron, re.DOTALL).findall(item.url)

    for scrapedurl, scrapedtitle in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle).capitalize()

        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 contentType="tv",
                 title="[COLOR azure][[COLOR orange]" + scrapedtitle + "[/COLOR]] - " + item.fulltitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=item.thumbnail,
                 fulltitle=scrapedtitle,
                 plot=item.plot,
                 show=scrapedtitle))
				 
    return itemlist

# ==================================================================================================================================================
	
def play(item):
    itemlist=[]
	
    data = item.url
	
    if "rapidcrypt" in item.url  or "flashx" in item.url:
       data = httptools.downloadpage(item.url).data
	   
	  
    while 'nodmca' in item.url or 'vcrypt' in item.url:
        item.url = httptools.downloadpage(item.url, only_headers=True, follow_redirects=False).headers.get("location")
        data = item.url
		
    #logger.debug(data)
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
