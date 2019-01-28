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

headers = [['User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0']]


def get_video_url(page_url, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    data = httptools.downloadpage(page_url).data
    bloque = scrapertools.find_single_match(data, 'sources:.\[.*?]')
    matches = scrapertools.find_multiple_matches(bloque, '(http.*?)"')
    for videourl in matches:
        video_urls.append(["MP4 [Wstream]", videourl])
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
