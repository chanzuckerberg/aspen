# pull official base image
FROM python:3.7.10-slim-buster

# create directory for the app user
RUN mkdir -p /app
WORKDIR /app

COPY . .

# install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends netcat gcc pipenv
RUN pipenv install --deploy --system
