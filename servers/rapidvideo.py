# -*- coding: iso-8859-1 -*-
# ------------------------------------------------------------
# streamondemand-PureITA- XBMC Plugin
# Server rapidvideo
# http://www.mimediacenter.info/foro/viewtopic.php?f=36&t=7808
# by alfa - alfa-pureita
# ------------------------------------------------------------

import re
import urllib

from core import logger
from core import scrapertools
from core import httptools


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    try:
        response = httptools.downloadpage(page_url)
    except:
        pass

    if not response.data or "urlopen error [Errno 1]" in str(response.code):
        from platformcode import config
        if config.is_xbmc():
            return False, "[Rapidvideo] Questo connettore funziona solo con versioni le versioni 17 di Kodi"
        elif config.get_platform() == "plex":
            return False, "[Rapidvideo] Questo connettore non funziona con la tua versione Plex installata"
        elif config.get_platform() == "mediaserver":
            return False, "[Rapidvideo] Questo connettore richiede la versione di Python 2.7.9 o successive"

    if "Object not found" in response.data:
        return False, "[Rapidvideo] Il file non esiste oppure e stato cancellato"
    if response.code == 500:
        return False, "[Rapidvideo] Problemi temporanei nel server"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)
    video_urls = []
    data = httptools.downloadpage(page_url).data
    patron = 'https://www.rapidvideo.com/e/[^"]+'
    match = scrapertools.find_multiple_matches(data, patron)
    if match:
        for url1 in match:
           res = scrapertools.find_single_match(url1, '=(\w+)')
           data = httptools.downloadpage(url1).data
           url = scrapertools.find_single_match(data, 'source src="([^"]+)')
           ext = scrapertools.get_filename_from_url(url)[-4:]
           video_urls.append(['%s %s [rapidvideo]' % (ext, res), url])
    else:
        patron = 'data-setup.*?src="([^"]+)".*?'
        patron += 'type="([^"]+)"'
        match = scrapertools.find_multiple_matches(data, patron)
        for url, ext in match:
            video_urls.append(['%s [rapidvideo]' % (ext), url])
    return video_urls


# Encuentra vídeos de este servidor en el texto pasado
def find_videos(text):
    encontrados = set()
    devuelve = []

    #
    patronvideos = 'rapidvideo.(?:org|com)/(?:\\?v=|e/|embed/|v/)([A-z0-9]+)'
    logger.info("[rapidvideo.py] find_videos #" + patronvideos + "#")
    matches = re.compile(patronvideos, re.DOTALL).findall(text)

    for match in matches:
        titulo = "[rapidvideo]"
        url = 'https://www.rapidvideo.com/e/%s' % match
        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'rapidvideo'])

            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    return devuelve
