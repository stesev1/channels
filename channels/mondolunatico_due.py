# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# TheGroove360 / XBMC Plugin
# Canale 
# ------------------------------------------------------------
import os
import re
import time
import urllib
import urlparse

from core import httptools
from core import config 
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "mondolunatico_due"
host = "http://mondolunatico.org/"

captcha_url = '%s/pass/CaptchaSecurityImages.php?width=100&height=40&characters=5' % host


def mainlist(item):
    logger.info("[.mondolunatico_due] mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Film - [COLOR orange]Cinema[/COLOR]",
                     action="peliculas",
                     url="%sstream/genre/al-cinema/" % host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/popcorn_cinema_P.png"),
	            Item(channel=__channel__,
                     title="[COLOR azure]Film - [COLOR orange]Novita'[/COLOR]",
                     action="peliculas",
                     url="%sstream/movies/" % host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/hd_movies_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film - [COLOR orange]Anno[/COLOR]",
                     action="cat_years",
                     url="%sstream/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/movie_year_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film & Serie TV - [COLOR orange]Categorie[/COLOR]",
                     action="categorias",
                     url="%sstream/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genres_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV - [COLOR orange]Aggiornate[/COLOR]",
                     action="peliculas_tv",
                     extra="serie",
                     url="%sstream/tvshows/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/new_tvshows_P.png"),
                Item(channel=__channel__,
                     title="[COLOR orange]Cerca Serie...[/COLOR]",
                     action="search",
                     extra="serie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca ...[/COLOR]",
                     action="search",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png")]

    return itemlist


# ==================================================================================================================================================
	
def categorias(item):
    logger.info("[.mondolunatico_due] categorias")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url).data
    bloque = scrapertools.get_match(data, '<h2>Film Per Genere</h2>(.*?)</li></ul></nav></div>')

    # Extrae las entradas
    patron = '<li[^>]+><a href="([^"]+)"[^>]>([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:

        if "*" in scrapedtitle:
               scrapedtitle = "[COLOR orange]" + scrapedtitle + "[/COLOR]"
        if "&" in scrapedtitle or "Mystery" in scrapedtitle or "Kids" in scrapedtitle:
               scrapedtitle = scrapedtitle + " ([COLOR orange]Film & Serie TV[/COLOR])"
        else:
               scrapedtitle = "[COLOR azure]" + scrapedtitle + "[/COLOR]"	
        if "Download" in scrapedtitle or "Al Cinema" in scrapedtitle or "Reality" in scrapedtitle or "History" in scrapedtitle:
               continue
        scrapedtitle=scrapedtitle.replace("televisione film", "Film TV").replace("*", "").strip()
        scrapedtitle=scrapedtitle.replace("Richieste", "Film piu' Richiesti").replace("SubITA", "Film Sub-ITA").strip()     		  
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genre_P.png",
                 folder=True))

    return itemlist

# ==================================================================================================================================================
	
def cat_years(item):
    logger.info("[.mondolunatico_due] years")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url).data
    bloque = scrapertools.get_match(data, '<h2>Release year</h2>(.*?)</li></ul></nav></div>')

    # Extrae las entradas 
    patron = '<li><a href="([^"]+)">(.*?)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
         
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/movie_year_P.png",
                 folder=True))

    return itemlist

# ==================================================================================================================================================

def search(item, texto):
    logger.info("[.mondolunatico_due] " + item.url + " search " + texto)
    item.url = host + "stream/?s=" + texto
    try:
        #if item.extra == "movie":
            return pelis_src(item)
    # Continua la ricerca in caso di errore 
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

# ==================================================================================================================================================
		
def pelis_src(item):
    logger.info("[streamondemand-pureita mondolunatico_new] pelis_src")
    itemlist = []
    numpage = 14

    p = 1
    if '{}' in item.url:
        item.url, p = item.url.split('{}')
        p = int(p)
		
    # Descarga la pagina 
    data = httptools.downloadpage(item.url).data

    # Estrae i contenuti 
    patron = '<div class="thumbnail animation-2">\s*<a href="([^"]+)">\s*<img src="([^"]+)" alt="(.*?)" />.*?'
    patron += '<span class="rating">([^<]+)<\/span>.*?'
    patron += '<span class="year">([^<]+)</span>.*?'
    patron += '<div class="contenido">\s*<p>([^"]+)</p>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for i, (scrapedurl, scrapedthumbnail, scrapedtitle, rating, year, scrapedplot) in enumerate(matches):
        if (p - 1) * numpage > i: continue
        if i >= p * numpage: break
        title = scrapertools.decodeHtmlentities(scrapedtitle)

        rating=rating.replace("IMDb ", "")
        rating=" ([COLOR yellow]" + rating + "[/COLOR])"
        if year:
           date = " (" + year + ")"
           years=" ([COLOR yellow]" + year + "[/COLOR])"
        if year in scrapedtitle:
          years =""
          date=""
        if "tvshows" in scrapedurl:
          type=" ([COLOR yellow]Serie TV[/COLOR])"
        else:
          type=""		
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="episodios" if "tvshows" in scrapedurl else "findvideos",
                 title="[COLOR azure]" + title + "[/COLOR]" + type + years + rating,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 fulltitle=title + date,
                 show=title,
                 folder=True), tipo="tv" if "tvshows" in scrapedurl else "movie"))

    # Extrae el paginador
    if len(matches) >= p * numpage:
        scrapedurl = item.url + '{}' + str(p + 1)
        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="pelis_src",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))
				 
    else:
         next_page = scrapertools.find_single_match(data, '<a href="([^"]+)" ><span class="icon-chevron-right">')
         if next_page != "":
             itemlist.append(
                 Item(channel=__channel__,
                      action="pelis_src",
                      title="[COLOR orange]Successivi >>[/COLOR]",
                      url=next_page,
                      thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png"))	

    return itemlist

# ==================================================================================================================================================

def peliculas(item):
    logger.info("[streamondemand-pureita mondolunatico_new] peliculas")
    itemlist = []
    numpage = 14

    p = 1
    if '{}' in item.url:
        item.url, p = item.url.split('{}')
        p = int(p)

    # Descarga la pagina
    data = httptools.downloadpage(item.url).data

    # Extrae las entradas
    patron = '<div class="poster">\s*<img src="([^"]+)" \s*alt="([^"]+)">\s*'
    patron += '<div[^>]+>[^>]+></span>\s*([^<]+)<\/div>\s*[^>]+>\s*[^>]+>(.*?)<.*?'
    patron += 'a href="([^"]+)">[^>]+><\/div><\/a>.*?<\/a>\s*<\/h3>\s*<span>([^<]+)<\/span>.*?'
    patron += '<div class="texto">(.*?)</div>'
    matches = re.compile(patron, re.DOTALL).findall(data)


    for i, (scrapedthumbnail, scrapedtitle, rating, quality, scrapedurl, year, scrapedplot ) in enumerate(matches):
        if (p - 1) * numpage > i: continue
        if i >= p * numpage: break
        scrapedtitle = scrapedtitle.replace("+", "piu").replace("&#038;", "e")
        if "Fichier" in scrapedtitle or "***" in scrapedtitle:
          continue
		  
        if quality ==" ":
           quality=""
        if quality:
          quality=quality.replace(".", " ").strip()
          quality = " ([COLOR yellow]" + quality + "[/COLOR])"
        else:
          quality=""
		  
        if rating =="0":
           rating="" 
        if rating:
          rating=rating.replace(",", ".").strip()
          rating = " ([COLOR yellow]" + rating + "[/COLOR])"
        else:
          rating=""  
		  
        if year:
          years = " ([COLOR yellow]" + year + "[/COLOR])"
          date =" ("+year+")"  		  
        else:
          years =""
          date =""
        if year in scrapedtitle:
          years =""
          date=""  
        title = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="episodios" if "tvshows" in scrapedurl else "findvideos",
                 contentType="tv" if "tvshows" in scrapedurl else "movie",
                 title="[COLOR azure]" + title + "[/COLOR]" + years + quality + rating,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=title + date,
                 show=title,
                 plot=scrapedplot,
                 folder=True), tipo="tv" if "tvshows" in scrapedurl else "movie"))
				 			 

    # Extrae el paginador
    if len(matches) >= p * numpage:
        scrapedurl = item.url + '{}' + str(p + 1)
        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="peliculas",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))
				 
    else:
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

def peliculas_list(item):
    logger.info("[streamondemand-pureita mondolunatico_new] peliculas_list")
    itemlist = []
    numpage = 14
	
    p = 1
    if '{}' in item.url:
        item.url, p = item.url.split('{}')
        p = int(p)

    # Descarga la pagina
    data = httptools.downloadpage(item.url).data

    # Estrae i contenuti 
    patron = '<b><a href="([^"]+)">([^<]+)<\/a></li></b><br>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    scrapedthumbnail = ""
    scrapedplot = ""
    for i, (scrapedurl, scrapedtitle) in enumerate(matches):
        if (p - 1) * numpage > i: continue
        if i >= p * numpage: break
        title = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="episodios",
                 contentType="tv",
                 title="[COLOR azure]" + title + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=title,
                 show=title,
                 plot=scrapedplot,
                 folder=True), tipo='tv'))
				 
    # Extrae el paginador
    if len(matches) >= p * numpage:
        scrapedurl = item.url + '{}' + str(p + 1)
        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="peliculas_list",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))

    return itemlist

# ==================================================================================================================================================	

def peliculas_tv(item):
    logger.info("[streamondemand-pureita mondolunatico_new] peliculas_tv")
    itemlist = []
    numpage = 14
	
    p = 1
    if '{}' in item.url:
        item.url, p = item.url.split('{}')
        p = int(p)

    # Descarga la pagina
    data = httptools.downloadpage(item.url).data

    # Extrae las entradas
    patron = '<div class="poster">\s*<img src="([^"]+)" \s*'
    patron += 'alt="([^"]+)">\s*<div[^>]+>[^>]+><\/span>\s*([^<]+)<\/div>\s*'
    patron += '[^>]+>\s*<\/div>\s*<a href="([^"]+)">.*?'
    patron += '<\/h3>\s*<span>([^<]+)<\/span>.*?<div class="texto">(.*?)<'
    matches = re.compile(patron, re.DOTALL).findall(data)


    for i, (scrapedthumbnail, scrapedtitle, rating, scrapedurl, year, scrapedplot ) in enumerate(matches):
        if (p - 1) * numpage > i: continue
        if i >= p * numpage: break
        scrapedtitle=scrapedtitle.replace("(Cliccate La Scheda Info per vedere i link)", "")
        scrapedtitle=scrapedtitle.replace("&#8217;", "'").replace("Flash", "The Flash").strip()

        title = scrapertools.decodeHtmlentities(scrapedtitle)

        if rating =="0":
           rating="" 
        if rating:
           rating=" ([COLOR yellow]" + rating + "[/COLOR])"
        else:
           rating=""
        if year:
          years = " ([COLOR yellow]" + year + "[/COLOR])"
          date =" ("+year+")"  		  
        else:
          years =""
          date =""
        if year in scrapedtitle:
          years =""
          date=""    
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="episodios",
                 contentType="tv",
                 title="[COLOR azure]" + title + "[/COLOR]" + years + rating,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=title + date,
                 show=title,
                 plot=scrapedplot,
                 folder=True), tipo='tv'))

    # Extrae el paginador
    if len(matches) >= p * numpage:
        scrapedurl = item.url + '{}' + str(p + 1)
        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="peliculas_tv",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))
				 
    else:
         next_page = scrapertools.find_single_match(data, '<a href="([^"]+)" ><span class="icon-chevron-right">')
         if next_page != "":
             itemlist.append(
                 Item(channel=__channel__,
                      action="peliculas_tv",
                      title="[COLOR orange]Successivi >>[/COLOR]",
                      url=next_page,
                      thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png"))	

    return itemlist
	
# ==================================================================================================================================================
	
def episodios(item):
    logger.info("streamondemand.mondolunatico_new episodios")

    itemlist = []

    # Descarga la pagina 
    data = httptools.downloadpage(item.url).data

    html = []

    for i in range(2):
        patron = 'href="(https?://www\.keeplinks\.co/p92/([^"]+))"'
        matches = re.compile(patron, re.DOTALL).findall(data)
        for keeplinks, id in matches:
            _headers = [['Cookie', 'flag[' + id + ']=1; defaults=1; nopopatall=' + str(int(time.time()))],
                        ['Referer', keeplinks]]

            html.append(httptools.downloadpage(keeplinks, headers=_headers).data)

        patron = r'="(%s/pass/index\.php\?ID=[^"]+)"' % host
        matches = re.compile(patron, re.DOTALL).findall(data)
        for scrapedurl in matches:
            tmp = httptools.downloadpage(scrapedurl).data

            if 'CaptchaSecurityImages.php' in tmp:
                # Descarga el captcha
                img_content = httptools.downloadpage(captcha_url).data

                captcha_fname = os.path.join(config.get_data_path(), __channel__ + "captcha.img")
                with open(captcha_fname, 'wb') as ff:
                    ff.write(img_content)

                from platformcode import captcha

                keyb = captcha.Keyboard(heading='', captcha=captcha_fname)
                keyb.doModal()
                if keyb.isConfirmed():
                    captcha_text = keyb.getText()
                    post_data = urllib.urlencode({'submit1': 'Invia', 'security_code': captcha_text})
                    tmp = httptools.downloadpage(scrapedurl, post=post_data).data

                try:
                    os.remove(captcha_fname)
                except:
                    pass

            html.append(tmp)

        data = '\n'.join(html)

    encontrados = set()

    patron = '<p><a href="([^"]+?)">([^<]+?)</a></p>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedtitle in matches:
        if "mondolunatico.org/goto" in scrapedtitle:
           scrapedtitle="Lista episodi in Fase di Ripristino >>"
        else:
           scrapedtitle = scrapedtitle.split('/')[-1]
        if not scrapedtitle or scrapedtitle in encontrados: continue
        encontrados.add(scrapedtitle)
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle).title()
        scrapedtitle=scrapedtitle.replace(".-.", " ").replace("Mkv", "").replace(".", " ").replace("Mp4", "").replace("Ac3", "").replace("Soft","")
        scrapedtitle=scrapedtitle.replace("By Bloody", "").replace("Avi", "").replace("Xvid", "").replace("Dvdrip", "").replace("_"," ").replace("Spft","")
        scrapedtitle=scrapedtitle.replace("Internal", "").replace("%2520", " ").replace("Html", "").replace("Dvdrip", "").strip()
        if "=" in scrapedtitle:
           continue

        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="findvideos",
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=item.thumbnail,
                 fulltitle=item.fulltitle,
                 plot=item.plot,
                 show=item.show))

    patron = '<a href="([^"]+)" target="_blank" class="selecttext live">([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedtitle in matches:
        if "mondolunatico.org/goto" in scrapedtitle:
           scrapedtitle="Lista Episodi in Fase di Ripristino >>"
        else:
           scrapedtitle = scrapedtitle.split('/')[-1]
        if not scrapedtitle or scrapedtitle in encontrados: continue
        encontrados.add(scrapedtitle)
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle).title()

        scrapedtitle=scrapedtitle.replace(".-.", " ").replace("Mkv", "").replace(".", " ").replace("Mp4", "").replace("Ac3", "").replace("_"," ")
        scrapedtitle=scrapedtitle.replace("By Bloody", "").replace("Avi", "").replace("Xvid", "").replace("Dvdrip-", "").replace("Soft-", "").replace("Spft-","")
        scrapedtitle=scrapedtitle.replace("Internal", "").replace("%2520", " ").replace("Html", "").replace("Dvdrip", "").strip()
        if "=" in scrapedtitle:
           continue

        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="findvideos",
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=item.thumbnail,
                 fulltitle=item.fulltitle,
                 plot=item.plot,
                 show=item.show))


    return itemlist

# ==================================================================================================================================================
	
def findvideos_tv(item):
    logger.info("[streamondemand-pureita mondolunatico_new] findvideos_tv")
    itemlist = []

    # Descarga la pagina 
    data = item.url if item.extra == 'serie' else httptools.downloadpage(item.url).data

    # Estrae i contenuti 
    patron = r'noshade>(.*?)<br>.*?<a href="(%s/pass/index\.php\?ID=[^"]+)"' % host
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedtitle, scrapedurl in matches:
        scrapedtitle = scrapedtitle.replace('*', '').replace('Streaming', '').strip()
        title = '%s - [%s]' % (scrapedtitle, item.title)
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 title="[[COLOR orange]" + scrapedtitle + "[/COLOR]] -" + item.title,
                 url=scrapedurl,
                 thumbnail=item.thumbnail,
                 fulltitle=item.fulltitle,
                 show=item.show,
                 server='captcha',
                 folder=False))

    patron = 'href="(%s/stream/links/\d+/)"' % host
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl in matches:
        data += httptools.downloadpage(scrapedurl).data

    ### robalo fix obfuscator - start ####

    patron = 'href="(https?://www\.keeplinks\.(?:co|eu)/p92/([^"]+))"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for keeplinks, id in matches:
        headers = [['Cookie', 'flag[' + id + ']=1; defaults=1; nopopatall=' + str(int(time.time()))],
                   ['Referer', keeplinks]]

        html = httptools.downloadpage(keeplinks, headers=headers).data
        data += str(scrapertools.find_multiple_matches(html, '</lable><a href="([^"]+)" target="_blank"'))

    ### robalo fix obfuscator - end ####

    patron = 'src="([^"]+)" frameborder="0"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl in matches:
        data += httptools.downloadpage(scrapedurl).data

    for videoitem in servertools.find_video_items(data=data):
        servername = re.sub(r'[-\[\]\s]+', '', videoitem.title)
        videoitem.title = "".join(['[[COLOR orange]' + servername.capitalize() + '[/COLOR]] - ', item.title])
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.show = item.show
        videoitem.plot = item.plot
        videoitem.channel = __channel__
        itemlist.append(videoitem)

    return itemlist

# ==================================================================================================================================================

def findvideos(item):
    logger.info("[streamondemand-pureita mondolunatico_new] findvideos")
	
    # Descarga la pagina 
    data = httptools.downloadpage(item.url).data
	
    patron = '<li id=[^=]+="dooplay_player_option[^=]+="([^"]+)" data-nume="([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)
	
    for id, serv  in matches:
        base = "%sstream/wp-admin/admin-ajax.php" % host
        player = urllib.urlencode({'action': 'doo_player_ajax', 'post': id, 'nume': serv})
        data += httptools.downloadpage(base, post=player).data
        
    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        servername = re.sub(r'[-\[\]\s]+', '', videoitem.title)
        videoitem.title = "".join(['[[COLOR orange]' + servername.capitalize() + '[/COLOR]] - ', item.title])
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.plot = item.plot
        videoitem.channel = __channel__

    return itemlist

# ==================================================================================================================================================	
	
def play(item):
    logger.info("[streamondemand-pureita mondolunatico_new] play")
    itemlist = []

    if item.server == 'captcha':
        headers = [['Referer', item.url]]

        # Descarga la pagina 
        data = httptools.downloadpage(item.url, headers=headers).data

        if 'CaptchaSecurityImages.php' in data:
            # Descarga el captcha
            img_content = httptools.downloadpage(captcha_url, headers=headers).data

            captcha_fname = os.path.join(config.get_data_path(), __channel__ + "captcha.img")
            with open(captcha_fname, 'wb') as ff:
                ff.write(img_content)

            from platformcode import captcha

            keyb = captcha.Keyboard(heading='', captcha=captcha_fname)
            keyb.doModal()
            if keyb.isConfirmed():
                captcha_text = keyb.getText()
                post_data = urllib.urlencode({'submit1': 'Invia', 'security_code': captcha_text})
                data = httptools.downloadpage(item.url, post=post_data, headers=headers).data

            try:
                os.remove(captcha_fname)
            except:
                pass

        itemlist.extend(servertools.find_video_items(data=data))

        for videoitem in itemlist:
            videoitem.title = item.title
            videoitem.fulltitle = item.fulltitle
            videoitem.thumbnail = item.thumbnail
            videoitem.show = item.show
            videoitem.plot = item.plot
            videoitem.channel = __channel__
    else:
        itemlist.append(item)

    return itemlist

# ==================================================================================================================================================
# ==================================================================================================================================================
# ==================================================================================================================================================
	
def findvideos_movie(item):
    itemlist = []
	
    data = httptools.downloadpage(item.url).data

    itemlist.extend(servertools.find_video_items(data=data))
    for videoitem in itemlist:
        servername = re.sub(r'[-\[\]\s]+', '', videoitem.title)
        videoitem.title = "".join(['[[COLOR orange]' + servername.capitalize() + '[/COLOR]] - ', item.title])
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.plot = item.plot
        videoitem.channel = __channel__

    return itemlist

# ==================================================================================================================================================	
	
def findvideos_x(item):
    logger.info("[streamondemand-pureita mondolunatico_new] findvideos_x")

    itemlist = []

    # Descarga la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data

    # Estrae i contenuti 
    patron = 'src="([^"]+)" frameborder="0"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl in matches:
        if "dir?" in scrapedurl:
            data += httptools.downloadpage(scrapedurl).url
        else:
            data += httptools.downloadpage(scrapedurl).data

    for videoitem in servertools.find_video_items(data=data):
        videoitem.title = "".join(['[COLOR orange]' + videoitem.title + ' [COLOR azure]- ' + item.title+ '[/COLOR]'])
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.show = item.show
        videoitem.plot = item.plot
        videoitem.channel = __channel__
        itemlist.append(videoitem)

    return itemlist

	
