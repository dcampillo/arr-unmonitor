#!/usr/bin/python3
###################################
# Unmonitor Script for Sonarr
# Author : MadSurfer
# Date : 06.11.2021
# Version : 0.9
# Description : Automatically unmonitor episde on "Import"
# Release note: Import changes in the configuration of the script!!!
###################################

import logging, json, ssl, re, sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from os import environ, path

ARR_API_KEY = ""
ARR_HOST = ""  # example : my.domain.info
ARR_PORT = "" # default Radarr port = 8989
REQ_HEADERS = {'X-Api-Key': ARR_API_KEY, 'Content-Type': 'application/json'}
ARR_USE_SSL = False # Default = False, if set to True, configure the ARR_PORT appropriately
ARR_CHECK_SSL = True # Default = True, ARR will check the validity of the SSL Certificate

def getEpisode(episodeID):
    
    if ARR_USE_SSL:
        apireq = "https://{host}:{port}/api/episode/{epid}".format(host=ARR_HOST, port=ARR_PORT, epid=episodeID)
        if ARR_CHECK_SSL == False:
            ssl._create_default_https_context = ssl._create_unverified_context
    else:
        apireq = "http://{host}:{port}/api/episode/{epid}".format(host=ARR_HOST, port=ARR_PORT, epid=episodeID)

    request = Request(method='GET', headers=REQ_HEADERS, url=apireq)
    rep = urlopen(request)
    epData = json.load(rep)
    return epData

def setMonitoring(episodeID, MonitorStatus):
    if ARR_USE_SSL:
        apireq = "https://{host}:{port}/api/episode/{epid}".format(host=ARR_HOST, port=ARR_PORT, epid=episodeID)
    else:
        apireq = "http://{host}:{port}/api/episode/{epid}".format(host=ARR_HOST, port=ARR_PORT, epid=episodeID)
    
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

        if ARR_PORT != "":
            print("CONFIG_CHECK: PORT is set!")
        else:
            sys.stderr.write("CONFIG_CHECK ERROR ARR_PORT: ARR_PORT '' is a NOT VALID API PORT!")
            sys.exit("CONFIG_CHECK_ERROR")

    else:
        epId = environ.get('sonarr_episodefile_episodeids')
        if epId:
            setMonitoring(epId, False)
            print("Sonarr post-import: Episode ID = {episodeid}".format(episodeid=epId))

if __name__ == "__main__":
    main()