#!/bin/bash
docker build . \
    --no-cache \
    -t rotoreader:latest \
    -t maxo5499/sportsstack-rotoreader:latest