ARG katsu_api_target_url

FROM node:14.16.0-alpine as build

LABEL Maintainer="CanDIG Project"

ENV TYK_KATSU_API_TARGET=$katsu_api_target_url

RUN apk update && apk add gettext

WORKDIR /app/candig-data-portal
ENV PATH /app/candig-data-portal/node_modules/.bin:$PATH

RUN apk add --no-cache git curl vim

COPY candig-data-portal .

RUN npm install
RUN npm run build

ENTRYPOINT ["npm", "start"]
