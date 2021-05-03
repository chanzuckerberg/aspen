#!/usr/bin/env bash
set -Eeuo pipefail

if [ $# -lt 1 ]; then
    echo "To activate virtual env, run: "
    echo "% source /aspen/.venv/bin/activate\""

    bash
elif [ $# -lt 2 ]; then
    # uh what?
    echo "Usage: <revspec> <script> [<scriptarg> ...]"
    echo "    Checks out <revspec> on aspen and run <script>"
    echo "Usage:"
    echo "    Interactive shell."
    exit 1
else
    export ASPEN_GIT_REVSPEC="$1"

    git init
    git fetch --depth 1 git://github.com/chanzuckerberg/aspen "$ASPEN_GIT_REVSPEC"
    git checkout FETCH_HEAD

    /aspen/.venv/bin/pip install -U pip
    /aspen/.venv/bin/pip install -e src/backend/third-party/sqlalchemy-enum-tables/
    /aspen/.venv/bin/pip install -e src/backend/

    shift
    $*
fi
