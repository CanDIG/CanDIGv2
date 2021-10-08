"""
Auth module for service
"""

import flask

from candig_dataset_service.api.logging import structured_log as struct_log
from candig_dataset_service.api.logging import logger


def _report_proxy_auth_error(key, **kwargs):
    """
    Generate standard log message for warning:
    API access without
    :param **kwargs: arbitrary keyword parameters
    """
    message = 'Attempt to access with invalid proxy/api key: ' + key
    logger().warning(struct_log(action=message, **kwargs))


def auth_key(api_key, required_scopes=None):
    fc = flask.current_app.config
    # Allow CanDIG API gateway to handle auth (not for standalone use)
    if fc.get('AUTH_METHOD') == 'GATEWAY':
        # TODO: use gateway client certificate instead
        fh = flask.request.headers
        if not fh["Host"] == fc.get('GATEWAY_HOST'):
            _report_proxy_auth_error(api_key)
            return None
    # For now, any api_key to local app should work
    # TODO: refine auth methods
    return {}