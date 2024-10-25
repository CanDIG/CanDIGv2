import authx.auth
import os
import getpass
from settings import get_env

ENV = get_env()

def get_site_admin_token(username=None, password=None, refresh_token=None):
    # look for refresh token
    if refresh_token is None:
        if os.path.isfile("tmp/site-admin-refresh-token"):
            with open("tmp/site-admin-refresh-token") as f:
                refresh_token = f.read().splitlines().pop()
            os.remove("tmp/site-admin-refresh-token")

    # if no refresh token, get one:
    # check for default site admin user: if not present, check env vars
    username = os.getenv("CANDIG_SITE_ADMIN_USER")
    password = os.getenv("CANDIG_SITE_ADMIN_PASSWORD")
    # site admin user/password need to be inputted on stdin if not default:
    if password is None or password == "":
        username = input("Enter username: ")
        password = getpass.getpass("Enter password: ")

    try:
        credentials = authx.auth.get_oauth_response(
            keycloak_url=ENV["KEYCLOAK_PUBLIC_URL"],
            client_id=ENV["CANDIG_CLIENT_ID"],
            client_secret=ENV["CANDIG_CLIENT_SECRET"],
            username=username,
            password=password,
            refresh_token=refresh_token
            )

        if "error" in credentials:
            try:
                os.remove("tmp/site-admin-refresh-token")
            except FileNotFoundError:
                pass
            except Exception as e:
                print(str(e))
                print(type(e))
            return get_site_admin_token()

        with open(f"tmp/site-admin-refresh-token", "w") as f:
            f.write(credentials["refresh_token"])

        return credentials["access_token"]
    except Exception as e:
        try:
            os.remove("tmp/site-admin-refresh-token")
        except:
            pass
        raise authx.auth.CandigAuthError(f"Error obtaining response from keycloak server: {e}")

if __name__ == "__main__":
    result = get_site_admin_token()
    print(result)
