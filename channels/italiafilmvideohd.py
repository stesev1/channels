# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# StreamOnDemand-PureITA / XBMC Plugin
# Canal para italiafilmvideohd
# http://www.mimediacenter.info/foro/viewtopic.php?f=36&t=7808
# ------------------------------------------------------------
import base64
import re
import urlparse

from core import config
from core import httptools
from core import logger
from core import scrapertools
from core.item import Item
from core.tmdb import infoSod
from servers import servertools

__channel__ = "italiafilmvideohd"
host = "https://italiafilm.network/"

headers = [['User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:44.0) Gecko/20100101 Firefox/44.0'],
           ['Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'],
           ['Accept-Encoding', 'gzip, deflate'],
           ['Referer', host],
           ['Cache-Control', 'max-age=0']]


def isGeneric():
    return True


def mainlist(item):
    logger.info("[italiafilmvideohd.py] mainlist")

    itemlist = [
        Item(channel=__channel__,
             title="[COLOR azure]Film[COLOR orange] - Al Cinema[/COLOR]",
             action="fichas",
             url=host + "/cinema/",
             thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/popcorn_cinema_P.png"),
        Item(channel=__channel__,
             title="[COLOR azure]Film[COLOR orange] - Novita'[/COLOR]",
             action="fichas",
             url=host + "/film-hd/",
             thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/movie_new_P.png"),
        Item(channel=__channel__,
             title="[COLOR azure]Film[COLOR orange] - HD[/COLOR]",
             action="fichas",
             url=host + "/nuove-uscite/",
             thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/movie_new_P.png"),
        Item(channel=__channel__,
             title="[COLOR azure]Film[COLOR orange] - Categorie[/COLOR]",
             action="genere",
             url=host,
             thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genres_P.png"),
        Item(channel=__channel__,
             title="[COLOR azure]Serie TV [COLOR orange]- Aggiornate[/COLOR]",
             action="fichas_tv",
             url=host + "/serie-tv-hd/",
             thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/tv_serie_P.png"),
        Item(channel=__channel__,
             title="[COLOR azure]Film & Serie TV [COLOR orange]- Popolari[/COLOR]",
             action="fichas",
             url=host + "/film-piu-popolari/",
             thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/tv_serie_P.png"),
        Item(channel=__channel__,
             title="[COLOR azure]Film & Serie TV [COLOR orange]- Piu' Votati[/COLOR]",
             action="fichas",
             url=host + "/film-piu-votati/",
             thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/tv_serie_P.png"),
        Item(channel=__channel__,
             title="[COLOR orange]Cerca...[/COLOR]",
             action="search",
             thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png")]

    return itemlist

# ===================================================================================================================================================
	
def search(item, texto):
    logger.info("[italiafilmvideohd.py] " + item.url + " search " + texto)

    item.url = host + "/?s=" + texto

    try:
        return fichas(item)

    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

# ===================================================================================================================================================

def genere(item):
    logger.info("[italiafilmvideohd.py] genere")
    itemlist = []

    data = scrapertools.anti_cloudflare(item.url, headers)

    patron = '<div class="sub_title">Genere</div>(.+?)</div>'
    data = scrapertools.find_single_match(data, patron)

    patron = '<li>.*?'
    patron += 'href="([^"]+)".*?'
    patron += '<i>([^"]+)</i>'

    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedtitle in matches:
        scrapedtitle = scrapedtitle.replace('&amp;', '-')
        itemlist.append(
            Item(channel=__channel__,
                 action="fichas",
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail='https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genre_P.png',
                 folder=True))

    return itemlist

# ===================================================================================================================================================

def fichas(item):
    logger.info("[italiafilmvideohd.py] fichas")

    itemlist = []

    # Descarga la pagina
    data = scrapertools.anti_cloudflare(item.url, headers)
    # fix - calidad

    # ------------------------------------------------
    cookies = ""
    matches = re.compile('(.italiafilm.video.*?)\n', re.DOTALL).findall(config.get_cookie_data())
    for cookie in matches:
        name = cookie.split('\t')[5]
        value = cookie.split('\t')[6]
        cookies += name + "=" + value + ";"
    headers.append(['Cookie', cookies[:-1]])
    import urllib
    _headers = urllib.urlencode(dict(headers))
    # ------------------------------------------------

    patron = '<li class="item">.*?href="([^"]+)".*?'
    patron += 'title="([^"]+)".*?<img src="([^"]+)".*?'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scraped_2, scrapedtitle, scrapedthumbnail in matches:
        scrapedurl = scraped_2
        if "serie" in scraped_2:
		 scrapedtitle= scrapedtitle + " [COLOR orange](Serie TV)[/COLOR]"
        title = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedthumbnail += "|" + _headers
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos_all" if not "serie" in scrapedurl else "episodios",
                 title=title,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=title,
                 show=scrapedtitle), tipo='movie' if not "serie" in scrapedurl else "tv"))

    # Paginación
    next_page = scrapertools.find_single_match(data, '<a href="([^"]+)"\s*><span aria-hidden="true">&raquo;')

    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="fichas",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=next_page,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png"))

    return itemlist

# ===================================================================================================================================================

def fichas_tv(item):
    logger.info("[seriehd.py] fichas")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data

    patron = '<a class="poster" href="([^"]+)" title="(.*?)">\s*'
    patron += '<img src="([^"]+)" alt=".*?" />'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, scrapedthumbnail  in matches:
        scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle).strip()
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 fulltitle=scrapedtitle,
                 url=scrapedurl,
                 show=scrapedtitle,
                 thumbnail=scrapedthumbnail), tipo='tv'))

    patron = '<a href="([^"]+)"\s*><span aria-hidden="true">&raquo;'
    next_page = scrapertools.find_single_match(data, patron)
    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="fichas_tv",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=next_page,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png"))

    return itemlist

# ===================================================================================================================================================

def episodios(item):
    logger.info("[seriehd.py] episodios")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data
    patron = r'<iframe width=".+?" height=".+?" src="([^"]+)" allowfullscreen frameborder="0">'
    url = scrapertools.find_single_match(data, patron).replace("?italiafilm", "")

    data = httptools.downloadpage(url).data.replace('\n', '').replace(' class="active"', '')


    section_stagione = scrapertools.find_single_match(data, '<h3>STAGIONE</h3>\s*<ul>(.*?)</ul>')
    patron = '<li[^>]+><a href="([^"]+)">(\d+)<'
    seasons = re.compile(patron, re.DOTALL).findall(section_stagione)

    for scrapedseason_url, scrapedseason in seasons:

        season_url = urlparse.urljoin(url, scrapedseason_url)
        data = httptools.downloadpage(season_url).data.replace('\n', '').replace(' class="active"', '')

        section_episodio = scrapertools.find_single_match(data, '<h3>EPISODIO</h3>\s*<ul>(.*?)</ul>')
        patron = '<li><a href="([^"]+)">(\d+)<'
        episodes = re.compile(patron, re.DOTALL).findall(section_episodio)

        for scrapedepisode_url, scrapedepisode in episodes:
            episode_url = urlparse.urljoin(url, scrapedepisode_url)

            title = scrapedseason + "x" + scrapedepisode.zfill(2)

            itemlist.append(
                Item(channel=__channel__,
                     action="findvideos_tv",
                     contentType="episode",
                     title=title + " - " + item.show,
                     url=episode_url, 
                     fulltitle=title,
                     show=item.show,
                     plot=item.plot,
                     thumbnail=item.thumbnail))


    return itemlist

# ===================================================================================================================================================
	
def findvideos_tv(item):
    logger.info("[seriehd.py] findvideos")

    itemlist = []

    # Descarga la página
    data = httptools.downloadpage(item.url, headers=headers).data.replace('\n', '')

    patron = r'<iframe id="iframeVid" width=".*?" height=".*?" src="([^"]+)" allowfullscreen=""></iframe>'
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
        for res_url, res_video in scrapertools.find_multiple_matches(res, '<option.*?value="([^"]+?)">([^<]+?)</option>'):

            data = httptools.downloadpage(urlparse.urljoin(url, res_url), headers=headers).data.replace('\n', '')

            mir = scrapertools.find_single_match(data, patron_mir)

            for mir_url in scrapertools.find_multiple_matches(mir, '<option.*?value="([^"]+?)">[^<]+?</value>'):

                data = httptools.downloadpage(urlparse.urljoin(url, mir_url), headers=headers).data.replace('\n', '')

                for media_label, media_url in re.compile(patron_media).findall(data):
                    urls.append(url_decode(media_url))

        itemlist = servertools.find_video_items(data='\n'.join(urls))
        for videoitem in itemlist:
            videoitem.title = item.title + "[COLOR orange]" + videoitem.title + "[/COLOR]"
            videoitem.fulltitle = item.fulltitle
            videoitem.thumbnail = item.thumbnail
            videoitem.show = item.show
            videoitem.plot = item.plot
            videoitem.channel = __channel__

    return itemlist
	
# ===================================================================================================================================================
	
def findvideos(item):
    logger.info("[italiafilmvideohd.py] findvideos")

    itemlist = []

    # Descarga la página
    data = scrapertools.anti_cloudflare(item.url, headers).replace('\n', '')

    patron = r'<iframe width=".+?" height=".+?" src="([^"]+)" allowfullscreen frameborder="0">'
    url = scrapertools.find_single_match(data, patron).replace("?italiafilm", "")

    if 'hdpass' in url:
        data = scrapertools.cache_page(url, headers=headers)

        start = data.find('<div class="row mobileRes">')
        end = data.find('<div id="playerFront">', start)
        data = data[start:end]

        patron_res = r'<div class="row mobileRes">([\s\S]*)<\/div>'
        patron_mir = r'<div class="row mobileMirrs">([\s\S]*)<\/div>'
        patron_media = r'<input type="hidden" name="urlEmbed" data-mirror="([^"]+)" id="urlEmbed" value="([^"]+)"[^>]+>'

        res = scrapertools.find_single_match(data, patron_res)

        urls = []
        for res_url, res_video in scrapertools.find_multiple_matches(res, '<option.*?value="([^"]+?)">([^<]+?)</option>'):

            data = scrapertools.cache_page(urlparse.urljoin(url, res_url), headers=headers).replace('\n', '')

            mir = scrapertools.find_single_match(data, patron_mir)

            for mir_url in scrapertools.find_multiple_matches(mir, '<option.*?value="([^"]+?)">[^<]+?</value>'):

                data = scrapertools.cache_page(urlparse.urljoin(url, mir_url), headers=headers).replace('\n', '')

                for media_label, media_url in re.compile(patron_media).findall(data):
                    urls.append(url_decode(media_url))

        itemlist = servertools.find_video_items(data='\n'.join(urls))
        for videoitem in itemlist:
            videoitem.title = item.title + videoitem.title
            videoitem.fulltitle = item.fulltitle
            videoitem.thumbnail = item.thumbnail
            videoitem.show = item.show
            videoitem.plot = item.plot
            videoitem.channel = __channel__

        return itemlist

# ===================================================================================================================================================

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

# ===================================================================================================================================================
	
def findvideos_all(item):
    logger.info("[streamondemand-pureita italiafilmvideohd] findvideos_all")
    itemlist = []

    # Descarga la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data


    patron = '<iframe width=".*?" height=".*?" src="([^"]+)" width=".*?" height=".*?" frameborder=".*?" scrolling=".*?" allowfullscreen /></iframe></div>'
    matches = re.compile(patron, re.DOTALL).findall(data)
	
    for scrapedurl in matches:
        data = httptools.downloadpage(scrapedurl).data
        videos = servertools.find_video_items(data=data)
        for video in videos:
            itemlist.append(video)
			
    for videoitem in itemlist:
        servername = re.sub(r'[-\[\]\s]+', '', videoitem.title)
        videoitem.title = "[[COLOR orange]" + servername.capitalize() + "[/COLOR]] " + item.title
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__
    return itemlist
