#!/bin/bash

if [[ "$RUN_AS" == "TEST_SERVER" ]]; then
    # start the test server
    cd /app
    PYTHONPATH=/app uvicorn test.server.test_server:app --host 0.0.0.0 --port 8001 --log-level error

elif [[ "$RUN_AS" == "PREPARER" ]]; then
    # Assure tables presence
    cd /app
    python -m src.prepare_environment

    # Generate random endpoints
    python -m test.client.generate_endpoints

else
    # Start both worker and API services
    export PARTITION_ID=1
    export PARTITION_COUNT=2
    cd /app
    PYTHONPATH=/app python -m src.worker.main & 
    PYTHONPATH=/app uvicorn src.api.main:app --host 0.0.0.0 --port 8080 --reload &
    wait
fi
