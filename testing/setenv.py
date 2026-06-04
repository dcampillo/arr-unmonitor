#!/usr/bin/python3
import os

# Single-episode import
os.environ["sonarr_episodefile_episodeids"] = "11898"

# Multi-episode import: Sonarr passes a comma-separated list of episode ids.
# Swap the line above for this one to exercise the multi-episode code path.
# os.environ["sonarr_episodefile_episodeids"] = "101,102"

os.environ["radarr_movie_id"] = "1254"
