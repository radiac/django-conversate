#!/bin/bash
#
# Watch css resources for django-conversate

# Terminate script on error and print each command
set -ex

# Make sure it's up to date right now
npm run build-css

# Now watch for changes
node-sass \
    --include-path node_modules \
    ./static_src/scss/styles.scss \
    -w ./conversate/static/conversate/css/styles.css
