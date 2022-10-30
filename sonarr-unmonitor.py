#!/usr/bin/python3
###################################
# Unmonitor Script for Sonarr
# Author : MadSurfer
# Date : 22.08.2021
# Version : 0.4
# Description : Automatically unmonitor episde on "Import"
###################################

import logging
import requests, json

from os import environ, path

SONARR_API_KEY = ""
SONARR_HOST = ""
REQ_HEADERS = {'X-Api-Key': SONARR_API_KEY, 'Content-Type': 'application/json'}

def getEpisode(episodeID):
    apireq = "{0}/api/episode/{1}"
    rep = requests.get(apireq.format(SONARR_HOST, episodeID, SONARR_API_KEY), headers=REQ_HEADERS)
    return rep.json()

def setMonitoring(episodeID, MonitorStatus):
    apireq = "{0}/api/episode/{1}"
    episodeInfos = getEpisode(episodeID)
    episodeInfos["monitored"] = MonitorStatus
    payload = {'json_payload': json.dumps(episodeInfos)}
    rep = requests.put(apireq.format(SONARR_HOST, episodeID), 
        data=json.dumps(episodeInfos), 
        headers=REQ_HEADERS)
    if rep.status_code != 202:
        print("HTTP {0}".format(rep.status_code))
        print(rep.json())

EventType = environ.get('sonarr_eventtype')
if EventType == 'Test':
    logging.info("Episode Unmonitor script testing")
else:
    epId = environ.get('sonarr_episodefile_episodeids')
    if epId:
        setMonitoring(epId, False)
        logMsg = "Sonarr post-import: Episode ID = {0}"
        logging.info(logMsg.format(epId))