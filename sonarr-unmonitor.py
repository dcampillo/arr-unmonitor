#!/usr/bin/python3
###################################
# Unmonitor Script for Sonarr
# Author : MadSurfer
# Date : 22.08.2021
# Version : 0.2
# Description : Automatically unmonitor episde on "Import"
###################################

import os, time, shutil, sys, logging
import requests, json
import json

from os import environ, path

SONARR_API_KEY = ""
SONARR_HOST = ""

def getEpisode(episodeID):
    apireq = "{0}/api/episode/{1}?apikey={2}"
    rep = requests.get(apireq.format(SONARR_HOST, episodeID, SONARR_API_KEY))
    return rep.json()

def setMonitoring(episodeID, MonitorStatus):
    apireq = "{0}/api/episode/{1}?apikey={2}"
    #data = {'monitored' : MonitorStatus, 'Id' : episodeID}
    data = getEpisode(episodeID)
    data["monitored"] = MonitorStatus
    payload = {'json_payload': json.dumps(data)}
    rep = requests.put(apireq.format(SONARR_HOST, episodeID, SONARR_API_KEY), data=json.dumps(data))

def readConfig(config_file_path):
    with open(config_file_path, "r") as f:
        return json.load(f)

# if a  json confile file argument is used, the local settings are overriden
if os.path.isfile(sys.argv[1]):
    try:
        config = readConfig(sys.argv[1])
        SONARR_API_KEY = config["SONARR_API_KEY"]
        SONARR_HOST = config["SONARR_HOST"]
    except:
        print("An error occured while loading config file")
        sys.exit(-1)

EventType = environ.get('sonarr_eventtype')
if EventType == 'Test':
    logging.info("Episode Unmonitor script testing")
else:
    epId = environ.get('sonarr_episodefile_episodeids')
    serieTitle = environ.get("sonarr_series_title")
    epSeason = int(environ.get("sonarr_episodefile_seasonnumber"))
    epNumber = int(environ.get("sonarr_episodefile_episodenumbers"))
    epTitle = environ.get("sonarr_episodefile_episodetitles")

    setMonitoring(epId, False)
    logMsg = "Sonarr post-import: '{0} S{1:0>2d}E{2:0>2d} {3}' unmonitored!"
    logging.info(logMsg.format(serieTitle, epSeason, epNumber, epTitle))
