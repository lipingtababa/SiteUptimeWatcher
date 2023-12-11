#!/bin/bash

# Prefill the database
python test/client/FillSites.py

# Run linter
pylint ./src

# Run unit test
pytest ./test -v

# start the test server
nohup uvicorn test.server.TestServer:app --host 0.0.0.0 \
    --reload --timeout-keep-alive 305 \
    --log-level error > output.log 2>&1 &

# Start the server
python src/main.py