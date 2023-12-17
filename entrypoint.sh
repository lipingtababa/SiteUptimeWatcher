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
    # get number of cores from the system
    # and use all but one for the workers
    CORES=$(( $(nproc --all) - 1 ))
    if [[ "$CORES" -lt 1 ]]; then
        CORES=1
    fi
    echo "Going to use $CORES cores"

    pids=()
    for ((i=0; i<$CORES; i++)); do
        # start CORES workers in parallel
        # set environment variable for each worker
        export PARTITION_ID=$i
        export PARTITION_COUNT=$CORES
        python src/main.py & 
        pid=($!)
        echo "Started worker $pid"
        pids+=("$pid")
    done

    # wait for all workers to finish
    for pid in "${pids[@]}"; do
        wait $pid
    done
fi
