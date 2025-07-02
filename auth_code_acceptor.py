import http.server
import os
import requests
import socketserver
from urllib.parse import urlparse

response_handled = False

class CustomHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global response_handled
        # Grab the auth code that was passed back by Keycloak
        # Looks like a GET response with http://candig.docker.internal:5080/auth/login?session_state=c09981fd-e960-4c3e-b502-e65567763962&iss=http://candig.docker.internal:8080/auth/realms/candig&code=ecb00c59-e17d-4e75-ba88-830b377a2f8d.c09981fd-e960-4c3e-b502-e65567763962.f6eb7692-9d83-4bb0-b442-4e775ede72bc
        query = urllib.parse(self.path)
        query_components = dict(qc.split("=") for qc in query.split("&"))
        code = query_components["code"]

        # Use the auth code to generate a refresh/access token
        # and also the client secret in tmp/keycloak/client-secret
        # POST to /token
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        body = {
            "client_id": os.environ['KEYCLOAK_CLIENT_ID'],
            "client_secret": os.environ['KEYCLOAK_SECRET'],
            "grant_type": "authorization_code",
            "redirect_uri": os.environ['AUTH_ACCEPT_URL'],
            "code": code
        }
        resp = requests.post(f"{os.environ['KEYCLOAK_PRIVATE_URL']}{os.environ['KEYCLOAK_AUTH_PREFIX']}/realms/{os.environ['KEYCLOAK_REALM']}/protocol/openid-connect/token",
                      json=body)

        # Parse the response to grab what we need, and output to tmp/site-admin-refresh-token

        # Then pass back to the caller saying that we've finished
        response_handled = True

def run(server_class=http.server.HTTPServer, handler_class=CustomHandler):
    server_address = ('0.0.0.0', int(os.environ['AUTH_ACCEPT_PORT']))
    httpd = server_class(server_address, handler_class)
    # We'll need to tell the user to access the Keycloak URL to login
    print(f"To continue, please login to the server at {os.environ['KEYCLOAK_REALM_URL']}/protocol/openid-connect/auth?scope=openid+email&response_type=code&client_id=local_candig&response_mode=query&redirect_uri={os.environ['AUTH_ACCEPT_URL']}")
    if "DEFAULT_SITE_ADMIN_USER" in os.environ:
        with open("tmp/keycloak/test-site-admin-password", "r") as f:
            print(f"username: {os.environ['DEFAULT_SITE_ADMIN_USER']} password: {f.read()}")
    # http://candig.docker.internal:8080/auth/realms/candig/protocol/openid-connect/auth?scope=openid+email&response_type=code&client_id=local_candig&response_mode=query&redirect_uri=http://candig.docker.internal:5080/auth/login
    while not response_handled:
        httpd.handle_request()

run()
