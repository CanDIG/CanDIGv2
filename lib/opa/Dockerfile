FROM alpine/alpine:latest as fetch

RUN curl -f https://github.com/stobbsm/gohttpcheck/releases/download/v0.1/gohttpcheck-linux-amd64-v0.1 /gohttpcheck

FROM openpolicyagent/opa:latest-static as base

COPY --from=fetch /gohttpcheck /gohttpcheck
