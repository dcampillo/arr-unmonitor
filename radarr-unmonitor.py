#!/usr/bin/python3
###################################
# Unmonitor Script for Radarr
# Author : MadSurfer
# Date : 06.11.2021
# Version : 1.0
# Description : Automatically unmonitor movie on "Import"
# Release note: Uses Radarr API v3. See README.
###################################

import json, ssl, sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from os import environ

# --- Configuration --------------------------------------------------------
# Edit the values below. ARR_API_KEY, ARR_HOST and ARR_PORT can also be
# overridden via environment variables of the same name (the environment value
# takes precedence). ARR_USE_SSL / ARR_CHECK_SSL are set here only.
ARR_API_KEY = ""  # set your API key here (or via the ARR_API_KEY env var)
ARR_HOST = ""     # example : my.domain.info (or ARR_HOST env var)
ARR_PORT = ""     # default Radarr port = 7878 (or ARR_PORT env var)
ARR_USE_SSL = False   # Default = False, if set to True, configure ARR_PORT appropriately
ARR_CHECK_SSL = True  # Default = True, verify the validity of the SSL certificate

# Environment variables take precedence over the in-file values above
ARR_API_KEY = environ.get("ARR_API_KEY", ARR_API_KEY)
ARR_HOST = environ.get("ARR_HOST", ARR_HOST)
ARR_PORT = environ.get("ARR_PORT", ARR_PORT)

REQ_HEADERS = {'X-Api-Key': ARR_API_KEY, 'Content-Type': 'application/json'}
REQ_TIMEOUT = 30  # seconds
# --------------------------------------------------------------------------


def getSslContext():
    """Return an SSLContext with verification disabled when requested, else None."""
    if ARR_USE_SSL and not ARR_CHECK_SSL:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx
    return None


def buildUrl(pathAndQuery):
    scheme = "https" if ARR_USE_SSL else "http"
    return "{scheme}://{host}:{port}/api/v3/{path}".format(
        scheme=scheme, host=ARR_HOST, port=ARR_PORT, path=pathAndQuery)


def getMovie(movieID):
    request = Request(method='GET', headers=REQ_HEADERS,
                      url=buildUrl("movie/{movieid}".format(movieid=movieID)))
    rep = urlopen(request, timeout=REQ_TIMEOUT, context=getSslContext())
    return json.load(rep)


def setMonitoring(movieID, MonitoringStatus):
    try:
        movieItem = getMovie(movieID)
        if movieItem:
            movieItem["monitored"] = MonitoringStatus
            request = Request(method='PUT', headers=REQ_HEADERS,
                              data=json.dumps(movieItem).encode('utf-8'),
                              url=buildUrl("movie/{movieid}?moveFiles=false".format(movieid=movieID)))
            urlopen(request, timeout=REQ_TIMEOUT, context=getSslContext())
            sys.stdout.write("RADARR_UNMONITOR: MovieID:{movieid} - Unmonitored".format(movieid=movieID))
        else:
            sys.stderr.write("RADARR_UNMONITOR: MovieID:{movieid} - Movie not found".format(movieid=movieID))
            sys.exit(1)

    except HTTPError as err:
        sys.stderr.write("RADARR_UNMONITOR: MovieID:{movieid} - HTTP{httpcode} - {reason}".format(movieid=movieID, httpcode=err.code, reason=err.reason))
        sys.exit(1)

    except URLError as err:
        sys.stderr.write("RADARR_UNMONITOR: MovieID:{movieid} - Error: {reason} | Check script configuration ARR_HOST setting".format(movieid=movieID, reason=err.reason))
        sys.exit(1)

    except Exception as err:
        sys.stderr.write("RADARR_UNMONITOR: MovieID:{movieid} - Unknown error: {err}".format(movieid=movieID, err=err))
        sys.exit(1)


def main():
    EventType = environ.get('radarr_eventtype')
    if EventType == 'Test':
        print("Checking config")
        if ARR_API_KEY != "":
            print("CONFIG_CHECK: API key is present")
        else:
            sys.stderr.write("CONFIG_CHECK API_KEY: API Key '' is a NOT VALID API KEY!")
            sys.exit("CONFIG_CHECK_ERROR")

        if ARR_HOST != "":
            print("CONFIG_CHECK: HOST is set!")
        else:
            sys.stderr.write("CONFIG_CHECK ERROR ARR_HOST: ARR_HOST '' is a NOT VALID HOST!")
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
