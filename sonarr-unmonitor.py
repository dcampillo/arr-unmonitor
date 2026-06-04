#!/usr/bin/python3
###################################
# Unmonitor Script for Sonarr
# Author : MadSurfer
# Date : 06.11.2021
# Version : 1.0
# Description : Automatically unmonitor episode(s) on "Import"
# Release note: Uses Sonarr API v3 (works with Sonarr v3 and v4). See README.
###################################

import json, ssl, sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from os import environ

# --- Configuration --------------------------------------------------------
# Edit the values below, or override any of them via environment variables
# of the same name (the environment value takes precedence).
ARR_API_KEY = ""  # set your API key here (or via the ARR_API_KEY env var)
ARR_HOST = ""     # example : my.domain.info (or ARR_HOST env var)
ARR_PORT = ""     # default Sonarr port = 8989 (or ARR_PORT env var)
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


def parseEpisodeIds(raw):
    """Sonarr can pass a comma-separated list of episode IDs for multi-episode files."""
    ids = []
    for part in raw.split(","):
        part = part.strip()
        if part:
            ids.append(int(part))
    return ids


def setMonitoring(episodeIDs, MonitorStatus):
    payload = {"episodeIds": episodeIDs, "monitored": MonitorStatus}
    try:
        request = Request(method='PUT', headers=REQ_HEADERS,
                          data=json.dumps(payload).encode('utf-8'),
                          url=buildUrl("episode/monitor"))
        urlopen(request, timeout=REQ_TIMEOUT, context=getSslContext())
        sys.stdout.write("SONARR_UNMONITOR: EpisodeIDs:{epids} - Unmonitored".format(epids=episodeIDs))

    except HTTPError as err:
        sys.stderr.write("SONARR_UNMONITOR: EpisodeIDs:{epids} - HTTP{httpcode} - {reason}".format(epids=episodeIDs, httpcode=err.code, reason=err.reason))
        sys.exit(1)

    except URLError as err:
        sys.stderr.write("SONARR_UNMONITOR: EpisodeIDs:{epids} - Error: {reason} | Check script configuration ARR_HOST setting".format(epids=episodeIDs, reason=err.reason))
        sys.exit(1)

    except Exception as err:
        sys.stderr.write("SONARR_UNMONITOR: EpisodeIDs:{epids} - Unknown error: {err}".format(epids=episodeIDs, err=err))
        sys.exit(1)


def main():
    EventType = environ.get('sonarr_eventtype')
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
        rawIds = environ.get('sonarr_episodefile_episodeids')
        if rawIds:
            episodeIds = parseEpisodeIds(rawIds)
            if episodeIds:
                setMonitoring(episodeIds, False)
                print("Sonarr post-import: Episode IDs = {epids} unmonitored!".format(epids=episodeIds))


if __name__ == "__main__":
    main()
