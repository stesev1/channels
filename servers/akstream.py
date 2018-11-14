# -*- coding: utf-8 -*-
# StreamOnDemand Community Edition - Kodi Addon
# by DrZ3r0

import urllib

from core import httptools, logger
from core import scrapertools

headers = [
    ['User-Agent',
#     'Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25'],
     'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0'],
]


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("[akstream.py] url=" + page_url)
    video_urls = []

    data = httptools.downloadpage(page_url, headers=headers).data

    vres=scrapertools.find_multiple_matches(data,'nowrap[^>]+>([^,]+)')
    data_pack = scrapertools.find_single_match(data, "(eval.function.p,a,c,k,e,.*?)\s*</script>")
    if data_pack != "":
        from lib import jsunpack
        data = jsunpack.unpack(data_pack)
        
    # URL
    matches = scrapertools.find_multiple_matches(data, '(http.*?\.mp4)')
    _headers = urllib.urlencode(dict(headers))

    i=0
    for media_url in matches:
        # URL del vídeo
        video_urls.append([vres[i] + " mp4 [Akstream] ", media_url + '|' + _headers])
        i=i+1

    for video_url in video_urls:
        logger.info("[akstream.py] %s - %s" % (video_url[0], video_url[1]))

    return video_urls

