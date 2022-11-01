#!/usr/bin/python3
###################################
# Unmonitor Script for Radarr
# Author : MadSurfer
# Date : 01.11.2021
# Version : 0.7b
# Description : Automatically unmonitor episde on "Import"
###################################

import logging, json, ssl
from urllib.request import Request, urlopen

from os import environ, path

RADARR_API_KEY = ""
RADARR_HOST = ""
REQ_HEADERS = {'X-Api-Key': RADARR_API_KEY, 'Content-Type': 'application/json'}

def getMovie(movieID):
    apireq = "{0}/api/v3/movie/{1}".format(RADARR_HOST, movieID)
    ssl._create_default_https_context = ssl._create_unverified_context
    request = Request(method='GET', headers=REQ_HEADERS, url=apireq)
    rep = urlopen(request)
    MovieData = json.load(rep)
    return MovieData

def setMonitoring(movieID, MonitoringStatus):
    apireq = "{0}/api/v3/movie/{1}?moveFiles=false".format(RADARR_HOST, movieID)
    movieItem = getMovie(movieID)
    movieItem["monitored"] = MonitoringStatus
    request = Request(method='PUT', headers=REQ_HEADERS, data=json.dumps(movieItem).encode('utf-8'), url=apireq)
    rep = urlopen(request)

EventType = environ.get('sonarr_eventtype')
if EventType == 'Test':
    logging.info("Movie Unmonitor script testing")
else:
    movieId = environ.get("radarr_movie_id")
    if movieId:
        setMonitoring(movieId, False)
