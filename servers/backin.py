# -*- coding: utf-8 -*-
# StreamOnDemand Community Edition - Kodi Addon
# by DrZ3r0

import urllib

import xbmc

from core import httptools, logger
from core import scrapertools


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("page_url=" + page_url)

    video_urls = []

    headers = [["User-Agent", "Mozilla/5.0 (Windows NT 6.1; rv:54.0) Gecko/20100101 Firefox/54.0"]]

    # First access
    httptools.downloadpage("http://backin.net/s/%s" % page_url, headers=headers)

    xbmc.sleep(10000)
    headers.append(["Referer", "http://backin.net/s/%s" % page_url])

    data = httptools.downloadpage("http://backin.net/stream-%s-500x400.html" % page_url, headers=headers).data

    data_pack = scrapertools.find_single_match(data, "(eval.function.p,a,c,k,e,.*?)\s*</script>")
    if data_pack:
        from lib import jsunpack
        data = jsunpack.unpack(data_pack)

    # URL
    url = scrapertools.find_single_match(data, 'file\s*:\s*"([^"]+)",')

    # URL del vídeo
    video_urls.append([".mp4" + " [backin]", url + '|' + urllib.urlencode(dict(headers))])

    for video_url in video_urls:
        logger.info("%s - %s" % (video_url[0], video_url[1]))

    return video_urls
