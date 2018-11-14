# -*- coding: utf-8 -*-
# StreamOnDemand Community Edition - Kodi Addon

import urllib

from core import httptools, logger
from core import scrapertools
from lib import jsunpack

headers = [['User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:54.0) Gecko/20100101 Firefox/54.0']]


def test_video_exists(page_url):
    logger.info("[fastvideo.py] test_video_exists(page_url='%s')" % page_url)

    video_id = scrapertools.find_single_match(page_url, 'me/([A-Za-z0-9]+)')
    url = 'http://www.fastvideo.me/embed-%s-607x360.html' % video_id

    data = httptools.downloadpage(url, headers=headers).data

    if "File was deleted from FastVideo" in data:
        return False, "Il video è stato cancellato."

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("[fastvideo.py] url=" + page_url)

    video_id = scrapertools.find_single_match(page_url, 'me/([A-Za-z0-9]+)')
    url = 'http://www.fastvideo.me/embed-%s-607x360.html' % video_id

    data = httptools.downloadpage(url, headers=headers).data

    packed = scrapertools.find_single_match(data, "<script type='text/javascript'>eval.function.p,a,c,k,e,.*?</script>")
    unpacked = jsunpack.unpack(packed)
    media_url = scrapertools.find_single_match(unpacked, 'file:"([^"]+)"')

    headers.append(['Referer', page_url])

    _headers = urllib.urlencode(dict(headers))
    # URL del video
    vurl = media_url + '|' + _headers

    video_urls = [[scrapertools.get_filename_from_url(media_url)[-4:] + " [fastvideo.me]", vurl]]

    for video_url in video_urls:
        logger.info("[fastvideo.py] %s - %s" % (video_url[0], video_url[1]))

    return video_urls

