FROM alpine:latest
MAINTAINER CanDIG
ENV NODE_ENV=production

WORKDIR /var/www

RUN apk update
RUN apk add nodejs yarn

ADD package.json .

RUN yarn add express --save
RUN yarn add pug --save
RUN yarn add helmet --save
RUN yarn add compression --save

ADD app.js .
COPY html /var/www/html

ENTRYPOINT ["/usr/bin/node", "app.js"]
