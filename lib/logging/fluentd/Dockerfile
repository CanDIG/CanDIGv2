ARG BASE_IMAGE
FROM ${BASE_IMAGE}

LABEL Maintainer="CanDIG Project"

USER root

RUN gem install fluent-plugin-concat

RUN apk add --no-cache --update --virtual .build-deps sudo build-base ruby-dev \
  && sudo gem install strptime \
  && sudo gem sources --clear-all \
  && apk del .build-deps \
  && rm -rf /tmp/* /var/tmp/* /usr/lib/ruby/gems/*/cache/*.gem

COPY fluent.conf /fluentd/etc/

USER fluent
