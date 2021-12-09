FROM node:14.16.0-alpine

LABEL Maintainer="CanDIG Project"

RUN apk add --no-cache git
RUN apk add --no-cache curl

COPY candig-data-portal /app/candig-data-portal

WORKDIR /app/candig-data-portal

RUN npm install

ENTRYPOINT ["npm", "start"]