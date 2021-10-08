#!/usr/bin/env python3
"""
Driver program for service
"""
import sys
import argparse
import logging
import pkg_resources
import connexion
import json

from tornado.options import define
from candig_rnaget.api.models import BasePath
from candig_rnaget.expression.download import tmp_download, persistent_download
import candig_rnaget.orm
from prometheus_flask_exporter import PrometheusMetrics


def main(args=None):
    """The main routine."""
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser('Run RNA Get service')
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--database', default='./data/rnaget.db')
    parser.add_argument('--port', default=3000)
    parser.add_argument('--logfile', default="./log/rnaget.log")
    parser.add_argument('--loglevel', default='INFO',
                        choices=['DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL'])
    parser.add_argument('--tmpdata', default="./data/tmp/")
    args = parser.parse_args(args)

    # set up the local application
    app.app.config['BASE_DL_URL'] = 'http://'+str(args.host)+':'+str(args.port)

    # TODO: Clarify that absolute path is needed for flask.sendfile to work
    app.app.config['TMP_DIRECTORY'] = args.tmpdata

    define("dbfile", default=args.database)
    candig_rnaget.orm.init_db()
    db_session = candig_rnaget.orm.get_session()

    @app.app.teardown_appcontext
    def shutdown_session(exception=None):  # pylint:disable=unused-variable,unused-argument
        """
        Tear down the DB session
        """
        db_session.remove()

    # configure logging
    log_handler = logging.FileHandler(args.logfile)
    numeric_loglevel = getattr(logging, args.loglevel.upper())
    log_handler.setLevel(numeric_loglevel)

    app.app.logger.addHandler(log_handler)
    app.app.logger.setLevel(numeric_loglevel)

    app.run(host=args.host, port=args.port)


def configure_app():
    app = connexion.FlaskApp(__name__, server='tornado', options={"swagger_url": "/"})
    app.app.url_map.strict_slashes = False
    api_def = pkg_resources.resource_filename('candig_rnaget',
                                              'api/rnaget.yaml')

    # validate_response needs to be False due to a bug from connexion that assumes response is json when this is True
    app.add_api(api_def, strict_validation=True, validate_responses=False)
    app.add_url_rule(BasePath + '/expressions/download/<file>', 'persistent', persistent_download)
    app.add_url_rule(BasePath + '/download/<token>', 'tmp', tmp_download)

    @app.app.after_request
    def rewrite_bad_request(response):
        if response.status_code == 400 and response.data.decode('utf-8').find('"title":') != -1:
            original = json.loads(response.data.decode('utf-8'))
            response.data = json.dumps({'code': 400, 'message': original["detail"]})
            response.headers['Content-Type'] = 'application/json'
        return response

    return app


app = configure_app()

# Expose WSGI application
application = app.app
metrics = PrometheusMetrics(application)

if __name__ == "__main__":
    main()
