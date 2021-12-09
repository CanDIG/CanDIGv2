FROM node:14.16.0-alpine

LABEL Maintainer="CanDIG Project"

WORKDIR /app/candig-data-portal

RUN apk add --no-cache git curl

COPY candig-data-portal .

RUN npm install

ENTRYPOINT ["npm", "start"]
