# -*- coding: utf-8 -*-
# StreamOnDemand Community Edition - Kodi Addon
# Credits: alfa-addon
# Last edit whiplash78

import os
import urllib

import xbmc

from core import config, logger
from core import httptools
from core import scrapertools


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)

    data = httptools.downloadpage(page_url, cookies=False).data
    if 'file was deleted' in data:
        return False, "[FlashX] File rimosso"
    elif 'Video is processing now' in data:
        return False, "[FlashX] File processing"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("url=" + page_url)

    data = httptools.downloadpage(page_url).data

    cgi_counter = scrapertools.find_single_match(data, """(?is)src=.(https://www.flashx.bz/counter.cgi.*?[^(?:'|")]+)""")
    cgi_counter = cgi_counter.replace("%0A", "").replace("%22", "")
    httptools.downloadpage(cgi_counter, cookies=False)

    xbmc.sleep(6 * 1000)

    url_playitnow = "https://www.flashx.bz/dl?playitnow"
    fid = scrapertools.find_single_match(data, 'input type="hidden" name="id" value="([^"]*)"')
    fname = scrapertools.find_single_match(data, 'input type="hidden" name="fname" value="([^"]*)"')
    fhash = scrapertools.find_single_match(data, 'input type="hidden" name="hash" value="([^"]*)"')

    headers = {'Content': 'application/x-www-form-urlencoded'}
    post_parameters = {
        "op": "download1",
        "usr_login": "",
        "id": fid,
        "fname": fname,
        "referer": "https://www.flashx.bz/",
        "hash": fhash,
        "imhuman": "Continue To Video"
    }
    data = httptools.downloadpage(url_playitnow, urllib.urlencode(post_parameters), headers=headers).data

    video_urls = []
    media_urls = scrapertools.find_multiple_matches(data, "{src: '([^']+)'.*?,label: '([^']+)'")
    subtitle = ""
    for media_url, label in media_urls:
        if media_url.endswith(".srt") and label == "Italian":
            try:
                from core import filetools
                data = httptools.downloadpage(media_url).data
                subtitle = os.path.join(config.get_data_path(), 'sub_flashx.srt')
                filetools.write(subtitle, data)
            except:
                import traceback
                logger.info("Error download subtitle: " + traceback.format_exc())

    for media_url, label in media_urls:
        if not media_url.endswith("png") and not media_url.endswith(".srt"):
            video_urls.append(["." + media_url.rsplit('.', 1)[1] + " [flashx]", media_url, 0, subtitle])

    for video_url in video_urls:
        logger.info("%s - %s" % (video_url[0], video_url[1]))

    return video_urls
