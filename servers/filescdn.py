# -*- coding: utf-8 -*-
# StreamOnDemand Community Edition - Kodi Addon

from core import scrapertools, logger


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url).data

    if "File was deleted" in data:
        return False, "[FilesCDN] Il video è stato cancellato"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)
    video_urls = []
    data = httptools.downloadpage(page_url).data
    url = scrapertools.find_single_match(data, '(?i)link:\s*"(https://.*?filescdn\.com.*?mp4)"')
    url = url.replace(':443', '')
    video_urls.append(['filescdn', url])

    return video_urls
