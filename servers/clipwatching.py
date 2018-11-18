# -*- coding: utf-8 -*-
#------------------------------------------------------------
# streamondemand-pureita - XBMC Plugin
# Conectore per clipwatching
# http://www.mimediacenter.info/foro/viewtopic.php?f=36&t=7808
# by Alfa
#------------------------------------------------------------

import re
import urllib

from core import config
from core import httptools
from core import scrapertools
from core import logger
from lib import jsunpack


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url).data
    if "File Not Found" in data or "File was deleted" in data:
        return False, "[clipwatching] Il video e stato cancellato"
    return True, ""


def get_video_url(page_url, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    data = httptools.downloadpage(page_url).data
    packed = scrapertools.find_single_match(data, "text/javascript'>(.*?)\s*</script>")
    unpacked = jsunpack.unpack(packed)
    video_urls = []
    videos = scrapertools.find_multiple_matches(unpacked, 'file:"([^"]+).*?label:"([^"]+)')
    for video, label in videos:
        video_urls.append([label + " [clipwatching]", video])
    logger.info("Url: %s" % videos)
    video_urls.sort(key=lambda it: int(it[0].split("p ", 1)[0]))
    return video_urls
	
	
	
def find_videos(data):
    encontrados = set()
    devuelve = []

    # http://clipwatching.com/jdfscsa5uoy4
    patronvideos  = "clipwatching.com/(\\w+)"
    logger.info("streamondemand-pureita.servers.clipwatching find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[clipwatching]"
        url = "http://clipwatching.com/embed-%s.html" % match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'clipwatching' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    patronvideos  = "clipwatching.com/(e.*?.html)"
    logger.info("streamondemand-pureita.servers.clipwatching find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[clipwatching]"
        url = "http://clipwatching.com/%s" % match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'clipwatching' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)
			
    return devuelve
	
	
