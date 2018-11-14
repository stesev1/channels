# -*- coding: utf-8 -*-
# StreamOnDemand Community Edition - Kodi Addon
# by MrTruth

from core import httptools, scrapertools, logger


def get_video_url(page_url, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data
    
    matches = scrapertools.find_multiple_matches(data, '<source src="([^"]+)" type=\'[^\']+\' label=\'([^\']+)\'[^>]+>')
    for videourl, video_type in matches:
        extension = scrapertools.get_filename_from_url(videourl)[-4:]
        video_urls.append(["%s [estream] %sp" % (extension, video_type.split('x')[1]), videourl])

    return video_urls
