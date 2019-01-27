# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector for akstream.net
# http://www.mimediacenter.info/foro/viewtopic.php?f=36&t=7808
# by DrZ3r0
# ------------------------------------------------------------

import re
import urllib

from core import httptools
from core import logger
from core import scrapertools

headers = [['User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0']]

def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("[akstream.py] url=" + page_url)
    video_urls = []

    data = scrapertools.cache_page(page_url, headers=headers)
    vid = scrapertools.find_multiple_matches(data,'nowrap[^>]+>([^,]+)')

    headers.append(['Referer', page_url])
    post_data = scrapertools.find_single_match(data, "(eval.function.p,a,c,k,e,.*?)\s*</script>")
    if post_data != "":
       from lib import jsunpack
       data = jsunpack.unpack(post_data)

    media_url = scrapertools.find_multiple_matches(data, '(http.*?\.mp4)')
    _headers = urllib.urlencode(dict(headers))
    i=0

    for media_url in media_url:
        video_urls.append([vid[i] + " mp4 [Akstream] ", media_url + '|' + _headers])
        i=i+1

    for video_url in video_urls:
        logger.info("[akstream.py] %s - %s" % (video_url[0], video_url[1]))

    return video_urls


# Encuentra vídeos del servidor en el texto pasado
def find_videos(text):
    encontrados = set()
    devuelve = []

    # http://akstream.net/v/iwbe6genso37
    patronvideos = 'akvideo.stream/?(?:/video/|embed-)([a-z0-9A-Z]+)'
    logger.info("[akstream.py] find_videos #" + patronvideos + "#")
    matches = re.compile(patronvideos, re.DOTALL).findall(text)

    for match in matches:
        titulo = "[Akstream]"
        url = "http://akvideo.stream/" + match
        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'akstream'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    return devuelve