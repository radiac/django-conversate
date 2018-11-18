#!/bin/bash
#
# Build all static assets for django-conversate

# Terminate script on error and print each command
set -ex

npm run build-js
npm run build-css
