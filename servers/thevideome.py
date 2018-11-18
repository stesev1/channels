# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand-pureita - XBMC Plugin
# Conector para thevideo
# http://www.mimediacenter.info/foro/viewtopic.php?f=36&t=7808
# Alfa - Alfa-PureITA
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

def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)

    data = httptools.downloadpage(page_url).data
    if "File was deleted" in data or "Page Cannot Be Found" in data:
        return False, "[thevideo.me] File Cancellato"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)
    video_urls = []
    post= {}
    post = urllib.urlencode(post)
    if not "embed" in page_url:
        page_url = page_url.replace("https://thevideo.me/", "https://thevideo.me/embed-") + ".html"
    url = httptools.downloadpage(page_url, follow_redirects=False, only_headers=True).headers.get("location", "")
    data = httptools.downloadpage("https://vev.io/api/serve/video/" + scrapertools.find_single_match(url, "embed/([A-z0-9]+)"), post=post).data
    bloque = scrapertools.find_single_match(data, 'qualities":\{(.*?)\}')
    matches = scrapertools.find_multiple_matches(bloque, '"([^"]+)":"([^"]+)')
    for res, media_url in matches:
        video_urls.append(
            [scrapertools.get_filename_from_url(media_url)[-4:] + " (" + res + ") [thevideo.me]", media_url])
    return video_urls


# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    # Añade manualmente algunos erróneos para evitarlos
    encontrados = set()
    devuelve = []

    patronvideos = "(?:thevideo.me|tvad.me|thevid.net|thevideo.ch|thevideo.us)/(?:embed-|)([A-z0-9]+)"
    logger.info("#" + patronvideos + "#")
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    for match in matches:
        titulo = "[thevideo.me]"
        url = "https://thevideo.me/embed-" + match + ".html"
        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'thevideome'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    return devuelve

