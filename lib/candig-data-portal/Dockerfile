ARG candig_data_portal_url
ARG katsu_api_target_url

FROM node:14.16.0-alpine as build

LABEL Maintainer="CanDIG Project"


ENV CANDIG_DATA_PORTAL_URL=$candig_data_portal_url
ENV TYK_KATSU_API_TARGET=$katsu_api_target_url


RUN apk update
RUN apk add gettext

WORKDIR /app/candig-data-portal
ENV PATH /app/candig-data-portal/node_modules/.bin:$PATH

RUN apk add --no-cache git curl

COPY candig-data-portal .

RUN npm install
RUN npm run build

ENTRYPOINT ["npm", "start"]