#!/bin/bash
#
# Watch all static assets for django-conversate

# Terminate script on error and print each command
set -ex

npm-run-all --parallel watch-js watch-css
