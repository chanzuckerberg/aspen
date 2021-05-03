## Dockerfile for aspen batch jobs
##
##
FROM nextstrain/base
ARG REVSPEC=trunk
ARG ASPEN_DOCKER_IMAGE_VERSION
ENV ASPEN_DOCKER_IMAGE_VERSION=${ASPEN_DOCKER_IMAGE_VERSION}

RUN apt-get install -y git

WORKDIR /aspen

# Prepopulate the virtual environment by installing the dependencies of aspen as of a fixed rev.
# Assuming the dependencies do not change from the time the docker image is built to the time the
# docker image is used, this cuts startup time for the docker image.  If the dependencies DO change,
# then pip will uninstall the prepopulated dependencies and install the correct dependencies.
RUN mkdir /tmp/aspen-tmp
RUN cd /tmp/aspen-tmp
RUN git init
RUN git fetch --depth 1 git://github.com/chanzuckerberg/aspen $REVSPEC
RUN git checkout FETCH_HEAD
RUN python3.7 -m venv /aspen/.venv
RUN /aspen/.venv/bin/pip install -U pip
RUN /aspen/.venv/bin/pip install -e src/backend/third-party/sqlalchemy-enum-tables/
RUN /aspen/.venv/bin/pip install -e src/backend/
RUN cd /
RUN rm -rf /tmp/aspen-tmp

COPY docker-entrypoint.sh /usr/local/bin/
ENTRYPOINT ["docker-entrypoint.sh"]
