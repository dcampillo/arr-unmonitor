
# Arr-Unmonitor
Sonarr/Radarr custom scripts to unmonitor episodes or movies after import.

> **v1.0** — The Sonarr script now uses the Sonarr API **v3** endpoint
> (`/api/v3/episode/monitor`) and works with **Sonarr v3 and v4**. It also
> correctly handles multi-episode imports. The Radarr script uses Radarr API v3.

## Requirements
- Python 3.x is recommended
- The script have been tested with Python 3.8.x and  3.9.x

## Installation
Update each script accordingly:

 1. Place the scripts in a folder accessible by Radarr or Sonarr
 2. !! For "Linux", make the script executable
 3. Settings to be set in the script:
	 1. ARR_API_KEY = ""
	 2. ARR_HOST = "" # example : my.domain.info
	 3. ARR_PORT = "" # default Radarr port = 7878 / default Sonarr port = 8989
	 5. ARR_USE_SSL = False # Default = False, if set to True, configure the ARR_PORT appropriately
	 6. ARR_CHECK_SSL = True # Default = True, ARR will check the validity of the SSL Certificate

> **Tip:** Instead of editing the script, you can override `ARR_API_KEY`,
> `ARR_HOST` and `ARR_PORT` via environment variables of the same name — handy
> for keeping the API key out of the file. The environment value takes
> precedence over the in-file value.


## Sonarr / Radarr configuration
1. Add a new connection (Settings -> Connect -> Custom Scripts)
2. Give a name to your connection
3. Check the Notification Trigger "on import"
4. Select your script
5. If the script is accessible/executable by Sonarr/Radarr, you should see a green "Check" after clicking on the button "Test"
