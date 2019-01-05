# -*- coding: utf-8 -*-
# StreamOnDemand Community Edition - Kodi Addon
# by errmax, dr-z3r0
# Rel: 20180127
import re

from core import httptools, servertools, logger, scrapertools
from servers.decrypters import expurl


def find_videos(text):
    encontrados = {
        'https://vcrypt.net/images/logo', 'https://vcrypt.net/css/out',
        'https://vcrypt.net/images/favicon', 'https://vcrypt.net/css/open',
        'http://linkup.pro/js/jquery', 'https://linkup.pro/js/jquery',
        'http://www.rapidcrypt.net/open'
    }
    devuelve = []

    patronvideos = [
        r'(https?://(gestyy|rapidteria|sprysphere)\.com/[a-zA-Z0-9]+)',
        r'(https?://(vcrypt|linkup)\.[^/]+/[^/]+/[a-zA-Z0-9_]+)'
    ]

    for patron in patronvideos:
        logger.info(" find_videos #" + patron + "#")
        matches = re.compile(patron).findall(text)

        for url, host in matches:
            if url not in encontrados:
                logger.info("  url=" + url)
                encontrados.add(url)

                if host == 'gestyy':
                    resp = httptools.downloadpage(
                        url,
                        follow_redirects=False,
                        cookies=False,
                        only_headers=True,
                        replace_headers=True,
                        headers={'User-Agent': 'curl/7.59.0'})
                    data = resp.headers.get("location", "")
                elif host == 'vcrypt':
                    idata = httptools.downloadpage(url).data
                    patron = r"document.cookie\s=\s.*?'(.*)'"
                    # matches = re.compile(patron, re.IGNORECASE).findall(idata)
                    matches = re.finditer(patron, idata, re.MULTILINE)
                    mcookie = {}
                    for matchNum, match in enumerate(matches, start=1):
                        for c in match.group(1).split("; "):
                            c, v = c.split('=')
                            mcookie[c] = v

                    patron = r';URL=([^\"]+)\">'
                    dest = scrapertools.get_match(idata, patron)
                    import requests
                    r = requests.post(dest, cookies=mcookie)

                    url = r.url

                    if "4snip" in url:
                        desturl = url.replace("/out/", "/outlink/")
                        import os
                        par = os.path.basename(desturl)
                        rdata = requests.post(desturl, data={'url': par})
                        url = rdata.url

                    if "wstream" in url:
                        url = url.replace("/video/", "/")

                    data = url

                else:
                    data = ""
                    while host in url:
                        resp = httptools.downloadpage(
                            url, follow_redirects=False)
                        url = resp.headers.get("location", "")
                        if not url:
                            data = resp.data
                        elif host not in url:
                            data = url
                if data:
                    devuelve.append(data)
            else:
                logger.info("  url duplicada=" + url)

    patron = r"""(https?://(?:www\.)?(?:threadsphere\.bid|adf\.ly|q\.gs|j\.gs|u\.bb|ay\.gy|linkbucks\.com|any\.gs|cash4links\.co|cash4files\.co|dyo\.gs|filesonthe\.net|goneviral\.com|megaline\.co|miniurls\.co|qqc\.co|seriousdeals\.net|theseblogs\.com|theseforums\.com|tinylinks\.co|tubeviral\.com|ultrafiles\.net|urlbeat\.net|whackyvidz\.com|yyv\.co|adfoc\.us|lnx\.lu|sh\.st|href\.li|anonymz\.com|shrink-service\.it|rapidcrypt\.net)/[^"']+)"""

    logger.info(" find_videos #" + patron + "#")
    matches = re.compile(patron).findall(text)

    for url in matches:
        if url not in encontrados:
            logger.info("  url=" + url)
            encontrados.add(url)

            long_url = expurl.expand_url(url)
            if long_url:
                devuelve.append(long_url)
        else:
            logger.info("  url duplicada=" + url)

    ret = servertools.findvideos(str(devuelve)) if devuelve else []
    return ret
