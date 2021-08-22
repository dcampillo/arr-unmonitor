#!/usr/bin/python3
###################################
# Unmonitor Script for Sonarr
# Author : MadSurfer
# Date : 22.08.2021
# Version : 0.1
# Description : Automatically unmonitor episde on "Import"
###################################

import os, time, shutil, sys, syslog
import requests, json
import json

from os import environ, path

SONARR_API_KEY = ""
SONARR_SVR = ""

def getEpisode(episodeID):
    apireq = "{0}/api/episode/{1}?apikey={2}"
    rep = requests.get(apireq.format(SONARR_SVR, episodeID, SONARR_API_KEY))
    return rep.json()

def setMonitoring(episodeID, MonitorStatus):
    apireq = "{0}/api/episode/{1}?apikey={2}"
    data = {'monitored' : MonitorStatus, 'Id' : episodeID}
    payload = {'json_payload': json.dumps(data)}
    rep = requests.put(apireq.format(SONARR_SVR, episodeID, SONARR_API_KEY), data=json.dumps(data))

def loadConfig(config_file_path):
    with open(config_file_path, "r") as f:
        return json.load(f)

config = loadConfig("zorglub.json")
SONARR_API_KEY = config["sonarr_apikey"]
SONARR_SVR = config["sonarr_svr"]

EventType = environ.get('sonarr_eventtype')
if EventType == 'Test':
    syslog.syslog(syslog.LOG_INFO, "Episode Unmonitor script testing")
else:
    epId = environ.get('sonarr_episodefile_episodeids')
    serieTitle = environ.get("sonarr_series_title")
    epSeason = int(environ.get("sonarr_episodefile_seasonnumber"))
    epNumber = int(environ.get("sonarr_episodefile_episodenumbers"))
    epTitle = environ.get("sonarr_episodefile_episodetitles")

    setMonitoring(epId, False)
    logMsg = "Sonarr post-import: {0} S{1:0>2d}E{2:0>2d} {3} unmonitored!"
    syslog.syslog(syslog.LOG_INFO, logMsg.format(serieTitle, epSeason, epNumber, epTitle))
