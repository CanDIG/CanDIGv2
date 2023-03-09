import os
import argparse

DESCRIPTION="""
Insert multiple domains into each template file in this directory.
"""

EPILOG="""
NOTES:

Tyk uses the templates in this directory to determine what other CanDIG servers
are available. Each server requires an entry into each .tpl file, which this
script helps you insert.

This script will always insert an entry for
${KEYCLOAK_PUBLIC_URL}/auth/realms/${KEYCLOAK_REALM}|${KEYCLOAK_CLIENT_ID_64}|${TYK_POLICY_ID}
, which enables the localhost to authorize itself.
"""

to_insert="""            {{
                "issuer": "{uri}/auth/realms/candig",
                "client_ids": {{
                    "{secret}": "{policy}"
                }}
            }}"""

def process_one(filename, domains, secrets, policies):
    with open(filename, "r") as r:
        try:
            text = r.read().splitlines()
        except:
            print("Could not read " + filename)
            return
        toread = -1
        for (idx, line) in enumerate(text):
            if "providers\": [" in line:
                toread = idx
                break

        # No providers entry found: skip
        if toread == -1:
            return

        # Try to find the end of the providers array
        while (toread < len(text)):
            if "]" in text[toread+1]:
                break
            text.pop(toread+1)

        # Could not find the end: skip
        if toread >= len(text):
            return

        # Insert each domain
        for (i, domain) in enumerate(domains):
            text.insert(
                toread+1+i,
                to_insert.format(uri=domain, secret=secrets[i], policy=policies[i])
                )
            if i+1 < len(domains):
                text[toread+1+i] += ","

    with open(filename, "w") as w:
        w.write("\n".join(text))
    print(f"Edited {filename}")

def main():
    parser = argparse.ArgumentParser(
        "Domain Inserter",
        description=DESCRIPTION,
        epilog=EPILOG
        )
    parser.add_argument(
        "providers",
        nargs="*",
        help="a provider in domain|secret|policy format, e.g. http://docker.localhost|VgGpzVdAjWCuuJZwNF5IzvJFnm4sWdrc|candig_policy"
        )
    args = parser.parse_args()

    domains = ["${KEYCLOAK_PUBLIC_URL}/auth/realms/${KEYCLOAK_REALM}"]
    secrets = ["${KEYCLOAK_CLIENT_ID_64}"]
    policies = ["${TYK_POLICY_ID}"]
    for server in args.providers:
        config = server.split("|")

        if len(config) != 3:
            print("Could not parse: " + server)

        domains.append(config[0])
        secrets.append(config[1])
        policies.append(config[2])

    for f in [f for f in os.listdir(".") if os.path.isfile(f) and f.endswith(".tpl")]:
        process_one(f, domains, secrets, policies)

main()
