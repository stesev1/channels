# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# TheGroove360 / XBMC Plugin
# Canale 
# ------------------------------------------------------------

import re

import datetime
import json
import urllib

from core import httptools, tmdb
from platformcode import logger
from core import scrapertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "saghe"

PERPAGE = 20

tmdb_key =  tmdb.tmdb_auth_key #tmdb_key = '92db8778ccb39d825150332b0a46061d'
dttime = (datetime.datetime.utcnow() - datetime.timedelta(hours=5))
systime = dttime.strftime('%Y%m%d%H%M%S%f')
today_date = dttime.strftime('%Y-%m-%d')
month_date = (dttime - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
month2_date = (dttime - datetime.timedelta(days=60)).strftime('%Y-%m-%d')
year_date = (dttime - datetime.timedelta(days=365)).strftime('%Y-%m-%d')
tmdb_image = 'http://image.tmdb.org/t/p/original'
tmdb_poster = 'http://image.tmdb.org/t/p/w500'


def mainlist(item):
    logger.info("Stefano.saghe mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR yellow]The Marvel Universe[/COLOR]",
                     action="tmdb_saghe",
                     url='http://api.themoviedb.org/3/list/50941077760ee35e1500000c?api_key=%s&language=it' % tmdb_key,
                     thumbnail="https://image.tmdb.org/t/p/w180_and_h270_bestv2/6t3KOEUtrIPmmtu1czzt6p2XxJy.jpg"),
                Item(channel=__channel__,
                     title="[COLOR yellow]The DC Comics Universe[/COLOR]",
                     action="tmdb_saghe",
                     url='http://api.themoviedb.org/3/list/5094147819c2955e4c00006a?api_key=%s&language=it' % tmdb_key,
                     thumbnail="https://image.tmdb.org/t/p/w180_and_h270_bestv2/xWlaTLnD8NJMTT9PGOD9z5re1SL.jpg"),
                Item(channel=__channel__,
                     title="[COLOR yellow]iMDb Top 250 Movies[/COLOR]",
                     action="tmdb_saghe",
                     url='http://api.themoviedb.org/3/list/522effe419c2955e9922fcf3?api_key=%s&language=it' % tmdb_key,
                     thumbnail="https://image.tmdb.org/t/p/w180_and_h270_bestv2/9O7gLzmreU0nGkIB6K3BsJbzvNv.jpg"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Rotten Tomatoes top 100 movies of all times[/COLOR]",
                     action="tmdb_saghe",
                     url='http://api.themoviedb.org/3/list/5418c914c3a368462c000020?api_key=%s&language=it' % tmdb_key,
                     thumbnail="https://image.tmdb.org/t/p/w180_and_h270_bestv2/zGadcmcF48gy8rKCX2ubBz2ZlbF.jpg"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Reddit top 250 movies[/COLOR]",
                     action="tmdb_saghe",
                     url='http://api.themoviedb.org/3/list/54924e17c3a3683d070008c8?api_key=%s&language=it' % tmdb_key,
                     thumbnail="https://image.tmdb.org/t/p/w180_and_h270_bestv2/dM2w364MScsjFf8pfMbaWUcWrR.jpg"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Sci-Fi Action[/COLOR]",
                     action="tmdb_saghe",
                     url='http://api.themoviedb.org/3/list/54408e79929fb858d1000052?api_key=%s&language=it' % tmdb_key,
                     thumbnail="https://image.tmdb.org/t/p/w180_and_h270_bestv2/5ig0kdWz5kxR4PHjyCgyI5khCzd.jpg"),
                Item(channel=__channel__,
                     title="[COLOR yellow]007 - Movies[/COLOR]",
                     action="tmdb_saghe",
                     url='http://api.themoviedb.org/3/list/557b152bc3a36840f5000265?api_key=%s&language=it' % tmdb_key,
                     thumbnail="https://image.tmdb.org/t/p/w180_and_h270_bestv2/zlWBxz2pTA9p45kUTrI8AQiKrHm.jpg"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Disney Classic Collection[/COLOR]",
                     action="tmdb_saghe",
                     url='http://api.themoviedb.org/3/list/51224e42760ee3297424a1e0?api_key=%s&language=it' % tmdb_key,
                     thumbnail="https://image.tmdb.org/t/p/w180_and_h270_bestv2/vGV35HBCMhQl2phhGaQ29P08ZgM.jpg"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Bad Movies[/COLOR]",
                     action="badmovies",
                     url='http://www.badmovies.org/movies/',
                     thumbnail="http://www.badmovies.org/mainpage/badmovielogo_600.jpg")]
    return itemlist


def tmdb_saghe(item):
    try:
        result = httptools.downloadpage(item.url).data
        result = json.loads(result)
        items = result['items']
    except:
        return

    itemlist = []
    for item in items:
        try:
            title = item['title']
            title = scrapertools.decodeHtmlentities(title)
            title = title.encode('utf-8')

            poster = item['poster_path']
            if poster == '' or poster is None:
                raise Exception()
            else:
                poster = '%s%s' % (tmdb_poster, poster)
            poster = poster.encode('utf-8')

            fanart = item['backdrop_path']
            if fanart == '' or fanart is None: fanart = '0'
            if not fanart == '0': fanart = '%s%s' % (tmdb_image, fanart)
            fanart = fanart.encode('utf-8')

            plot = item['overview']
            if plot == '' or plot is None: plot = '0'
            plot = scrapertools.decodeHtmlentities(plot)
            plot = plot.encode('utf-8')

            itemlist.append(
                Item(channel=__channel__,
                     action="do_search",
                     extra=urllib.quote_plus(title),
                     title="[COLOR azure]%s[/COLOR]" % title,
                     fulltitle=title,
                     plot=plot,
                     thumbnail=poster,
                     fanart=fanart,
                     folder=True))
        except:
            pass

    return itemlist

def badmovies(item):
    itemlist = []

    p = 1
    if '{}' in item.url:
        item.url, p = item.url.split('{}')
        p = int(p)

    # Carica la pagina 
    data = httptools.downloadpage(item.url).data
    data = scrapertools.find_single_match(data, '<table width="100%" cellpadding="6" cellspacing="1" class="listtab">(.*?)<tr><td align="center" valign="top">')

    # Estrae i contenuti 
    patron = r'">([^<]+)\s*</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    scrapedurl = ""
    scrapedplot = ""
    scrapedthumbnail = ""
    for i, (scrapedtitle) in enumerate(matches):
        if (p - 1) * PERPAGE > i: continue
        if i >= p * PERPAGE: break
        title = scrapertools.decodeHtmlentities(scrapedtitle).strip()
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="do_search",
                 title=title,
                 url=title,
                 thumbnail=scrapedthumbnail,
                 fulltitle=title,
                 show=title,
                 plot=scrapedplot,
                 folder=True), tipo='movie'))

    if len(itemlist) > 0:
        itemlist.append(
            Item(channel=__channel__,
                 action="HomePage",
                 title="[COLOR yellow]Torna Home[/COLOR]",
                 folder=True)),

    if len(matches) >= p * PERPAGE:
        scrapedurl = item.url + '{}' + str(p + 1)
        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="badmovies",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png",
                 folder=True))

    return itemlist

def do_search(item):
    from channels import buscador
    return buscador.do_search(item)
