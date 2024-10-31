---
title: Logging
description: Information about logging in CanDIG
---

We use Docker’s [fluentd](https://www.fluentd.org/) plugin to direct all logs to a single container running fluentd. This container is defined in `CanDIGv2/lib/logging`. All of the services are configured to send their logs to the fluentd service.

The fluentd container is configured to send its output to a file, located in `CanDIGv2/tmp/logs`. The active log file is named `buffer.*.log`, while the daily logs are rotated out to files named by date, e.g. `.20240817_0.log`.

The fluentd configuration intercepts many formats of messages sent by our various microservices, esp those we have no control over, like Opa, Tyk, and uwsgi. 

For the services we implement ourselves, we have a separate [candigv2_logging](https://github.com/CanDIG/candigv2-logging) module that should be installed on each Python-based container. This module wraps the standard Python logging library for consistency, adding a single logging format for CanDIGv2 services and decorating logged messages in a standard fashion:

- fluentd adds the container name and timestamp to all messages and includes the logged message as json

- json format is `'level: %(levelname)s, file: %(name)s, log: %(message)s'`

-  request can be included in logged messages (we handle Flask and Django-style requests for now), and if it is included, metadata keys are added: path, method, query params. If there is a logged-in user, the user’s user id and session id are included as well. This can be used for auditing data access.