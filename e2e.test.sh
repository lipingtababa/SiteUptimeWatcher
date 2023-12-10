#!/bin/bash

# First of all, we have to make a list of URLs to be monitored.
./test/client/FillSites.py

# Start a local server and the Detector application.
# Please refer to the docker-compose.test.yml for more details.
docker-compose -f docker-compose.e2e.test.yml up 

