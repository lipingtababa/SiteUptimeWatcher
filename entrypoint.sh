#!/bin/bash

if [[ "$RUN_AS" == "TEST_SERVER" ]]; then

    # start the test server
    uvicorn test.server.test_server:app --host 0.0.0.0 \
    --reload --timeout-keep-alive 305 \
    --log-level error --port 8000

elif [[ "$RUN_AS" == "PREPARER" ]]; then
    # Assure tables presence
    python src/prepare_environment.py

    # Generate random endpoints
    python test/client/generate_endpoints.py

else
    # Start both worker and API services
    export PARTITION_ID=1
    export PARTITION_COUNT=2
    python src/main.py & 
    python src/api/main.py &
    wait
fi
