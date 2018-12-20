# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# TheGroove360 / XBMC Plugin
# Canale cb01anime
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

__channel__ = "cb01anime"
host        = "http://www.cineblog01.pink/anime/"
headers     = [['Referer', host]]

# ========================================================================================================================================================
def mainlist(item):
    logger.info("[thegroove360.cb01anime] mainlist")
    itemlist = [Item(channel=__channel__,
                     action="peliculas_new",
                     title="[COLOR azure]Anime[COLOR orange] - Novita'[/COLOR]",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/anime_new_P.png"),
                Item(channel=__channel__,
                     action="genere",
                     title="[COLOR azure]Anime[COLOR orange] - Categorie[/COLOR]",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/anime_genre_P.png"),
                Item(channel=__channel__,
                     action="year",
                     title="[COLOR azure]Anime[COLOR orange] - Anno[/COLOR]",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/anime_year_P.png"),
                Item(channel=__channel__,
                     action="alfabetico",
                     title="[COLOR azure]Anime[COLOR orange] - Lista A-Z[/COLOR]",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/anime_az_P.png"),
                Item(channel=__channel__,
                     action="listacompleta",
                     title="[COLOR azure]Anime[COLOR orange] - Lista[/COLOR]",
                     url="%s/lista-completa-anime-cartoon/" % host,
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/anime_lista_P.png"),
                Item(channel=__channel__,
                     action="search",
                     title="[COLOR yellow]Cerca ...[/COLOR]",
                     extra="anime",
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/search_P.png")]

    return itemlist

# ========================================================================================================================================================

def peliculas_new(item):
    logger.info("[thegroove360.cb01anime] peliculas_new")
    itemlist = []

    # Descarga la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = '<img src="([^"]+)" alt="" width[^>]+><\/a>\s*[^>]+>[^>]+>\s*'
    patron += '[^>]+>\s*[^>]+>\s*[^>]+>[^>]+>\s*<a href="([^"]+)">\s*'
    patron += '<h1>([^<]+)<\/h1><\/a>.*?-->(.*?)<a'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedthumbnail, scrapedurl, scrapedtitle, scrapedplot in matches:
        if "Lista Richieste Up" in scrapedtitle or "Lista Alfabetica" in scrapedtitle:
           continue	
        scrapedplot = scrapedplot.replace("<p><img s", "").replace("<br />", "")
        scrapedplot = scrapedplot.replace("<p><img a", "").replace("<br>", "")		
        scrapedplot = scrapedplot.strip()
        title = scrapedtitle.replace("[", "(").replace("]", ")")
        title = scrapedtitle.replace("Sub Ita", "[COLOR yellow]Sub Ita[/COLOR]")
        title = scrapedtitle.replace("FULL Ita", "[COLOR yellow]Ita[/COLOR]")

	
        itemlist.append(
            Item(channel=__channel__,
                 action="episodios",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + title + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot + "....",
                 folder=True))

    # Extrae el paginador 
    patronvideos = "<link rel='next' href='([^']+)'"
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_new",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/next_1.png",
                 extra=item.extra,
                 folder=True))

    return itemlist

# ========================================================================================================================================================

def genere(item):
    logger.info("[thegroove360.cb01anime] genere")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data

    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data, '<select name="select2"(.*?)</select>')

    # The categories are the options for the combo  
    patron = '<option value="([^"]+)">([^<]+)</option>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)


    for scrapedurl, scrapedtitle in matches:
        scrapedurl = host + scrapedurl
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_new",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/anime_genre_P.png",
                 folder=True))

    return itemlist

# ========================================================================================================================================================

def year(item):
    logger.info("[thegroove360.cb01anime] genere")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data

    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data, 'Anime per Anno</option>(.*?)</select>')

    # The categories are the options for the combo  
    patron = '<option value="([^"]+)">([^<]+)</option>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)


    for scrapedurl, scrapedtitle in matches:
        if "-20??" in scrapedtitle:
          continue
        scrapedurl = host + scrapedurl
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_new",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/anime_year_P.png",
                 folder=True))

    return itemlist

# ========================================================================================================================================================

def alfabetico(item):
    logger.info("[thegroove360.cb01anime] listacompleta")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data

    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data, '<option value=\'-1\'>Anime per Lettera</option>(.*?)</select>')

    # The categories are the options for the combo  
    patron = '<option value="([^"]+)">\(([^<]+)\)</option>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)


    for scrapedurl, scrapedtitle in matches:
        scrapedurl = host + scrapedurl
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_new",
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/a-z_cartoons_P.png",
                 plot="Indice [[COLOR orange]" + scrapedtitle + "[/COLOR]]",
                 folder=True))

    return itemlist

# ========================================================================================================================================================

def listacompleta(item):
    logger.info("[thegroove360.cb01anime] listacompleta")
    itemlist = []

    data = scrapertools.anti_cloudflare(item.url, headers)

    # Narrow search by selecting only the combo
    patron = '<a href="#char_5a" title="Go to the letter Z">Z</a></span></div>(.*?)</ul></div><div style="clear:both;"></div></div>'
    bloque = scrapertools.get_match(data, patron)

    # The categories are the options for the combo  
    patron = '<li><a href="([^"]+)"><span class="head">([^<]+)</span></a></li>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)


    for scrapedurl, scrapedtitle in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="episodios",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/anime_lista_P.png",
                 folder=True))

    return itemlist

# ========================================================================================================================================================

def search(item, texto):
    logger.info("[thegroove360.cb01anime] " + item.url + " search " + texto)

    item.url = host + "?s=" + texto

    return peliculas_new(item)

# ========================================================================================================================================================

def episodios(item):
    logger.info("[thegroove360.cb01anime] episodios")

    itemlist = []

    # Descarga la página
    data = httptools.downloadpage(item.url).data
    data = scrapertools.decodeHtmlentities(data)

    patron1 = '(?:<p>|<td bgcolor="#ECEAE1">)<span class="txt_dow">(.*?)(?:</p>)?(?:\s*</span>)?\s*</td>'
    patron2 = '<a\s*href="([^"]+)"\s*[^>]+.*?>([^<]+)<\/a>'

    matches1 = re.compile(patron1, re.DOTALL).findall(data)
    if len(matches1) > 0:
        for match1 in re.split('<br />|<p>', matches1[0]):
            if len(match1) > 0:
                # Extrae las entradas
                titulo = None
                scrapedurl = ''
                matches2 = re.compile(patron2, re.DOTALL).finditer(match1)
                for match2 in matches2:
                    if titulo is None:
                        titulo = match2.group(2)
                    scrapedurl += match2.group(1) + '#' + match2.group(2) + '|'
                if titulo is not None:
                    title =  "[COLOR orange]" + titulo + "[/COLOR]"
                    if "Easybytez" in title or "Katfile" in title:
                       title= title.replace("Easybytez", "[B]Extra[/B]")

                    itemlist.append(
                        Item(channel=__channel__,
                             action="findvideos",
                             contentType="episode",
                             title=title,
                             extra=scrapedurl,
                             thumbnail=item.thumbnail,
                             fulltitle=item.fulltitle,
                             plot="[COLOR white][B]" + item.fulltitle + "[/COLOR][/B] " + item.plot,
                             show=item.show))
							 
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

    itemlist.sort(key=lambda x: x.title)
    itemlist.reverse()
    return itemlist

# ========================================================================================================================================================

def findvideos(item):
    logger.info("[thegroove360.cb01anime] findvideos")

    itemlist = []

    for match in item.extra.split(r'|'):
        match_split = match.split(r'#')
        scrapedurl = match_split[0]
        if len(scrapedurl) > 0:
            scrapedtitle = match_split[1]
            title = "[[COLOR orange]" + scrapedtitle + "[/COLOR]] " + item.fulltitle
            itemlist.append(
                Item(channel=__channel__,
                     action="play",
                     title=title,
                     url=scrapedurl,
                     fulltitle=item.fulltitle,
                     plot=item.plot,
                     thumbnail=item.thumbnail,
                     show=item.show,
                     folder=False))

    return itemlist

# ========================================================================================================================================================

def play(item):
    logger.info("[thegroove360.cb01anime] play")

    if '/goto/' in item.url:
        item.url = item.url.split('/goto/')[-1].decode('base64')

    item.url = item.url.replace('http://cineblog01.pw', 'http://k4pp4.pw')

    logger.debug("##############################################################")
    if "go.php" in item.url:
        data = scrapertools.anti_cloudflare(item.url, headers)
        try:
            data = scrapertools.get_match(data, 'window.location.href = "([^"]+)";')
        except IndexError:
            try:
                # data = scrapertools.get_match(data, r'<a href="([^"]+)">clicca qui</a>')
                # In alternativa, dato che a volte compare "Clicca qui per proseguire":
                data = scrapertools.get_match(data, r'<a href="([^"]+)".*?class="btn-wrapper">.*?licca.*?</a>')
            except IndexError:
                data = scrapertools.get_header_from_response(item.url, headers=headers, header_to_get="Location")
        while 'vcrypt' in data:
            data = scrapertools.get_header_from_response(data, headers=headers, header_to_get="Location")
        logger.debug("##### play go.php data ##\n%s\n##" % data)
    elif "/link/" in item.url:
        data = scrapertools.anti_cloudflare(item.url, headers)
        from lib import jsunpack

        try:
            data = scrapertools.get_match(data, "(eval\(function\(p,a,c,k,e,d.*?)</script>")
            data = jsunpack.unpack(data)
            logger.debug("##### play /link/ unpack ##\n%s\n##" % data)
        except IndexError:
            logger.debug("##### The content is yet unpacked ##\n%s\n##" % data)

        data = scrapertools.find_single_match(data, 'var link(?:\s)?=(?:\s)?"([^"]+)";')
        while 'vcrypt' in data:
            data = scrapertools.get_header_from_response(data, headers=headers, header_to_get="Location")
        logger.debug("##### play /link/ data ##\n%s\n##" % data)
    else:
        data = item.url
        logger.debug("##### play else data ##\n%s\n##" % data)
    logger.debug("##############################################################")

    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        videoitem.title = videoitem.title + "  -  " + item.show + " - " + item.title
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__

    return itemlist
