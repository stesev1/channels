# -*- coding: utf-8 -*-
# StreamOnDemand Community Edition - Kodi Addon
# By MrTruth

import re
import urllib

from core import httptools, logger


# Prendo l'url del video dal sito
def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("[cloudifer.py] url=" + page_url)
    video_urls = []

    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:54.0) Gecko/20100101 Firefox/54.0'}

    html = httptools.downloadpage(page_url, headers=headers).data
    match = re.search(r'file: "([^"]+)",', html, re.DOTALL)
    video_urls.append(["Cloudifer", match.group(1) + "|" + urllib.urlencode(headers)])

    return video_urls

