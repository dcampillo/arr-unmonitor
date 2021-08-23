#!/usr/bin/python3
###################################
# Unmonitor Script for Radarr
# Author : MadSurfer
# Date : 23.08.2021
# Version : 0.2
# Description : Automatically unmonitor episde on "Import"
###################################

import os, time, shutil, sys, logging
import requests, json
import json

from os import environ, path

RADARR_API_KEY = ""
RADARR_HOST = ""

def getMovie(movieID):
    apireq = "{0}/api/v3/movie/{1}?apikey={2}"
    rep = requests.get(apireq.format(RADARR_HOST, movieID, RADARR_API_KEY))
    return rep.json()

def setMonitoring(movieID, qualityId, moviePath, MonitorStatus):
    apireq = "{0}/api/v3/movie/{1}?moveFiles=false&apikey={2}"
    #data = {'monitored' : MonitorStatus, 'id' : movieID, 'movileFile' : { 'quality': {'quality' : { 'id' : qualityId }}}}
    data = {'monitored' : MonitorStatus, 'id' : movieID, 'qualityProfileId' : qualityId, 'Path' : moviePath }
    payload = {'json_payload': json.dumps(data)}
    rep = requests.put(apireq.format(RADARR_HOST, movieID, RADARR_API_KEY), data=json.dumps(data))
    print(rep.json())

def readConfig(config_file_path):
    with open(config_file_path, "r") as f:
        return json.load(f)

# if a  json confile file argument is used, the local settings are overriden
if os.path.isfile(sys.argv[1]):
    try:
        config = readConfig(sys.argv[1])
        RADARR_API_KEY = config["RADARR_API_KEY"]
        RADARR_HOST = config["RADARR_HOST"]
    except:
        print("An error occured while loading config file")
        sys.exit(-1)

EventType = environ.get('sonarr_eventtype')
if EventType == 'Test':
    logging.info("Episode Unmonitor script testing")
else:
    mov = getMovie(3)
    qualityProfileId = mov["qualityProfileId"]
    moviePath = mov["path"]
    setMonitoring(3, qualityProfileId, moviePath, False)

    # epId = environ.get('sonarr_episodefile_episodeids')
    # serieTitle = environ.get("sonarr_series_title")
    # epSeason = int(environ.get("sonarr_episodefile_seasonnumber"))
    # epNumber = int(environ.get("sonarr_episodefile_episodenumbers"))
    # epTitle = environ.get("sonarr_episodefile_episodetitles")

    

    
    
    #logMsg = "Radarr post-import: '{0} S{1:0>2d}E{2:0>2d} {3}' unmonitored!"
    #logging.info(logMsg.format(serieTitle, epSeason, epNumber, epTitle))