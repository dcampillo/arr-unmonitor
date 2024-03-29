#!/usr/bin/python3
###################################
# Unmonitor Script for Radarr
# Author : MadSurfer
# Date : 06.11.2021
# Version : 0.9
# Description : Automatically unmonitor movie on "Import"
# Release note: Import changes in the configuration of the script!!!
###################################

import logging, json, ssl, re, sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from os import environ, path

ARR_API_KEY = ""
ARR_HOST = "" # example : my.domain.info
ARR_PORT = "" # default Radarr port = 7878
REQ_HEADERS = {'X-Api-Key': ARR_API_KEY, 'Content-Type': 'application/json'}
ARR_USE_SSL = False # Default = False, if set to True, configure the ARR_PORT appropriately
ARR_CHECK_SSL = True # Default = True, ARR will check the validity of the SSL Certificate

def getMovie(movieID):
    if ARR_USE_SSL:
        apireq = "https://{host}:{port}/api/v3/movie/{movieid}".format(host=ARR_HOST, port=ARR_PORT, movieid=movieID)
        if ARR_CHECK_SSL == False:
            ssl._create_default_https_context = ssl._create_unverified_context
    else:
        apireq = "http://{host}:{port}/api/v3/movie/{movieid}".format(host=ARR_HOST, port=ARR_PORT, movieid=movieID)

    request = Request(method='GET', headers=REQ_HEADERS, url=apireq)
    
    rep = urlopen(request)
    MovieData = json.load(rep)
    return MovieData

def setMonitoring(movieID, MonitoringStatus):
    if ARR_USE_SSL:
        apireq = "https://{host}:{port}/api/v3/movie/{movieid}?moveFiles=false".format(host=ARR_HOST, port=ARR_PORT, movieid=movieID)
    else:
        apireq = "http://{host}:{port}/api/v3/movie/{movieid}?moveFiles=false".format(host=ARR_HOST, port=ARR_PORT, movieid=movieID)

    try:
        movieItem = getMovie(movieID)
        if movieItem:
            movieItem["monitored"] = MonitoringStatus
            request = Request(method='PUT', headers=REQ_HEADERS, data=json.dumps(movieItem).encode('utf-8'), url=apireq)
            rep = urlopen(request)
            sys.stdout.write("RADARR_UNMONITOR: EpisodeID:{movieid} - Unmonitored".format(movieid=movieID))
        else:
            print("Episode not found")

    except HTTPError as err:
        sys.stderr.write("RADARR_UNMONITOR: EpisodeID:{movieid} - HTTP{httpcode} - {reason}".format(movieid=movieID, httpcode=err.code, reason=err.reason))
        sys.exit(1)

    except URLError as err:
        sys.stderr.write("RADARR_UNMONITOR: EpisodeID:{movieid} - Error: {reason} | Check script configuration ARR_HOST setting".format(movieid=movieID, reason=err.reason))
        sys.exit(1)

    except Exception as err:
        sys.stderr.write("RADARR_UNMONITOR: Unknow Error RRRRRRRRRR")

def main():
    EventType = environ.get('radarr_eventtype')
    if EventType == 'Test':
        print("Checking config")
        if ARR_API_KEY != "":
            print("CONFIG_CHECK: API key is present")
        else:
            sys.stderr.write("CONFIG_CHECK API_KEY: API Key '' is a NOT VALID API KEY!")
            sys.exit("CONFIG_CHECK_ERROR")

        if ARR_PORT != "":
            print("CONFIG_CHECK: PORT is set!")
        else:
            sys.stderr.write("CONFIG_CHECK ERROR ARR_PORT: ARR_PORT '' is a NOT VALID API PORT!")
            sys.exit("CONFIG_CHECK_ERROR")

    else:
        movieId = environ.get("radarr_movie_id")
        if movieId:
            setMonitoring(movieId, False)
            print("Movie ID {movieid} unmonitored!".format(movieid=movieId))

if __name__ == "__main__":
    main()