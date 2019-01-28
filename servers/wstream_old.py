# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para wstream.video
# http://www.mimediacenter.info/foro/viewtopic.php?f=36&t=7808
# by DrZ3r0
# ------------------------------------------------------------

import re
import time
import urllib
import xbmc

from core import httptools
from lib import jsunpack
from core import config
from core import logger
from core import scrapertools

headers = [['User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0']]

def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("[wstream.py] get_video_url(page_url='%s')" % page_url)
    video_urls = []
    vid_urls = []
    
    data = httptools.downloadpage(page_url, headers=headers).data

    xbmc.sleep(4 * 1000)

    patronsources='sources\:\s*\[["\']\s*(https?:\/\/[^>]+?wstream.*?)\s*["\']\]'
    video_url = scrapertools.find_single_match(data, patronsources)
    if not video_url:
        data_pack = scrapertools.find_single_match(data, "<\/div>\s*[^>]+>(eval.function.p,a,c,k,e,.*?)\s*<\/script>")

        if data_pack != "":
            data_pack = jsunpack.unpack(data_pack)
        video_url = scrapertools.find_single_match(data_pack, patronsources)

    if video_url:
        video_url = re.sub('"','',video_url)
        video_url = re.split(",",video_url)

    vid_res=re.compile('download_video.*?>(.*?)<.*?<td>([^\,,\s]+)').findall(data)
    if vid_res[0][0]=='Original' and len(vid_res)==(len(video_url)+1):  del vid_res[0]
    
    i=0
    for v in video_url:
        if vid_res[i][0]: vres = vid_res[i][0] + " (" + vid_res[i][1] +")"
        else: vres = ''
        vid_urls.append([v,vres])
        i=i+1

    if vid_urls:
        for v in vid_urls:
            video_urls.append([v[1] + " mp4 [wstream]", v[0] + '|' + urllib.urlencode(dict(headers))])

    for video_url in video_urls:
        logger.info("[wstream.py] %s - %s" % (video_url[0], video_url[1]))

    return video_urls

# Encuentra vìdeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    patronvideos = r"wstream.video/(?:embed-)?([a-z0-9A-Z]+)"
    logger.info("[wstream.py] find_videos #" + patronvideos + "#")
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    for match in matches:
        titulo = "[wstream]"
        url = 'http://wstream.video/%s' % match

        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'wstream'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    return devuelve
