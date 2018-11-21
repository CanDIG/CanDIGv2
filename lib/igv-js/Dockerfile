FROM alpine:latest
MAINTAINER CanDIG

WORKDIR /root

RUN apk update && apk upgrade

RUN apk add nodejs npm

RUN npm install igv express
