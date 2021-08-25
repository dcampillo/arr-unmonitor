#!/usr/bin/python3
###################################
# Unmonitor Script for Radarr
# Author : MadSurfer
# Date : 23.08.2021
# Version : 0.4
# Description : Automatically unmonitor episde on "Import"
###################################

import os, time, shutil, sys, logging
import requests, json
import logging

from os import environ, path

RADARR_API_KEY = ""
RADARR_HOST = ""
REQ_HEADERS = {'X-Api-Key': RADARR_API_KEY, 'Content-Type': 'application/json'}

def getMovie(movieID):
    apireq = "{0}/api/v3/movie/{1}"
    rep = requests.get(apireq.format(RADARR_HOST, movieID), headers=REQ_HEADERS)
    return rep.json()

def setMonitoring(movieID, MonitoringStatus):
    apireq = "{0}/api/v3/movie/{1}?moveFiles=false"
    movieItem = getMovie(movieID)
    movieItem["monitored"] = MonitoringStatus
    rep = requests.put(apireq.format(RADARR_HOST, movieID), data=json.dumps(movieItem), headers=REQ_HEADERS)

EventType = environ.get('sonarr_eventtype')
if EventType == 'Test':
    logging.info("Episode Unmonitor script testing")
else:
    movieId = environ.get("radarr_movie_id")
    if movieId:
        setMonitoring(movieId, False)
