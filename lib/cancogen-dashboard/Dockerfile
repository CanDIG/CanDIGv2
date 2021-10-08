FROM node:14.16.0-alpine

LABEL Maintainer="CanDIG Project"

RUN apk add --no-cache git

COPY cancogen_dashboard /app/cancogen_dashboard

WORKDIR /app/cancogen_dashboard

RUN rm -rf package-lock.json .git \
	&& yarn install && yarn run build

ENTRYPOINT ["yarn", "start"]
