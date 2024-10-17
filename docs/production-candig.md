# Guide to CanDIG production deployments

Apart from the basic steps in the [CanDIGv2 Install Guide](install-candig.md) to get the candig stack up and running, there are additional settings and security recommendations that need to set up in a production level environment. We provide the following as general advice, but it is important for all CanDIG deployers to also consult with their institutional infrastructure security personnel to ensure that their deployment meets the necessary level of data security.

## Stable branch

Production deployments should use the latest [stable release of CanDIGv2](https://github.com/CanDIG/CanDIGv2/releases) which uses the stable branches and fixed versions of all other submodules and packages. The develop versions of CanDIG software are under active development and should not be used for production purposes. When new stable releases are made, we recommend updating as soon as possible. It is possible that CanDIG nodes running different stable releases will not be able to be federated.

## Reverse Proxy & Firewall

It is essential to setup a reverse proxy and firewall so that only specific ports are open to the internet. The software used for this is up to the deployer and is considered outside of the CanDIG stack. 

Essentially, the only two ports that should be available to the outside world are Tyk (default 5080) and Keycloak (default 8080). Usually we configure a reverse proxy so that both are on separate domains, such that e.g. https://candig.uhnresearch.ca directs to Tyk and https://candigauth.uhnresearch.ca directs to Keycloak.

Some specific examples of how existing institutes have approached this are below.

### HAProxy - UHN & BCGSC

At UHN, the candig.uhnresearch.ca domain is under a proxy, so requests to a specific service go through the following stack:

```
[ CLIENT ] ---> | HTTPS | ---> [ UHN PROXY ] ---> | HTTP | ---> [ CANDIG_PROD / TYK ] ---> | HTTP | ---> [ CANDIG_DATA_SERVICES ]
```

Specifically, the UHN proxy forwards all candig.uhnresearch.ca and candigauth.uhnresearch.ca requests (port 443) to candig1:5080 (tyk) and candig1:8080 (keycloak) respectively, thereby acting as a firewall.  All CanDIGv2 microservices can only be accessed through Tyk.

> [!Note]
> BCGSC initially had an issue with having a double proxy which caused a double URL bug. Switching to a single proxy resolved this issue. Please reach out if you need help solving this.

### OpenStack security group & nginx - C3G

 An OpenStack security group is applied as a firewall that allows ingress traffic to ports 80 and 443 only.

 nginx acts as a reverse proxy which:
 1. Re-routes http traffic to https
 2. Provides SSL certificates
 3. Routes ${CANDIG_DOMAIN} and ${CANDIG_AUTH_DOMAIN} http[s] traffic from outside to the appropriate microservice (tyk or keycloak respectively) and port.

## Virtual Machine behind Virtual Private Network

Any user that can access the VM where the CanDIG stack is running can access potentially private data. Users that have access to this VM should be strictly controlled to those users who are authorized to see any data that is ingested into the stack. One option is to use a VPN to ensure only those with access to the VPN can access the running VM. This strategy is currently being used at UHN and BCGSC.

## .env settings

The following default settings in the `.env` file should be changed when deploying CanDIG in a production environment:

| value in prod environment                                                                |
|------------------------------------------------------------------------------------------|
| `CANDIG_DOMAIN=<your.prod.domain>`                                                       |
| `CANDIG_AUTH_DOMAIN=<your.prod.auth.domain>`                                             |
| `CANDIG_DEBUG_MODE=0`                                                                    |
| `CANDIG_PRODUCTION_MODE=1`                                                               | 
| `CANDIG_SITE_LOCATION=`<your-site-location> e.g. UHN, BC                                             |
| `FEDERATION_SELF_SERVER` - update id, province, province-code see [section below](setting-location-information)                                                       |
| `KEYCLOAK_PUBLIC_PROTO=https`                                                            |
| `KEYCLOAK_PUBLIC_URL=${KEYCLOAK_PUBLIC_PROTO}://${CANDIG_AUTH_DOMAIN}`                   |
| `KEYCLOAK_PRIVATE_URL=${KEYCLOAK_PRIVATE_PROTO}://keycloak:${KEYCLOAK_PORT}`             |
| `TYK_LOGIN_TARGET_URL=https://${CANDIG_DOMAIN}`                                          |
| `TYK_USE_SSL=true`                                                                       |
| `CANDIG_DATA_PORTAL_URL=https://${CANDIG_DOMAIN}:${CANDIG_DATA_PORTAL_PORT}/data-portal` |

### Setting location information
You will need to modify the `FEDERATION_SELF_SERVER` file to reflect your site's specific settings. Set `CANDIG_SITE_LOCATION` to the name of your site, such as UHN, BCGSC, or C3G. For federation settings, set the id, name, province, and province-code for `FEDERATION_SELF_SERVER` variable in the `.env`. See table below for codes for each Canadian province and territory:

|   Province/Territory         |   province  |   province-code  |
|------------------------------|-------------|------------------|
|   Alberta                    |   AB        |   ca-ab          |
|   British Columbia           |   BC        |   ca-bc          |
|   Manitoba                   |   MB        |   ca-mb          |
|   New Brunswick              |   NB        |   ca-nb          |
|   Newfoundland and Labrador  |   NL        |   ca-nl          |
|   Northwest Territories      |   NT        |   ca-nt          |
|   Nova Scotia                |   NS        |   ca-ns          |
|   Nunavut                    |   NU        |   ca-nu          |
|   Ontario                    |   ON        |   ca-on          |
|   Prince Edward Island       |   PE        |   ca-pe          |
|   Quebec                     |   QC        |   ca-qc          |
|   Saskatchewan               |   SK        |   ca-sk          |
|   Yukon                      |   YT        |   ca-yt          |

Example values from UHN which is located in Ontario:

```bash
CANDIG_SITE_LOCATION=UHN # or your site's location
...
FEDERATION_SELF_SERVER="{'id': 'UHN', 'url': '${FEDERATION_SERVICE_URL}/${TYK_FEDERATION_API_LISTEN_PATH}','location': {'name': '${CANDIG_SITE_LOCATION}','province': 'ON','province-code': 'ca-on'}}"
```

## Setting Site Logo
To customize the site logo, you need to place your image in the candig-data-portal either before building or within the container after running the build-all or install-all commands. The image should be located at `CanDIGv2/lib/candig-data-portal/candig-data-portal/src/assets/images/users/siteLogo.png`. This will overwrite the default logo.

File requirements:
- Name the file siteLogo.png
- The image should be square and will be set to 34x34 pixels
- The image format must be PNG

If the portal is already running, copy the logo into the Docker container using this command:

```bash
 docker cp Your_images_path/siteLogo.png candigv2_candig-data-portal_1:/app/candig-data-portal/src/assets/images/users
 ```
 Otherwise:

 ```bash
 cp your_image_path/siteLogo.png CanDIGv2/lib/candig-data-portal/candig-data-portal/src/assets/images/users/siteLogo.png
 ```

## Managing user roles in CanDIG

There are currently two site level roles in CanDIG
* Site Administrator - Can do everything: ingest, delete, read all ingest endpoints
* Site Curator - Can do anything apart from editing site level roles. Can ingest, delete, read all programs at a site, can add/delete program level roles

There are currently two program level roles
* Program curator - can ingest/delete/read everything for a particular program
* Team member - read-only access to a particular program

Per-user authorizations
* Authorized user - user external to the program team who has been granted temporary authorization to one or more programs

Details about how to assign/remove roles from users is in the [candig-ingest README](https://github.com/CanDIG/candigv2-ingest/blob/develop/README.md)

### Changing the default site admin

When CanDIG is initially deployed, a `site_admin` user will be created by default. The username and password for this user can be found in the `env.sh` file. It is important to change this default to a real user who should have site administration privileges. 

1. Login to the data portal with the credentials you wish to make a site administrator to ensure the user can login successfully

2. ssh into the VM running your CanDIG deployment and cd into the currently deployed repo directory

3. Get a site admin token using the default site admin user:

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

4. Set the role of the real user to a site admin with the following curl command:

```bash
curl -X POST $CANDIG_URL'/ingest/site-role/admin/email/<YOUR-EMAIL-ADDRESS>' -H 'Authorization: Bearer '$TOKEN
```

5. Check the role assignment was successful by verifying the following command returns `True`:

```bash
curl -X GET $CANDIG_URL'/ingest/site-role/admin/email/<YOUR-EMAIL-ADDRESS>' -H 'Authorization: Bearer '$TOKEN
```

6. Delete the default site admin user using your new real user site admin token

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
curl -X DELETE $CANDIG_URL'/ingest/site-role/admin/email/site_admin@test.ca' -H 'Authorization: Bearer '$TOKEN
```

Keep the site admin user and password secure at all times.

### Adding a site curator

See [candig-ingest README](https://github.com/CanDIG/candigv2-ingest/blob/develop/README.md)

## Connecting Keycloak to institutional LDAP

You will need to work with your site IT administrator in order to connect an external authentication service to the running Keycloak.

## Federating with other CanDIG production instances

To federate your own node with another CanDIG node, follow the instructions in the [federation-service README](https://github.com/CanDIG/federation_service#how-to-register-peer-servers).

Federation is a two way process, where you need to register another server with your node, and the other node needs to register your node, by exchanging valid site administration bearer tokens.

Once two nodes are federated, summary data from federated nodes will appear in both nodes' data portals and will be viewable by all users who are able to login. 

Access to patient level data through specific program authorization is managed by the node that hosts the data for that program. For example, if a user from UHN needs to be given authorization to a program hosted within the BC node, a site administrator from BC will need to [add a program authorization](https://github.com/CanDIG/candigv2-ingest#6-adding-a-dac-style-program-authorization-for-a-user) for that UHN user to that program within the BC CanDIG node.

## Backing up production data

It is not expected that a CanDIG instance would hold the only copy of any ingested data. However, recognising that the ETL and ingest process takes significant time and effort, it is a good idea to regularly backup all data stored in CanDIG. Steps for how to do this can be found in [Backing up and restoring CanDIG data](backup-restore-candig.md)

