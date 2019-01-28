# -*- coding: utf-8 -*-
# StreamOnDemand Community Edition - Kodi Addon

import xbmc

from core import httptools, scrapertools, logger

host = "http://vidtodo.com"
id_server = "vidtodo"


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)

    data = httptools.downloadpage(page_url).data.replace('"', "'")

    page_url_post = scrapertools.find_single_match(data, "<Form method='POST' action='([^']+)'>")
    imhuman = "&imhuman=" + scrapertools.find_single_match(data, "name='imhuman' value='([^']+)'").replace(" ", "+")
    import urllib
    post = urllib.urlencode({k: v for k, v in scrapertools.find_multiple_matches(data, "name='([^']+)' value='([^']*)'")}) + imhuman

    xbmc.sleep(1 * 1000)
    data = httptools.downloadpage(page_url_post, post=post).data

    sources = scrapertools.find_single_match(data, 'sources: \[([^\]]+)\]')
    video_urls = []
    for media_url in scrapertools.find_multiple_matches(sources, '"([^"]+)"'):
        if media_url.endswith(".mp4"):
            video_urls.append([".mp4 [%s]" % id_server, media_url])

        if media_url.endswith(".m3u8"):
            video_urls.append(["M3U8 [%s]" % id_server, media_url])

        if media_url.endswith(".smil"):
            smil_data = httptools.downloadpage(media_url).data

            rtmp = scrapertools.find_single_match(smil_data, 'base="([^"]+)"')
            playpaths = scrapertools.find_multiple_matches(smil_data, 'src="([^"]+)" height="(\d+)"')

            mp4 = "http:" + scrapertools.get_match(rtmp, '(//[^:]+):') + "/%s/" + \
                  scrapertools.find_single_match(data, '"Watch video ([^"]+")').replace(' ', '.') + ".mp4"

            for playpath, inf in playpaths:
                h = scrapertools.find_single_match(playpath, 'h=([a-z0-9]+)')
                video_urls.append([".mp4 [%s] %s" % (id_server, inf), mp4 % h])
                video_urls.append(["RTMP [%s] %s" % (id_server, inf), "%s playpath=%s" % (rtmp, playpath)])

    for video_url in video_urls:
        logger.info("video_url: %s - %s" % (video_url[0], video_url[1]))

    return video_urls
