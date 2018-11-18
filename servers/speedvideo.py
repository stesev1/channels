# -*- coding: utf-8 -*-
#------------------------------------------------------------
# streamondemand - XBMC Plugin
# Conector para speedvideo
# by be4t5
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# ------------------------------------------------------------

import base64
import re

from core import logger, httptools
from core import scrapertools


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)

    return True, ""


def get_video_url(page_url,
                  premium=False,
                  user="",
                  password="",
                  video_password=""):
    logger.info("url=" + page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data

    media_url = scrapertools.find_single_match(data, 'linkfile ="([^"]+)"')

    media_url = scrapertools.getLocationHeaderFromResponse(media_url)

    video_urls.append(
        ["." + media_url.rsplit('.', 1)[1] + ' [speedvideo]', media_url])

    return video_urls

# Encuentra videos de este servidor en el texto pasado
def find_videos(text):
    encontrados = set()
    devuelve = []

    # http://speedvideo.net/embed-fmbvopi1381q-530x302.html
    # http://speedvideo.net/hs7djap7jwrw/Tekken.Kazuyas.Revenge.2014.iTALiAN.Subbed.DVDRiP.XViD.NeWZoNe.avi.html
    patronvideos = 'speedvideo.net/(?:embed-|)([A-Z0-9a-z]{12})'
    logger.info("#" + patronvideos + "#")
    matches = re.compile(patronvideos, re.DOTALL).findall(text)

    for match in matches:
        titulo = "[speedvideo]"
        url = "http://speedvideo.net/embed-%s.html" % match
        if url not in encontrados and url != "http://speedvideo.net/embed":
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'speedvideo'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    return devuelve