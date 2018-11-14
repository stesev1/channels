# -*- coding: utf-8 -*-
# StreamOnDemand Community Edition - Kodi Addon

from core import scrapertools, logger


def test_video_exists(page_url):
    logger.info("(page_url='%s')" % page_url)

    # Vídeo borrado: http://www.fileflyer.com/view/fioZRBu
    # Video erróneo: 
    data = scrapertools.cache_page(page_url)
    if '<a href="/RemoveDetail.aspx">' in data:
        return False,"Il video non è più disponibile<br/>su fileflyer.com (Video cancellato)"
    else:
        return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    data = scrapertools.cache_page(page_url)
    location = scrapertools.get_match(data,
                                      '<td class="dwnlbtn"[^<]+<a id="[^"]+" title="[^"]+" class="[^"]+" href="([^"]+)"')

    video_urls.append([scrapertools.get_filename_from_url(location)[-4:] + " [fileflyer]", location])

    for video_url in video_urls:
        logger.info("%s - %s" % (video_url[0], video_url[1]))

    return video_urls
