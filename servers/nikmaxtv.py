# -*- coding: utf-8 -*-
# StreamOnDemand Community Edition - Kodi Addon
# By Errmax

import re
import urllib

from core import httptools, logger


# Prendo l'url del video dal sito
def get_video_url(page_url,
                  premium=False,
                  user="",
                  password="",
                  video_password=""):
    logger.info("[nkimaxtv.py] url=" + page_url)
    video_urls = []

    headers = {
        'User-Agent':
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:54.0) Gecko/20100101 Firefox/54.0',
        'Accept':
        'video/webm,video/ogg,video/*;q=0.9,application/ogg;q=0.7,audio/*;q=0.6,*/*;q=0.5'
    }

    html = httptools.downloadpage(page_url, headers=headers).data
    matches = re.findall('src:"([^"]+)"', html, re.DOTALL)
    for match in matches:
        video_urls.append([
            "NikMaxTv (" + match[-4:-2] + ")",
            match + "|" + urllib.urlencode(headers)
        ])

    return video_urls
