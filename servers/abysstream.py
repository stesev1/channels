# -*- coding: utf-8 -*-
# StreamOnDemand Community Edition - Kodi Addon
# by DrZ3r0
# Fix trovato qui (per varie ed eventuali - Zanzibar82) https://github.com/FusionwareIT/FusionBox-repo/

import urllib

from core import httptools, logger
from core import scrapertools

headers = [
    ['Accept-Encoding', 'gzip, deflate'],
    ['User-Agent',
     'Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25'],
]


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("[abysstream.py] url=" + page_url)
    video_urls = []

    data = httptools.downloadpage(page_url, headers=headers).data

    stream_link = scrapertools.find_single_match(data, '<input type="hidden" name="streamLink" value="([^"]+)">')
    temp_link = scrapertools.find_single_match(data, '<input type="hidden" name="templink" value="([^"]+)">')

    headers.append(['Referer', page_url])
    post_data = 'streamLink=%s&templink=%s' % (stream_link, temp_link)
    data = httptools.downloadpage('http://abysstream.com/viewvideo.php', post=post_data, headers=headers).data

    # URL
    media_url = scrapertools.find_single_match(data, '<source src="([^"]+)" type="video/mp4"')
    _headers = urllib.urlencode(dict(headers))

    # URL del vídeo
    video_urls.append(
        [scrapertools.get_filename_from_url(media_url)[-4:] + " [Abysstream]", media_url + '|' + _headers])

    for video_url in video_urls:
        logger.info("[abysstream.py] %s - %s" % (video_url[0], video_url[1]))

    return video_urls
