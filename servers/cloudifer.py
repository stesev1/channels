# -*- coding: iso-8859-1 -*-
# ------------------------------------------------------------
# streamondemand - XBMC Plugin
# Connettore per https://cloudifer.net/
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# By MrTruth
# ------------------------------------------------------------

import re
import urllib

from core import logger
from core import scrapertools


# Prendo l'url del video dal sito
def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("[cloudifer.py] url=" + page_url)
    video_urls = []

    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:53.0) Gecko/20100101 Firefox/53.0'}

    html = scrapertools.cache_page(page_url, headers=headers)
    match = re.search(r'file: "([^"]+)",', html, re.DOTALL)
    video_urls.append(["Cloudifer", match.group(1) + "|" + urllib.urlencode(headers)])

    return video_urls


# Encuentra vídeos de este servidor en el texto pasado
def find_videos(text):
    encontrados = set()
    devuelve = []

    # https://cloudifer.net/embed/1N2F
    # https://cloudifer.net/480
    patronvideos = r'(?://|\.)cloudifer.\w+/(?:embed/)?([a-zA-Z0-9]+)'
    logger.info("[cloudifer.py] find_videos #" + patronvideos + "#")
    matches = re.compile(patronvideos, re.DOTALL).findall(text)

    for match in matches:
        titulo = "[cloudifer]"
        url = "https://cloudifer.net/embed/%s" % match
        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'cloudifer'])

            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    return devuelve
