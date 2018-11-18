#!/bin/bash
#
# Watch js resources for django-conversate

# Terminate script on error and print each command
set -ex

watchify \
    -vd \
    -p \
    browserify ./static_src/js/room.js \
    -o ./conversate/static/conversate/js/room.js \
    -v \
    -d \
    -s room \
    --poll
