# Separate base image so that we can use it to update the package-lock.json file
FROM node:14.15.4-slim AS base
WORKDIR /usr/src/app
RUN chown node:node /usr/src/app
COPY package*.json ./

# Actual dev image used for day-to-day developments
FROM base as dev
ENV NODE_ENV=development
ENV BUILD_PATH=build
RUN npm ci --verbose --production=false && npm cache clean --force
RUN apt-get update && apt-get install make
RUN npm install -g serve
USER node
COPY . .
ENTRYPOINT ["./entrypoint.sh"]

# Build production from files in dev
FROM dev as builder
ENV NODE_ENV=production
RUN npm run build

FROM node:14.15.4-slim AS production
WORKDIR /usr/src/app
RUN npm install -g serve
USER node
# install serve - deployment static server suggested by official create-react-app
# copy our build files from our builder stage
COPY --from=builder /usr/src/app/build ./build
CMD ["serve", "-s", "build", "-l", "3000"]
