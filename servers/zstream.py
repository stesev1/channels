# -*- coding: utf-8 -*-
# StreamOnDemand Community Edition - Kodi Addon

from core import httptools, logger
from core import scrapertools


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)

    data = httptools.downloadpage(page_url).data
    if "File was deleted" in data:
        return False, "[Zstream] Il video è stato cancellato"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=%s" % page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data

    matches = scrapertools.find_multiple_matches(data, '\{file:"([^"]+)",label:"([^"]+)"')
    for media_url, calidad in matches:
        calidad = "." + media_url.rsplit('.', 1)[1] + " " + calidad
        video_urls.append([calidad + ' [zstream]', media_url])

    return video_urls
