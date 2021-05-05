# Separate base image so that we can use it to update the package-lock.json file
FROM node:14.15.4-slim AS base
WORKDIR /usr/src/app
RUN chown node:node /usr/src/app
COPY package*.json ./
ENV NODE_ENV=development
ENV BUILD_PATH=build
RUN npm i --verbose
RUN apt-get update && apt-get install make
RUN npm install -g serve
USER node
COPY . .
ENTRYPOINT ["./entrypoint.sh"]
