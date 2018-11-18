#!/bin/bash
#
# Build css resources for django-conversate

# Terminate script on error and print each command
set -ex

# Compile all scss files into css files
node-sass \
    --include-path node_modules \
    ./static_src/scss/ \
    --output ./conversate/static/conversate/css/ \
    --sourcemap \
    --no-recursive

# Uglify all CSS files
find \
    ./conversate/static/conversate/css/ \
    -iname \"*.css\" \
    -print \
    -exec \
        sh \
        -c 'uglifycss \"$1\" > \"$1.tmp\" && rm \"$1\" && mv \"$1.tmp\" \"$1\"' \
        -- {} \
    \;
