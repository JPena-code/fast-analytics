#!/usr/bin/env bash
set -e

fatal()
{
    echo "[FATAL] unable to: $*"
    exit 1
}

# TODO: handle override environment variables by cmd arguments
# or enable the final user to specify a path to a .env file
# that has to be mounted in container
export ENVIRONMENT=prod
export TIMEZONE=UTC
export APP='{"host": "0.0.0.0", "port": 8080}'

python3 -m fastanalytics || fatal "Start python app"
