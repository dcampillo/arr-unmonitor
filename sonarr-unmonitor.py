#!/usr/bin/python3
###################################
# Unmonitor Script for Sonarr
# Author : MadSurfer
# Date : 04.11.2021
# Version : 0.8
# Description : Automatically unmonitor episde on "Import"
###################################

import logging, json, ssl, re, sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from os import environ, path

ARR_API_KEY = ""
ARR_HOST = ""
REQ_HEADERS = {'X-Api-Key': ARR_API_KEY, 'Content-Type': 'application/json'}
ARR_USE_SSL = False

def getEpisode(episodeID):
    apireq = "{0}/api/episode/{1}".format(ARR_HOST, episodeID)
    if ARR_USE_SSL:
        ssl._create_default_https_context = ssl._create_unverified_context
    request = Request(method='GET', headers=REQ_HEADERS, url=apireq)
    rep = urlopen(request)
    epData = json.load(rep)
    return epData

def setMonitoring(episodeID, MonitorStatus):
    apireq = "{0}/api/episode/{1}".format(ARR_HOST, episodeID)
    try:
        episodeInfos = getEpisode(episodeID)
        if episodeInfos:
            episodeInfos["monitored"] = MonitorStatus
            request = Request(method='PUT', headers=REQ_HEADERS, data=json.dumps(episodeInfos).encode('utf-8'), url=apireq)
            rep = urlopen(request)
            sys.stdout.write("SONARR_UNMONITOR: EpisodeID:{epid} - Unmonitored".format(epid=episodeID))
        else:
            print("Episode not found")

    except HTTPError as err:
        sys.stderr.write("SONARR_UNMONITOR: EpisodeID:{episodeID} - HTTP{httpcode} - {reason}".format(episodeID=episodeID, httpcode=err.code, reason=err.reason))
        sys.exit(1)

    except URLError as err:
        sys.stderr.write("SONARR_UNMONITOR: EpisodeID:{episodeID} - Error: {reason} | Check script configuration ARR_HOST setting".format(episodeID=episodeID, reason=err.reason))
        sys.exit(1)

    except Exception as err:
        sys.stderr.write("SONARR_UNMONITOR: Unknow Error RRRRRRRRRR")

def main():

    EventType = environ.get('sonarr_eventtype')
    if EventType == 'Test':
        print("Checking config")
        if ARR_API_KEY != "":
            print("CONFIG_CHECK: API key is present")
        else:
            sys.stderr.write("CONFIG_CHECK API_KEY: API Key '' is a NOT VALID API KEY!")
            sys.exit("CONFIG_CHECK_ERROR")

        if re.match("^https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$", ARR_HOST):
            print("CONFIG_CHECK HOST: '{hostcheck}' is valid!".format(hostcheck=ARR_HOST))
        else:
            sys.stderr.write("CONFIG_CHECK_ERROR: {hostcheck} is NOT VALID!".format(hostcheck=ARR_HOST))
            sys.exit("CONFIG_CHECK_ERROR")
    else:
        epId = environ.get('sonarr_episodefile_episodeids')
        if epId:
            setMonitoring(epId, False)
            print("Sonarr post-import: Episode ID = {episodeid}".format(episodeid=epId))

if __name__ == "__main__":
    main()