ARG version

FROM fluent/fluentd:${version}

LABEL Maintainer="CanDIG Project"

USER root

RUN apk add --no-cache --update --virtual .build-deps sudo build-base ruby-dev \
  && sudo gem install fluent-plugin-elasticsearch strptime \
  && sudo gem sources --clear-all \
  && apk del .build-deps \
  && rm -rf /tmp/* /var/tmp/* /usr/lib/ruby/gems/*/cache/*.gem

COPY fluent.conf /fluentd/etc/

USER fluent
