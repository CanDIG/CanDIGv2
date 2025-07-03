import http.server
import os
import requests
import socketserver
from urllib.parse import urlparse

from settings import get_env

ENV = get_env()

obtained_token = ''

class CustomHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global obtained_token
        try:
            # Grab the auth code that was passed back by Keycloak
            # Looks like a GET response with http://candig.docker.internal:5080/auth/login?session_state=c09981fd-e960-4c3e-b502-e65567763962&iss=http://candig.docker.internal:8080/auth/realms/candig&code=ecb00c59-e17d-4e75-ba88-830b377a2f8d.c09981fd-e960-4c3e-b502-e65567763962.f6eb7692-9d83-4bb0-b442-4e775ede72bc
            query = urlparse(self.path).query
            query_components = dict(qc.split("=") for qc in query.split("&"))
            code = query_components["code"]

            # Grab the Keycloak secret
            with open('tmp/keycloak/client-secret', 'r') as f:
                keycloak_secret = f.read()

            # Use the auth code to generate a refresh/access token
            # and also the client secret in tmp/keycloak/client-secret
            # POST to /token
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            body = {
                "client_id": ENV['CANDIG_ENV']['KEYCLOAK_CLIENT_ID'],
                "client_secret": keycloak_secret,
                "grant_type": "authorization_code",
                "redirect_uri": ENV['CANDIG_ENV']['AUTH_ACCEPT_URL'],
                "code": code
            }
            url = f"{ENV['KEYCLOAK_REALM_URL']}/protocol/openid-connect/token"
            # print(body)
            resp = requests.post(url, data=body)

            # Parse the response to grab what we need, and output to
            # tmp/site-admin-refresh-token and tmp/site-admin-access-token
            if not resp.ok:
                raise Exception(f"Obtaining token failed with {resp.status_code}: {resp.reason} {resp.text}")
            json = resp.json()
            with open('tmp/site-admin-refresh-token', 'w') as f:
                f.write(json['refresh_token'])

            # Then pass back to the caller saying that we've finished
            self.send_response (200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes ("<html><body><h1>Login complete, please return to the command line</h1></body></html>", "utf-8"))

            obtained_token = json['refresh_token']
        except Exception as e:
            print(e)

def run(server_class=http.server.HTTPServer, handler_class=CustomHandler):
    print(ENV['CANDIG_ENV']['KEYCLOAK_CLIENT_ID'])
    server_address = (ENV['CANDIG_ENV']['CANDIG_DOMAIN'], int(ENV['CANDIG_ENV']['AUTH_ACCEPT_PORT']))
    httpd = server_class(server_address, handler_class)

    # We'll need to tell the user to access the Keycloak URL to login
    print(f"To continue, please login to the server at {ENV['KEYCLOAK_REALM_URL']}/protocol/openid-connect/auth?scope=openid+email&response_type=code&client_id=local_candig&response_mode=query&redirect_uri={ENV['CANDIG_ENV']['AUTH_ACCEPT_URL']}")

    # Tell the user what the site admin's default password is, if able
    if "DEFAULT_SITE_ADMIN_USER" in ENV['CANDIG_ENV']:
        with open("tmp/keycloak/test-site-admin-password", "r") as f:
            print(f"username: {ENV['CANDIG_ENV']['DEFAULT_SITE_ADMIN_USER']} password: {f.read()}")
    # http://candig.docker.internal:8080/auth/realms/candig/protocol/openid-connect/auth?scope=openid+email&response_type=code&client_id=local_candig&response_mode=query&redirect_uri=http://candig.docker.internal:5080/auth/login
    while not obtained_token:
        httpd.handle_request()
    return obtained_token

if __name__ == "__main__":
    run()
