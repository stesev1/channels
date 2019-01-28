# -*- coding: utf-8 -*-
#------------------------------------------------------------
# streamondemand-pureita - XBMC Plugin
# Conector para nowvideo
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
# Credits:
# Unwise and main algorithm taken from Eldorado url resolver
# https://github.com/Eldorados/script.module.urlresolver/blob/master/lib/urlresolver/plugins/nowvideo.py

import re
import urllib
import urlparse

from core import httptools
from core import logger
from core import scrapertools



def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)

    data = httptools.downloadpage(page_url).data

    if "The file is being converted" in data:
        return False, "File in elaborazione"
    elif "no longer exists" in data:
        return False, "File cancellato"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    data = httptools.downloadpage(page_url).data

    page_url_post = scrapertools.find_single_match(data, r'<Form\s*id="[^"]*"\s*method="POST"\s*action="([^"]+)">')
    post = urllib.urlencode(
        {k: v for k, v in scrapertools.find_multiple_matches(data, r'name="([^"]+)" value="([^"]*)"')})

    import xbmc
    xbmc.sleep(1000)

    page_url_post = urlparse.urljoin(page_url, page_url_post)

    data = httptools.downloadpage(page_url_post, post).data

    videourls = scrapertools.find_multiple_matches(data, r'source:\s*"([^"]+)"')
    for videourl in videourls:
        ext = scrapertools.get_filename_from_url(videourl)[-4:]
        videourl = videourl.replace("%3F", "?") + "|User-Agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0"
        video_urls.append([ext + " [nowvideo]", videourl])
    return video_urls



# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    # http://nowvideo.club/videos/ekg23cp29u54
    patronvideos = 'nowvideo.club/(?:videos|)(?:video/|embed.php\?.*v=)([A-z0-9]+)'
    logger.info("#" + patronvideos + "#")
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    for match in matches:
        titulo = "[nowvideo]"
        url = "http://nowvideo.club/videos/" + match
        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'nowvideo'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    return devuelve