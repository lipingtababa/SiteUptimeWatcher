#!/bin/bash


# conditional execution

if [[ "$RUN_AS" == "TEST_SERVER" ]]; then
    # Run linter
    pylint ./src

    # Run unit test
    pytest ./test -v
    # Reset the database
    python test/client/generate_endpoints.py

    # start the test server
    nohup uvicorn test.server.TestServer:app --host 0.0.0.0 \
    --reload --timeout-keep-alive 305 \
    --log-level error > /tmp/output.log 2>&1 &
else
    # Start the server
    python src/main.py
fi

