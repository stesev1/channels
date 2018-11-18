# -*- coding: iso-8859-1 -*-
# ------------------------------------------------------------
# streamondemand-pureita - XBMC Plugin
# Connettore Vidlox
# http://www.mimediacenter.info/foro/viewtopic.php?f=36&t=7808
# Anfa - Alfa-PureITA
# ------------------------------------------------------------

import re
import urllib

from core import httptools
from core import scrapertools
from core import logger


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
	
    data = httptools.downloadpage(page_url).data
    if "Deleted" in data:
        return False, "[vidlox] Il video e stato rimosso"

    return True, ""


def get_video_url(page_url, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    data = httptools.downloadpage(page_url).data
    bloque = scrapertools.find_single_match(data, 'sources:.\[.*?]')
    matches = scrapertools.find_multiple_matches(bloque, '(http.*?)"')
    for videourl in matches:
        extension = scrapertools.get_filename_from_url(videourl)[-4:]
        video_urls.append(["%s [vidlox]" %extension, videourl])

    return video_urls

	
def find_videos(text):
    encontrados = set()
    devuelve = []

    # https://vidlox.me/embed-e5vjxdwajp9j.html
    patronvideos = r"(?i)(https://vidlox.(?:tv|me)/embed-.*?.html)"
    logger.info("[vidloxtv.py] find_videos #" + patronvideos + "#")
    matches = re.compile(patronvideos, re.DOTALL).findall(text)

    for match in matches:
        titulo = "[vidloxtv]"
        url = match
        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'vidlox'])

            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    return devuelve
	

