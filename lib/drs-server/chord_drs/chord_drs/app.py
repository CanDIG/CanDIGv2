import os
from bento_lib.responses import flask_errors
from flask import Flask
from flask_migrate import Migrate
from werkzeug.exceptions import BadRequest, NotFound

from chord_drs.backend import close_backend
from chord_drs.commands import ingest
from chord_drs.config import Config, APP_DIR
from chord_drs.constants import SERVICE_NAME
from chord_drs.db import db
from chord_drs.metrics import metrics
from chord_drs.routes import drs_service

MIGRATION_DIR = os.path.join(APP_DIR, "migrations")

application = Flask(__name__)
application.config.from_object(Config)

# Register exception handlers, to return nice JSON responses
# - Generic catch-all
application.register_error_handler(
    Exception,
    flask_errors.flask_error_wrap_with_traceback(flask_errors.flask_internal_server_error, service_name=SERVICE_NAME)
)
application.register_error_handler(BadRequest, flask_errors.flask_error_wrap(flask_errors.flask_bad_request_error))
application.register_error_handler(NotFound, flask_errors.flask_error_wrap(flask_errors.flask_not_found_error))

# Attach the database to the application and run migrations if needed
db.init_app(application)
migrate = Migrate(application, db, directory=MIGRATION_DIR)

# Register routes
application.register_blueprint(drs_service)

# Register application commands
application.cli.add_command(ingest)

# Add callback to handle tearing down backend when a context is closed
application.teardown_appcontext(close_backend)

# Attach Prometheus metrics exporter (if we're not in a Bento context)
with application.app_context():
    if not application.config["CHORD_URL"]:
        metrics.init_app(application)
