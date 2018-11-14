# -*- coding: utf-8 -*-
# StreamOnDemand Community Edition - Kodi Addon
# by DrZ3r0

from core import httptools, logger
from core import scrapertools


# Returns an array of possible video url's from the page_url
def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("[megahd.py] get_video_url(page_url='%s')" % page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data

    data_pack = scrapertools.find_single_match(data, "(eval.function.p,a,c,k,e,.*?)\s*</script>")

    if data_pack != "":
        from lib import jsunpack
        data = jsunpack.unpack(data_pack)

    video_url = scrapertools.find_single_match(data, 'file"?\s*:\s*"([^"]+)",')
    video_urls.append([".mp4 [megahd]", video_url])

    for video_url in video_urls:
        logger.info("[megahd.py] %s - %s" % (video_url[0], video_url[1]))

    return video_urls

