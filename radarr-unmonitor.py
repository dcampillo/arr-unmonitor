#!/usr/bin/python3
###################################
# Unmonitor Script for Radarr
# Author : MadSurfer
# Date : 04.11.2021
# Version : 0.8
# Description : Automatically unmonitor movie on "Import"
###################################

import logging, json, ssl, re, sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from os import environ, path

ARR_API_KEY = ""
ARR_HOST = ""
REQ_HEADERS = {'X-Api-Key': ARR_API_KEY, 'Content-Type': 'application/json'}
ARR_USE_SSL = False

def getMovie(movieID):
    apireq = "{0}/api/v3/movie/{1}".format(ARR_HOST, movieID)
    if ARR_USE_SSL:
        ssl._create_default_https_context = ssl._create_unverified_context

    request = Request(method='GET', headers=REQ_HEADERS, url=apireq)
    
    rep = urlopen(request)
    MovieData = json.load(rep)
    return MovieData

def setMonitoring(movieID, MonitoringStatus):
    apireq = "{0}/api/v3/movie/{1}?moveFiles=false".format(ARR_HOST, movieID)
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

        if re.match("^https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$", ARR_HOST):
            print("CONFIG_CHECK: '{hostcheck}' is valid!".format(hostcheck=ARR_HOST))
        else:
            sys.stderr.write("CONFIG_CHECK HOST: '{hostcheck}' is a NOT VALID HOST!".format(hostcheck=ARR_HOST))
            sys.exit("CONFIG_CHECK_ERROR")

    else:
        movieId = environ.get("radarr_movie_id")
        if movieId:
            setMonitoring(movieId, False)
            print("Movie ID {movieid} unmonitored!".format(movieid=movieId))

if __name__ == "__main__":
    main()