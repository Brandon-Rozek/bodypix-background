#!/bin/bash
trap "exit" INT TERM ERR
trap "kill 0" EXIT

node server.js &
python -m bodypix-background "$@"  &

wait