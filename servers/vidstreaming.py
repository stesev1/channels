# -*- coding: utf-8 -*-
# StreamOnDemand Community Edition - Kodi Addon
# By MrTruth

import re

from core import httptools, scrapertools, servertools, logger


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url).data

    match = scrapertools.find_single_match(data, r'currentlink\s*=\s*"(//[^"]+)"')
    if not match:
        return False, "[VidStreaming] Il video non può essere riprodotto"

    return True, ""


def get_video_url(page_url, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data

    video_url = "https:" + scrapertools.find_single_match(data, r'currentlink\s*=\s*"(//[^"]+)"')

    extension = scrapertools.get_filename_from_url(video_url)[-4:]
    video_urls.append(["%s [vidstreaming]" % extension, video_url])

    return video_urls


def find_videos(text):
    encontrados = set()
    devuelve = []

    patronvideos = r'(?://|\.)vidstreaming\.io/(?:embed|streaming)\.php\?id=([0-9A-Za-z]+)'
    logger.info(" find_videos #" + patronvideos + "#")

    matches = re.compile(patronvideos).findall(text)

    for media_id in matches:
        titulo = "[vidstreaming]"
        url = 'https://vidstreaming.io/streaming.php?id=%s' % media_id
        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'vidstreaming'])
            encontrados.add(url)

            data = httptools.downloadpage(url).data
            devuelve.extend(servertools.findvideos(data))
        else:
            logger.info("  url duplicada=" + url)

    return devuelve
