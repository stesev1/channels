# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Thegroove360 - XBMC Plugin
# Canale  per http://manganimenod.it
# ------------------------------------------------------------

import re

from core import httptools, scrapertools, servertools, listtools
from core.item import Item
from platformcode import logger

__channel__ = "animenod"
listtools.__channel__ = __channel__

host = "http://animenod.one/"


# ----------------------------------------------------------------------------------------------------------------
def mainlist(item):
    logger.info("[thegroove360.animenod] mainlist")
    itemlist = [Item(channel=__channel__,
                     action="dragonball_list",
                     title=color("Dragon Ball (1, Z, GT, Kai, Super)", "azure"),
                     thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/popcorn_cinema_movie_.png"),
                Item(channel=__channel__,
                     action="episodi",
                     title=color("One Piece", "azure"),
                     url="%s/episodi.php?a=ONEPIECE&s=01" % host,
                     extra="ONEPIECE",
                     thumbnail="https://www.thetvdb.com/banners/_cache/posters/81797-13.jpg"),
                Item(channel=__channel__,
                     action="episodi",
                     title=color("Fairy Tail", "azure"),
                     url="%s/episodi.php?a=FAIRYTAIL&s=01" % host,
                     extra="FAIRYTAIL",
                     thumbnail="https://www.thetvdb.com/banners/_cache/posters/114801-16.jpg"),
                Item(channel=__channel__,
                     action="episodi",
                     title=color("Bleach", "azure"),
                     url="%s/episodi.php?a=BLEACH&s=01" % host,
                     extra="BLEACH",
                     thumbnail="https://www.thetvdb.com/banners/_cache/posters/74796-1.jpg"),
                Item(channel=__channel__,
                     action="episodi",
                     title=color("Cavalieri dello zodiaco", "azure"),
                     url="%s/episodi.php?a=CDZ&s=01" % host,
                     extra="CDZ",
                     thumbnail="https://www.thetvdb.com/banners/_cache/posters/72775-3.jpg"),
                Item(channel=__channel__,
                     action="episodi",
                     title=color("Hunter x Hunter", "azure"),
                     url="%s/episodi.php?a=HUNTERXHUNTER&s=01" % host,
                     extra="HUNTERXHUNTER",
                     thumbnail="https://www.thetvdb.com/banners/_cache/posters/79076-5.jpg"),
                Item(channel=__channel__,
                     action="episodi",
                     title=color("Naruto", "azure"),
                     url="%s/episodi.php?a=NARUTO1&s=01" % host,
                     extra="NARUTO1",
                     thumbnail="https://www.thetvdb.com/banners/_cache/posters/78857-9.jpg"),
                Item(channel=__channel__,
                     action="episodi",
                     title=color("Naruto: Shippuden", "azure"),
                     url="%s/episodi.php?a=NARUTOSHIPPUDEN&s=01" % host,
                     extra="NARUTOSHIPPUDEN",
                     thumbnail="https://www.thetvdb.com/banners/_cache/posters/79824-9.jpg"),
                Item(channel=__channel__,
                     action="episodi",
                     title=color("Boruto", "azure"),
                     url="%s/episodi.php?a=BORUTO&s=01" % host,
                     extra="BORUTO",
                     thumbnail="https://www.thetvdb.com/banners/_cache/posters/321285-2.jpg")]

    return itemlist


# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def dragonball_list(item):
    logger.info("[thegroove360.animenod] dragonball_list")
    itemlist = [Item(channel=__channel__,
                     action="episodi",
                     title=color("Dragon Ball", "azure"),
                     url="%s/episodi.php?a=DRAGONBALL1&s=01" % host,
                     extra="DRAGONBALL1",
                     thumbnail="https://www.thetvdb.com/banners/_cache/posters/76666-17.jpg"),
                Item(channel=__channel__,
                     action="episodi",
                     title=color("Dragon Ball Z", "azure"),
                     url="%s/episodi.php?a=DRAGONBALLZ&s=01" % host,
                     extra="DRAGONBALLZ",
                     thumbnail="https://www.thetvdb.com/banners/_cache/posters/81472-27.jpg"),
                Item(channel=__channel__,
                     action="episodi",
                     title=color("Dragon Ball Kai", "azure"),
                     url="%s/episodi.php?a=DRAGONBALLKAI&s=01" % host,
                     extra="DRAGONBALLKAI",
                     thumbnail="https://www.thetvdb.com/banners/_cache/posters/79275-3.jpg"),
                Item(channel=__channel__,
                     action="episodi",
                     title=color("Dragon Ball GT", "azure"),
                     url="%s/episodi.php?a=DRAGONBALLGT&s=01" % host,
                     extra="DRAGONBALLGT",
                     thumbnail="https://www.thetvdb.com/banners/_cache/posters/88031-1.jpg"),
                Item(channel=__channel__,
                     action="episodi",
                     title=color("Dragon Ball Super", "azure"),
                     url="%s/episodi.php?a=DRAGONBALLSUPER&s=01" % host,
                     extra="DRAGONBALLSUPER",
                     thumbnail="https://www.thetvdb.com/banners/_cache/posters/295068-16.jpg")]
    return itemlist

# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def episodi(item):
    logger.info("[thegroove360.animenod] episodi")
    itemlist = []

    data = httptools.downloadpage(item.url).data

    itemp = {'title': scrapertools.decodeHtmlentities('\\3').strip(),
             'url': "%s/%s" % (host, '\\1'),
             'fulltitle': scrapertools.decodeHtmlentities('\\3').strip(),
             'contentType': 'episode',
             'thumbnail': '\\2',
             'extra': item.extra,
             'extracheck': 'findvideos'}

    patron = r'<div class="ep"><a href="([^=]+=%s[^"]+)"><.*?url\(\'(.*?)\'\)[^>]+>[^>]+>' % item.extra
    patron += r'[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+><a.*?title="([^"]+)">'

    itemlist = listtools.list_titles(regx=patron, data=data, itemp=itemp)

    return itemlist


# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def findvideos(item):
    logger.info("[thegroove360.animenod] findvideos")

    data = httptools.downloadpage(item.url).data
    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        server = re.sub(r'[-\[\]\s]+', '', videoitem.title).capitalize()
        videoitem.title = "".join(["[%s] " % color(server, 'orange'), item.title])
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.show = item.show
        videoitem.plot = item.plot
        videoitem.channel = __channel__

    return itemlist

# ================================================================================================================

# ----------------------------------------------------------------------------------------------------------------
def color(text, color):
    return "[COLOR " + color + "]" + text + "[/COLOR]"

# ================================================================================================================
