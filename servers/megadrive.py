# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# StreamOnDemand-PureITA / XBMC Plugin
# Connettore  megadrive
# http://www.mimediacenter.info/foro/viewtopic.php?f=36&t=7808
# by DrZ3r0
# ------------------------------------------------------------

import re
import urllib

from core import logger
from core import scrapertools
from core import httptools


def get_video_url(page_url, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url).data
    video_urls = []
    videourl = scrapertools.find_single_match(data, "<source.*?src='([^']+)")
    video_urls.append([".mp4 [megadrive]", videourl])

    return video_urls


# Encuentra videos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    patronvideos = r"megadrive.co/embed/([A-z0-9]+)"
    logger.info("[megadrive.py] find_videos #" + patronvideos + "#")
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    for match in matches:
        titulo = "[megadrive]"
        url = 'http://megadrive.co/embed-%s.html' % match

        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'megadrive'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    return devuelve
