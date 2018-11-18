#!/bin/bash
#
# Build js resources for django-conversate

# Terminate script on error and print each command
set -ex

# Arguments:
#   source
#   -g uglifyify    Global transform
#   -v              Verbose
#   -s room         Standalone, available as window.room
#   -o output       Output file
browserify \
    ./static_src/js/room.js \
    -g uglifyify \
    -v \
    -s room \
    -o ./conversate/static/conversate/js/room.js

# Uglify the code
uglifyjs \
    ./conversate/static/conversate/js/room.js \
    -o ./conversate/static/conversate/js/room.js
