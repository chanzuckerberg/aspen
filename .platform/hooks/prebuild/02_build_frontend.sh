#!/bin/bash
set -x

export NVM_DIR="${HOME}/.nvm"

source "${NVM_DIR}/nvm.sh"

npm --prefix src/frontend run build
