FROM ubuntu:20.04
ARG DEBIAN_FRONTEND=noninteractive

LABEL maintainer = "Aspen"
LABEL description = "Image for Aspen ingest-gisaid workflow"

RUN sed -i s/archive.ubuntu.com/us-west-2.ec2.archive.ubuntu.com/ /etc/apt/sources.list; \
    echo 'APT::Install-Recommends "false";' > /etc/apt/apt.conf.d/98idseq; \
    echo 'APT::Install-Suggests "false";' > /etc/apt/apt.conf.d/99idseq

RUN apt-get -qq update && apt-get -qq -y install \
    git \
    jq \
    moreutils \
    curl \
    locales \
    zip \
    unzip \
    httpie \
    zlib1g-dev \
    libhts-dev \
    pkg-config \
    apt-utils \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    python3-yaml \
    python3-dateutil \
    virtualenv \
    awscli \
    xz-utils \
    gcc \
    && locale-gen en_US.UTF-8

RUN git clone --depth 1 git://github.com/chanzuckerberg/aspen && \
    virtualenv /aspen/.venv && \
    . /aspen/.venv/bin/activate && \
    pip install /aspen/src/backend /aspen/src/backend/third-party/sqlalchemy-enum-tables

RUN git clone --depth 1 git://github.com/nextstrain/ncov-ingest && \
    virtualenv /ncov-ingest/.venv && \
    . /ncov-ingest/.venv/bin/activate && \
    pip install -U pip pipenv && \
    pipenv install

RUN git clone --depth 1 git://github.com/nextstrain/ncov && \
    cp /aspen/src/backend/aspen/workflows/align_gisaid/config.yaml /ncov/my_profiles/align
