#!/bin/bash

echo "Starting up! Checking environment variables..."

required_env_vars=("REFRESH_TIME" "MDRC_SHEET_ID" "MDRC_DISCORD_TOKEN" "MDRC_SLACK_TOKEN" "MDRC_DISCORD_SERVER")

error_found=0

for var in "${required_env_vars[@]}"
do
  if [ -z "${!var}" ]; then
    echo "Error: Required environment variable $var is not set" >&2
    error_found=1
  fi
done

# Exit with status 1 if an error was found
if [ "$error_found" -eq 1 ]; then
  exit 1
fi

echo "Environment variables OK. Building initial TOML files..."
python matterbridge.py

status=$?

if [ $status -ne 0 ]; then
  echo "Error with python script, exiting."
  exit $status
fi
echo "Initial TOML build OK"

echo "Starting MDRC matterbridge executable in the background..."
./matterbridge-1.25.2-linux-64bit -conf=./matterbridge_mdrc.toml &
sleep 5

echo "Starting web server for health checks..."
python -m http.server --directory public &
sleep 3

echo "Continuously building TOML files..."
python matterbridge.py --continuous

status=$?

if [ $status -ne 0 ]; then
  echo "Error with python script, exiting."
  exit $status
fi