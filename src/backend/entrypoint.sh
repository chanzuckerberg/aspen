#!/bin/bash
set -e

if [ "$1" = 'cli' ]; then
    shift
    exec aspen-cli "$@"
fi

if [ "$1" = 'server' -o $# -eq 0 ]; then
    # By default run the server
    # Bind to 0.0.0.0 to expose outside of Docker container
    exec flask run --host 0.0.0.0 --port 3000
fi

# None of the above cases, just run the command verbatim
exec "$@"
