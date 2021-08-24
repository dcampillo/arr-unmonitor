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
import syslog

from os import environ, path

RADARR_API_KEY = ""
RADARR_HOST = ""

def getMovie(movieID):
    apireq = "{0}/api/v3/movie/{1}?apikey={2}"
    rep = requests.get(apireq.format(RADARR_HOST, movieID, RADARR_API_KEY))
    return rep.json()

def setMonitoring(movieID, qualityId, moviePath, MonitorStatus):
    apireq = "{0}/api/v3/movie/{1}?moveFiles=false&apikey={2}"
    data = {'monitored' : MonitorStatus, 'id' : movieID, 'qualityProfileId' : qualityId, 'Path' : moviePath }
    payload = {'json_payload': json.dumps(data)}

    print(payload)
    rep = requests.put(apireq.format(RADARR_HOST, movieID, RADARR_API_KEY), data=json.dumps(data))
    print(rep.json())
    syslog.syslog(syslog.LOG_ERR, str(movieID))
    syslog.syslog(syslog.LOG_ERR, str(environ))

def readConfig(config_file_path):
    with open(config_file_path, "r") as f:
        return json.load(f)

# if a  json confile file argument is used, the local settings are overriden
if len(sys.argv) > 1:
    if os.path.isfile(sys.argv[1]):
        try:
            config = readConfig(sys.argv[1])
            RADARR_API_KEY = config["RADARR_API_KEY"]
            RADARR_HOST = config["RADARR_HOST"]
        except:
            print("An error occured while loading config file")
            sys.exit(-1)

EventType = environ.get('sonarr_eventtype')
movieId = 1254
if EventType == 'Test':
    logging.info("Episode Unmonitor script testing")
else:
    #movieId = environ.get("radarr_movie_id")
    if movieId:
        mov = getMovie(movieId)
        print(mov)
        qualityProfileId = mov["qualityProfileId"]
        moviePath = mov["path"]
        print(qualityProfileId)
        print(moviePath)
        setMonitoring(movieId, qualityProfileId, moviePath, False)

    #logging.info(logMsg.format(serieTitle, epSeason, epNumber, epTitle))
