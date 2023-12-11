#!/bin/bash

# Run linter
pylint ./src

# Run unit test
pytest ./test -v

# conditional execution

if [[ "$RUN_AS" == "TEST_SERVER" ]]; then
    # Reset the database
    python test/client/generate_endpoints.py

    # start the test server
    uvicorn test.server.test_server:app --host 0.0.0.0 \
    --reload --timeout-keep-alive 305 \
    --log-level error --port 8000
else
    # Wait for the test server to start
    sleep 5

    # Start the server
    python src/main.py
fi

