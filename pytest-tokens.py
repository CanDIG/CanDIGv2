#!/usr/bin/env python3

import os
import auth_code_acceptor

print("""
NOTE:
In order to properly run pytest without ROPC, we will need you to sign into
Keycloak three times with the given credentials. Please use a new incognito
window for each
""")

admin_username = os.getenv("CANDIG_SITE_ADMIN_USER", "your site admin username")
admin_token = auth_code_acceptor.run(
    admin_username,
    os.getenv("CANDIG_SITE_ADMIN_PASSWORD", "your site admin password"))
user1_username = os.getenv("CANDIG_NOT_ADMIN_USER")
user1_token = auth_code_acceptor.run(
    user1_username, os.getenv("CANDIG_NOT_ADMIN_PASSWORD")
    )
user2_username = os.getenv("CANDIG_NOT_ADMIN2_USER")
user2_token = auth_code_acceptor.run(
    user2_username, os.getenv("CANDIG_NOT_ADMIN2_PASSWORD")
    )

# NB: Grabbing a new admin token will invalidate the existing one, so we need to
# write over the site-admin-refresh-token file as well
with open(f"tmp/site-admin-refresh-token", "w") as f:
    f.write(admin_token)
with open(f"tmp/pytest-{admin_username}-token", "w") as f:
    f.write(admin_token)
with open(f"tmp/pytest-{user1_username}-token", "w") as f:
    f.write(user1_token)
with open(f"tmp/pytest-{user2_username}-token", "w") as f:
    f.write(user2_token)
