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
if [[ -z "$ENVIRONMENT" ]]; then
    export ENVIRONMENT="prod"
fi
if [[ -z "$TIMEZONE" ]]; then
    export TIMEZONE=UTC
fi
if [[ -z  "$APP" || -z "$APP__HOST" || -z "$APP__PORT" ]]; then
    export APP='{"host": "0.0.0.0", "port": 8080}'
fi

python3 -m fastanalytics || fatal "Start python app"
