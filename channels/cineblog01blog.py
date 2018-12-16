# -*- coding: utf-8 -*-
#------------------------------------------------------------
# TheGroove360 - XBMC Plugin
# Channel for Cineblog01.cloud
#------------------------------------------------------------

import urlparse
import urllib2
import re
import sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from core import servertools

__channel__ = "cineblog01blog"
__category__ = "F,S"
__type__ = "generic"
__title__ = "Cineblog01 Cloud"
__language__ = "IT"

sito="https://www.cineblog01.cloud/"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("[thegroove360.cineblog01blog] mainlist")
    itemlist = []
    itemlist.append( Item(channel=__channel__, title="[COLOR azure]Nuovi Film[/COLOR]", action="peliculas", url=sito+"/new-film-streaming/", thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/popcorn_cinema_P.png"))
    itemlist.append( Item(channel=__channel__, title="[COLOR azure]Film Per Genere[/COLOR]", action="categorias", url=sito, thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/genres_P.png"))
    itemlist.append( Item(channel=__channel__, title="[COLOR azure]Film Per Paese[/COLOR]", action="catpays", url=sito , thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/movie_country_P.png"))
    itemlist.append( Item(channel=__channel__, title="[COLOR azure]Film Per Anno[/COLOR]", action="catyear", url=sito, thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/movie_year_P.png"))
    itemlist.append( Item(channel=__channel__, title="[COLOR yellow]Cerca...[/COLOR]", action="search",thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/search_P.png"))
    itemlist.append( Item(channel=__channel__, title="[COLOR azure]Serie TV[/COLOR]", extra="serie", action="peliculas", url=sito+"/telefilm-serie-tv-streaming/", thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/tv_serie_P.png"))
    itemlist.append( Item(channel=__channel__, title="[COLOR yellow]Cerca Serie TV...[/COLOR]", action="search", extra="serie",thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/search_P.png"))
    
    return itemlist

def categorias(item):
    logger.info("[thegroove360.cineblog01blog] categorias")
    itemlist = []
    
    data = scrapertools.cache_page(item.url)
    logger.info(data)

    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data,'<li class="drop"><a href="/" class="link1"><b>Film Streaming </b></a>.*?<ul>(.*?)<li class="drop">')
    
    # The categories are the options for the combo
    patron = '<li><a href="(.*?)">(.*?)</a></li>'
    matches = re.compile(patron,re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for url,titulo in matches:
        scrapedtitle = titulo
        scrapedurl = urlparse.urljoin(item.url,url)
        scrapedthumbnail = "https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/genre_P.png"
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="peliculas" , title="[COLOR azure]"+scrapedtitle+"[/COLOR]" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot))

    return itemlist

def catpays(item):
    logger.info("[thegroove360.cineblog01blog] categorias")
    itemlist = []
    
    data = scrapertools.cache_page(item.url)
    logger.info(data)

    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data,'<li class="drop"><a href="/" class="link1"><b>Film per paese</b></a>(.*?)<li class="drop">')
    
    # The categories are the options for the combo
    patron = '<li><a.*?href="(.*?)">(.*?)</a></li>'
    matches = re.compile(patron,re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for url,titulo in matches:
        scrapedtitle = titulo
        scrapedurl = urlparse.urljoin(item.url,url)
        scrapedthumbnail = "https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/movie_country_P.png"
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="peliculas" ,title="[COLOR azure]"+scrapedtitle+"[/COLOR]" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot, folder=True ))

    return itemlist

def catyear(item):
    logger.info("[thegroove360.cineblog01blog] categorias")
    itemlist = []
    
    data = scrapertools.cache_page(item.url)
    logger.info(data)

    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data,'<li class="drop"><a href="/" class="link1"><b>Film per anno</b></a>(.*?)<li class="drop">')
    
    # The categories are the options for the combo
    patron = '<li><a.*?href="(.*?)">(.*?)</a></li>'
    matches = re.compile(patron,re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for url,titulo in matches:
        scrapedtitle = titulo
        scrapedurl = urlparse.urljoin(item.url,url)
        scrapedthumbnail = "https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/movie_year_P.png"
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="peliculas" , title="[COLOR azure]"+scrapedtitle+"[/COLOR]", url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot, folder=True ))

    return itemlist

def search(item,texto):
    logger.info("[cineblog01blog.py] "+item.url+" search "+texto)
    item.url = "http://www.cineblog01.blog/xfsearch/" + texto
    try:

        if item.extra == "serie":
            item.url = "http://www.cineblog01.blue/xfsearch/" + texto
            return serie_tv(item)
        else:
            item.url = "http://www.cineblog01.blue/xfsearch/" + texto
            return peliculas(item)
    # The exception is caught, so as not to interrupt the global searcher if a channel fails
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []

def peliculas(item):
    logger.info("[thegroove360.cineblog01blog] peliculas")
    itemlist = []

    # Download the page
    data = scrapertools.cache_page(item.url)

    # Extract the entradas (carpetas)
    patron = '<div class="short-story">\s*'
    patron += '<a href="(.*?)" title="(.*?)">\s*'
    patron += '<img.*?:url\((.*?)\)'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle,scrapedthumbnail in matches:
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="episodios" if item.extra == "serie" else "findvideos", title=scrapedtitle, url=scrapedurl , thumbnail=scrapedthumbnail , viewmode="movie_with_plot", fanart=scrapedthumbnail , folder=True ) )


    # Extract the paginador
    patronvideos  = '<span class="nav_ext">...</span> <a href=".*?">.*?</a> <a href="(.*?)">Avanti</a></div></div>'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    if len(matches)>0:
        scrapedurl = urlparse.urljoin(item.url,matches[0])
        itemlist.append( Item(channel=__channel__, extra=item.extra, action="peliculas", title="[COLOR orange]Successivi >>[/COLOR]" , url=scrapedurl , thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/next_1.png", folder=True) )

    return itemlist

def serie_tv(item):
    logger.info("[thegroove360.cineblog01blog] peliculas")
    itemlist = []

    # Download the page
    data = scrapertools.cache_page(item.url)

    # Extract the entries (carpetas)
    patron = '<div class="short-story">\s*'
    patron += '<a href="(.*?)" title="(.*?)">\s*'
    patron += '<img.*?:url\((.*?)\)'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle,scrapedthumbnail in matches:
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="episodios" , title=scrapedtitle, url=scrapedurl , thumbnail=scrapedthumbnail , viewmode="movie_with_plot", fanart=scrapedthumbnail , folder=True ) )


    # Extract the paginador
    patronvideos  = '<span class="nav_ext">...</span> <a href=".*?">.*?</a> <a href="(.*?)">Avanti</a></div></div>'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    if len(matches)>0:
        scrapedurl = urlparse.urljoin(item.url,matches[0])
        itemlist.append( Item(channel=__channel__, extra=item.extra, action="serie_tv", title="[COLOR orange]Successivi >>[/COLOR]" , url=scrapedurl , thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/next_1.png", folder=True) )

    return itemlist

def episodios( item ):
    logger.info( "[cineblog01blog.py] episodios" )

    itemlist = []

    ## Download the page
    data = scrapertools.cache_page( item.url )

    plot = scrapertools.htmlclean(
        scrapertools.get_match( data, '</span></h1></div>(.*?)<td class="full-right">' )
    ).strip()

    ## Extract the data - Episodios
    patron = '<br />(\d+x\d+).*?href="//ads.ad-center.com/[^<]+</a>(.*?)<a href="//ads.ad-center.com/[^<]+</a>'
    matches = re.compile( patron, re.DOTALL ).findall( data )
    if len( matches ) == 0:
        patron = ' />(\d+x\d+)(.*?)<br'
        matches = re.compile( patron, re.DOTALL ).findall( data )

    print "##### episodios matches ## %s ##" % matches

    ## Extract the data - sub ITA/ITA
    patron = '<b>.*?STAGIONE.*?(sub|ITA).*?</b>'
    lang = re.compile( patron, re.IGNORECASE ).findall( data )

    lang_index = 0
    for scrapedepisode, scrapedurls in matches:

        if int( scrapertools.get_match( scrapedepisode, '\d+x(\d+)' ) ) == 1:
            lang_title = lang[lang_index]
            if lang_title.lower() == "sub": lang_title+= " ITA"
            lang_index+= 1

        title = scrapedepisode + " - " + item.show + " (" + lang_title + ")"
        scrapedurls = scrapedurls.replace( "playreplay", "moevideo" )

        matches_urls = re.compile( 'href="([^"]+)"', re.DOTALL ).findall( scrapedurls )
        urls = ""
        for url in matches_urls:
            urls+= url + "|"

        if urls != "":
            itemlist.append( Item( channel=__channel__, action="findvid_series", title=title, url=urls[:-1], thumbnail=item.thumbnail, plot=plot, fulltitle=item.fulltitle, show=item.show ) )

    return itemlist

def findvid_series( item ):
    logger.info( "[cineblog01blog.py] findvideos" )

    itemlist = []

    ## Extract the data
    if "|" not in item.url:
        ## Download the page
        data = scrapertools.cache_page( item.url)

        sources = scrapertools.get_match( data, '(<noindex> <div class="video-player-plugin">.*?</noindex>)')

        patron = 'src="([^"]+)"'
        matches = re.compile( patron, re.DOTALL ).findall( sources )
    else:
        matches = item.url.split( '|' )

    for scrapedurl in matches:

        server = scrapedurl.split( '/' )[2].split( '.' )
        if len(server) == 3: server = server[1]
        else: server = server[0]

        title = "[" + server + "] " + item.fulltitle

        itemlist.append( Item( channel=__channel__, action="play" , title=title, url=scrapedurl, thumbnail=item.thumbnail, fulltitle=item.fulltitle, show=item.show, folder=False ) )

    return itemlist

def play( item ):
    logger.info( "[cineblog01blog.py] play" )

    ## You only need the url
    data = item.url

    itemlist = servertools.find_video_items( data=data )

    for videoitem in itemlist:
        videoitem.title = item.show
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__

    return itemlist
