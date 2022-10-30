# Arr-Unmonitor
Sonarr/Radarr custom scripts to unmomitor episodes or movies after import.

## Requirements
- Python 3.x is recommended
- The script have been tested with Python 3.8.x and  3.9.x

## Installation
Requireds depedencies are listed in requirements.txt
- to install the depedencies: pip install -r requirements.txt

You can use the script with or without a configuration file:

1. Place the scripts in a folder accessible by Radarr or Sonarr
2. !! For "Linux", make the script executable
3. Update variable 'SONARR_HOST' and 'SONARR_API_KEY' in "sonarr-unmonitor.py" for Sonarr
4. Update variable 'RADARR_HOST' and 'RADARR_API_KEY' in "radarr-unmonitor.py" for Radarr

## Sonarr / Radarr configuration
1. Add a new connection (Settings -> Connections -> Custom Scripts)
2. Give a name to your connection
3. Check the Notification Trigger "on import"
4. Select your script
5. If the script is accessible/executable by Sonarr/Radarr, you should see a green "Check" after clicking on the button "Test"
