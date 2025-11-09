#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"

docker build . \
    --no-cache \
    -t maxo5499/sportsstack-rotoreader:latest