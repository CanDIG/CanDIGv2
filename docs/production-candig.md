# Guide to CanDIG production deployments

Apart from the basic steps in the [CanDIGv2 Install Guide](install-candig.md) to get the candig stack up and running, there are additional settings and security recommendations that need to set up in a production level environment. We provide the following as general advice, but it is important for all CanDIG deployers to also consult with their institutional infrastructure security personnel to ensure that their deployment meets the necessary level of data security.

## Reverse Proxy & Firewall

It is essential to setup a reverse proxy and firewall so that only specific ports are open to the internet. The software used for this is up to the deployer and is considered outside of the CanDIG stack. 

Basically, the only ports that should be available are to tyk (443) and keycloak (80).

Some specific examples of how existing institutes have approached this are below.

### HAProxy - UHN & BCGSC

At UHN, the candig.uhnresearch.ca domain is under a proxy, so requests to a specific service go through the following stack:

```
[ CLIENT ] ---> | HTTPS | ---> [ UHN PROXY ] ---> | HTTP | ---> [ CANDIG_PROD / TYK ] ---> | HTTP | ---> [ CANDIG_DATA_SERVICES ]
```

Specifically, the UHN proxy forwards all candig.uhnresearch.ca and candigauth.uhnresearch.ca requests (all ports) to candig1:5080 (tyk) and candig1:8080 (keycloak) respectively, thereby acting as a firewall.  All CanDIGv2 microservices can only be accessed through Tyk.

### OpenStack security group & nginx - C3G

 OpenStack security group that allows access to ports 80 and 443 acts as a Firewall.

 nginx acts as a reverse proxy which:
 1. Re-routes http traffic to https
 2. Provides SSL certificates
 3. Routes ${CANDIG_DOMAIN} and ${CANDIG_AUTH_DOMAIN} http[s] traffic from outside to the appropriate microservice (tyk or keycloak respectively) and port.

## Virtual Machine behind Virtual Private Network

Any user that can access the VM where the CanDIG stack is running can access potentially private data. Users that have access to this VM should be strictly controlled to those users who are authorized to see any data that is ingested into the stack. One option is to use a VPN to ensure only those with access to the VPN can access the running VM. This strategy is currently being used at UHN and BCGSC.

## .env settings

The following default settings in the `.env` file should be changed when deploying CanDIG in a production environment:

| value in prod environment                                                                | function |
|------------------------------------------------------------------------------------------|----------|
| `CANDIG_DOMAIN=<your.prod.domain>`                                                       |          |
| `CANDIG_AUTH_DOMAIN=<your.prod.auth.domain>`                                             |          |
| `CANDIG_DEBUG_MODE=0`                                                                    |          |
| `CANDIG_PRODUCTION_MODE=1`                                                               |          |
| `CANDIG_SITE_LOCATION=`update to your site location                                              |          |
| `FEDERATION_SELF_SERVER` - update id, province, province-code                                                       |          |
| `KEYCLOAK_PUBLIC_PROTO=https`                                                            |          |
| `KEYCLOAK_PUBLIC_URL=${KEYCLOAK_PUBLIC_PROTO}://${CANDIG_AUTH_DOMAIN}`                   |          |
| `KEYCLOAK_PRIVATE_URL=${KEYCLOAK_PRIVATE_PROTO}://keycloak:${KEYCLOAK_PORT}`             |          |
| `TYK_LOGIN_TARGET_URL=https://${CANDIG_DOMAIN}`                                          |          |
| `TYK_USE_SSL=true`                                                                       |          |
| `CANDIG_DATA_PORTAL_URL=https://${CANDIG_DOMAIN}:${CANDIG_DATA_PORTAL_PORT}/data-portal` |          |

## Changing the default site admin

When CanDIG is initially deployed, a `site_admin` user will be created by default. The username and password for this user can be found in the `env.sh` file. It is important to change this default to a real user who should have site administration privileges. 

1. Login to the data portal with the credentials you wish to make a site administrator to ensure the user can login successfully

2. Get a site admin token using the default site admin user:

```bash
source env.sh
```

```bash
CURL_OUTPUT=$(curl -s --request POST \
  --url $KEYCLOAK_PUBLIC_URL'/auth/realms/candig/protocol/openid-connect/token' \
  --header 'Content-Type: application/x-www-form-urlencoded' \
  --data grant_type=password \
  --data client_id=$CANDIG_CLIENT_ID \
  --data client_secret=$CANDIG_CLIENT_SECRET \
  --data username=$CANDIG_SITE_ADMIN_USER \
  --data password=$CANDIG_SITE_ADMIN_PASSWORD \
  --data scope=openid)
```

```bash
export TOKEN=$(echo $CURL_OUTPUT | grep -Eo 'access_token":"[a-zA-Z0-9._\-]+' | cut -d '"' -f3)
```

3. Set the role of the real user to a site admin with the following curl command:

```bash
curl -X POST $CANDIG_URL'/ingest/site-role/admin/email/<YOUR-EMAIL-ADDRESS>' -H 'Authorization: Bearer '$TOKEN
```

4. Check the role assignment was successful by verifying the following command returns `True`:

```bash
curl -X GET $CANDIG_URL'/ingest/site-role/admin/email/<YOUR-EMAIL-ADDRESS>' -H 'Authorization: Bearer '$TOKEN
```

5. Delete the default site admin user using your new real user site admin token

```bash
CURL_OUTPUT=$(curl -s --request POST \
  --url $KEYCLOAK_PUBLIC_URL'/auth/realms/candig/protocol/openid-connect/token' \
  --header 'Content-Type: application/x-www-form-urlencoded' \
  --data grant_type=password \
  --data client_id=$CANDIG_CLIENT_ID \
  --data client_secret=$CANDIG_CLIENT_SECRET \
  --data username=<YOUR-EMAIL-ADDRESS> \
  --data password=<YOUR-PASSWORD> \
  --data scope=openid)
```

```bash
export TOKEN=$(echo $CURL_OUTPUT | grep -Eo 'access_token":"[a-zA-Z0-9._\-]+' | cut -d '"' -f3)
```

```bash
curl -X GET $CANDIG_URL'/ingest/site-role/admin/email/site_admin@test.ca' -H 'Authorization: Bearer '$TOKEN
```


## Connecting Keycloak to institutional LDAP


## Federating with other CanDIG production instances

