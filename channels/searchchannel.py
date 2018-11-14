# -*- coding: utf-8 -*-
# StreamOnDemand Community Edition - Kodi Addon
# ------------------------------------------------------------
# streamondemand - XBMC Plugin
# Script per la ricerca di un canale in base al testo inserito
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# by MrTruth
# ------------------------------------------------------------

import glob
import os

from core import channeltools
from core import config
from platformcode import logger
from core.item import Item


def search(item, texto):
    logger.info("[searchchannel.py] search texto=" + texto)
    itemlist = []

    directory = os.path.join(config.get_runtime_path(), "channels", '*.xml')
    files = glob.glob(directory)
    for file in files:
        file = file.replace(".xml", "")
        channel_parameters = channeltools.get_channel_parameters(file)
        if channel_parameters['active'] == True:
            file = os.path.basename(file)
            texto = texto.lower().replace("+", "")
            name = channel_parameters['title'].lower().replace(" ", "")
            if texto in name:
                itemlist.append(Item(title=channel_parameters['title'], action="mainlist", channel=file,
                                     thumbnail=channel_parameters["thumbnail"], type="generic", viewmode="movie"))

    return itemlist
