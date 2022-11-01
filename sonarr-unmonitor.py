#!/usr/bin/python3
###################################
# Unmonitor Script for Sonarr
# Author : MadSurfer
# Date : 01.11.2021
# Version : 0.7b
# Description : Automatically unmonitor episde on "Import"
###################################

import logging, json, ssl
from urllib.request import Request, urlopen

from os import environ, path

SONARR_API_KEY = ""
SONARR_HOST = ""
REQ_HEADERS = {'X-Api-Key': SONARR_API_KEY, 'Content-Type': 'application/json'}

def getEpisode(episodeID):
    apireq = "{0}/api/episode/{1}".format(SONARR_HOST, episodeID)
    ssl._create_default_https_context = ssl._create_unverified_context
    request = Request(method='GET', headers=REQ_HEADERS, url=apireq)
    rep = urlopen(request)
    epData = json.load(rep)
    return epData

def setMonitoring(episodeID, MonitorStatus):
    apireq = "{0}/api/episode/{1}".format(SONARR_HOST, episodeID)
    episodeInfos = getEpisode(episodeID)
    episodeInfos["monitored"] = MonitorStatus
    request = Request(method='PUT', headers=REQ_HEADERS, data=json.dumps(episodeInfos).encode('utf-8'), url=apireq)
    rep = urlopen(request)

EventType = environ.get('sonarr_eventtype')
if EventType == 'Test':
    logging.info("Episode Unmonitor script testing")
else:
    epId = environ.get('sonarr_episodefile_episodeids')
    if epId:
        setMonitoring(epId, False)
        logMsg = "Sonarr post-import: Episode ID = {0}"
        logging.info(logMsg.format(epId))

