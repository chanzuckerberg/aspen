#!/bin/bash
set -x

export NVM_DIR="${HOME}/.nvm"
# We want to be on the latest Active LTS; but should
# set this value manually, so we can test it beforehand
export NODE_VERSION=$(cat .nvmrc)

# Install nvm
if [[ ! -f "${NVM_DIR}/nvm.sh" ]]; then
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.37.2/install.sh | bash
fi

# Activate nvm
source "${NVM_DIR}/nvm.sh"

# Install our preferred Node version
# Make sure we are using that version, and also
# make our version the default
if [[ $(nvm current) != "v${NODE_VERSION}" ]]; then
    nvm install ${NODE_VERSION}
    nvm alias default ${NODE_VERSION}
    nvm use ${NODE_VERSION}
fi

# Install Frontend dependencies
npm --prefix src/frontend ci
