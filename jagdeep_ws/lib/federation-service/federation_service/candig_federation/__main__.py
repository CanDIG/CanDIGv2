#!/usr/bin/env python3

"""
Driver program for service
"""

import sys
import argparse
import logging

import connexion
from prometheus_flask_exporter import PrometheusMetrics
from flask_cors import CORS


from candig_federation.api import network


def main(args=None):
    """
    Main Routine

    Parse all the args and set up peer and service dictionaries
    """
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser('Run federation service')
    parser.add_argument('--port', default=8890)
    parser.add_argument('--host', default='ga4ghdev01.bcgsc.ca')
    parser.add_argument('--logfile', default="./log/federation.log")
    parser.add_argument('--loglevel', default='INFO',
                        choices=['DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL'])
    parser.add_argument('--services', default="./configs/services.json")
    parser.add_argument('--peers', default="./configs/peers.json")
    parser.add_argument('--schemas', default="./configs/schemas.json")



    # known args used to supply command line args to pytest without raising an error here
    args, _ = parser.parse_known_args()

    # Logging configuration

    log_handler = logging.FileHandler(args.logfile)
    numeric_loglevel = getattr(logging, args.loglevel.upper())
    log_handler.setLevel(numeric_loglevel)

    APP.app.logger.addHandler(log_handler)
    APP.app.logger.setLevel(numeric_loglevel)

    # Peer Setup

    APP.app.config["peers"] = network.parse_configs("peers", args.peers,
                                                    args.schemas, APP.app.logger)

    # Self and Local don't actually need to be mapped anymore with the new broadcast logic
    APP.app.config["self"] = "http://{}:{}".format(args.host, args.port)

    # Service Parse
    APP.app.config["services"] = network.parse_configs("services", args.services,
                                                       args.schemas, APP.app.logger)

    return APP, args.port

def configure_app():
    """
    Set up base flask app from Connexion

    App pulled out as global variable to allow import into
    testing files to access application context
    """
    app = connexion.FlaskApp(__name__, server='tornado', options={"swagger_url": "/"})


    api_def = './api/federation.yaml'

    app.add_api(api_def, strict_validation=True, validate_responses=True)

    return app


APP = configure_app()
APPLICATION, PORT = main()

# expose flask app for uwsgi

application = APPLICATION.app
metrics = PrometheusMetrics(application)
CORS(application)


if __name__ == '__main__':
    APPLICATION.app.logger.info("federation_service running at {}".format(APPLICATION.app.config["self"]))
    APPLICATION.run(port=PORT)
