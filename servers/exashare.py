# -*- coding: utf-8 -*-
# StreamOnDemand Community Edition - Kodi Addon
# by DrZ3r0

import re

from core import httptools, logger
from core import scrapertools


def test_video_exists(page_url):
    logger.info("[exashare.py] test_video_exists(page_url='%s')" % page_url)

    data = httptools.downloadpage(page_url).data

    if re.search("""File Not Found""", data):
        return False, 'Video non trovato'

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("[exashare.py] url=" + page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data

    try:
        page_url = re.search('src="([^"]+)', data).group(1)
    except:
        return video_urls

    data = httptools.downloadpage(page_url).data

    # URL del vídeo
    url = re.search('file\s*:\s*"(http.+?)"', data)
    if url:
        url = url.group(1)
        video_urls.append([scrapertools.get_filename_from_url(url)[-4:] + " [exashare]", url])

    return video_urls  # Encuentra vídeos del servidor en el texto pasado

