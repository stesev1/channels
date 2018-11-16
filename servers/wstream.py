# -*- coding: utf-8 -*-
# StreamOnDemand Community Edition - Kodi Addon
# by DrZ3r0

import re
import urllib

import xbmc
from core import httptools, scrapertools, logger

headers = [['User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0']]


# Returns an array of possible video url's from the page_url
def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("[wstream.py] get_video_url(page_url='%s')" % page_url)
    video_urls = []
    vid_urls = []
    
    data = httptools.downloadpage(page_url, headers=headers).data

    xbmc.sleep(4 * 1000)

    patronsources='sources\:\s*\[["\']\s*(https?:\/\/[^>]+?wstream.*?)\s*["\']\]'
    video_url = scrapertools.find_single_match(data, patronsources)
    if not video_url:
        data_pack = scrapertools.find_single_match(data, "(eval.function.p,a,c,k,e,.*?)\s*</script>")

        if data_pack != "":
            from lib import jsunpack
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