# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para wstream.video
# http://www.mimediacenter.info/foro/viewtopic.php?f=36&t=7808
# by DrZ3r0
# ------------------------------------------------------------

import re
import time
import urllib
import xbmc

from core import httptools
from lib import jsunpack
from core import config
from core import logger
from core import scrapertools

headers = [['User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0']]


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("[wstream.py] url=" + page_url)
    video_urls = []

    data = scrapertools.cache_page(page_url, headers=headers)
    vid = scrapertools.find_multiple_matches(data,'download_video.*?>.*?<.*?<td>([^\,,\s]+)')

    headers.append(['Referer', page_url])
    post_data = scrapertools.find_single_match(data, "</div>\s*<script type='text/javascript'>(eval.function.p,a,c,k,e,.*?)\s*</script>")
    if post_data != "":
       from lib import jsunpack
       data = jsunpack.unpack(post_data)

    media_url = scrapertools.find_multiple_matches(data, '(http.*?\.mp4)')
    _headers = urllib.urlencode(dict(headers))
    i=0

    for media_url in media_url:
        video_urls.append([vid[i] + " mp4 [wstream] ", media_url + '|' + _headers])
        i=i+1

    for video_url in video_urls:
        logger.info("[wstream.py] %s - %s" % (video_url[0], video_url[1]))

    return video_urls	

		
	
def find_videos(data):
    encontrados = set()
    devuelve = []

    patronvideos = r"wstream.video/(?:embed-)?([a-z0-9A-Z]+)"
    logger.info("[wstream.py] find_videos #" + patronvideos + "#")
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    for match in matches:
        titulo = "[wstream]"
        url = 'http://wstream.video/%s' % match

        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'wstream'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    return devuelve
