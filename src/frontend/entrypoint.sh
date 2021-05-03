#!/bin/bash
set -e

if [ "$1" = 'devserver' -o $# -eq 0 ]; then
    # By default run the devserver
    exec npm run devserver
fi

if [ "$1" = 'server' ]; then
    # Run the autobuilder
    exec npm start
fi

# None of the above cases, just run the command verbatim
exec "$@"
