FROM node:13.12.0-alpine

LABEL Maintainer="CanDIG Project"

COPY cancogen_dashboard /app/cancogen_dashboard

WORKDIR /app/cancogen_dashboard

RUN apk add --no-cache git && yarn set version berry

ENTRYPOINT ["yarn", "start"]
