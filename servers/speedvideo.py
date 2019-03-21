# -*- coding: utf-8 -*-
#------------------------------------------------------------
# streamondemand - XBMC Plugin
# Conector para speedvideo
# by be4t5
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# ------------------------------------------------------------

import base64
import re

from core import logger, httptools
from core import scrapertools


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)

    return True, ""


def get_video_url(page_url,
                  premium=False,
                  user="",
                  password="",
                  video_password=""):
    logger.info("url=" + page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data

    media_urls = scrapertools.find_multiple_matches(data, r"file:[^']'([^']+)',\s*label:[^\"]\"([^\"]+)\"")

    for media_url, label in media_urls:
        media_url = httptools.downloadpage(media_url, only_headers=True, follow_redirects=False).headers.get("location", "")

        if media_url:
            video_urls.append([label + " " + media_url.rsplit('.', 1)[1] + ' [speedvideo]', media_url])

    return video_urls