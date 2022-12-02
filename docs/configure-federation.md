# Configuring Federation Service

## Initialize Federation Service

Before running federation service, we first need to define the servers and services that is needed for the federation-service `docker-compose.yml`. The two main files that need to be created are `servers.json` and `services.json`. These files need to be added in the `/tmp/federation/` directory of the CanDIGv2 repo. See `/lib/federation-service/federation_service/configs/servers.json` and `/lib/federation-service/federation_service/configs/services.json` for examples. For the CanDIGv2 network, the `servers.json` is:

```json
{
  "servers": [
    {
      "url": "https://candigtest.bcgsc.ca/federation/search",
      "location": ["BCGSC", "British Columbia", "ca-bc"]
    },
    {
      "url": "https://candigv2.calculquebec.ca:8081/federation/search",
      "location": ["C3G", "Quebec", "ca-qc"]
    },
    {
      "url": "https://candig.uhnresearch.ca/federation/search",
      "location": ["UHN", "Ontario", "ca-on"]
    }
  ]
}
```

Services need to follow a consistent naming pattern so consult with federation site operators regarding the convention for service names. But generally, the names of services in `services.json` is the accepted naming scheme. As for the service URL, this will be the PUBLIC_URL of the corresponding data service.

Once these files are set, you can add `federation-service` to the list of `CANDIG_MODULES` in `.env` and then run `make docker-pull` or `make build-federation-service` if you want to either pull the latest federation-service image matching `FEDERATION_VERSION` or build it from source. After this, you can run `make compose-federation-service` to deploy the federation-service in the CanDIGv2 stack. You can test the service by folloring the testing steps provided in `/lib/federation-service/federation_service/README.md`.

## WSL Federation Configuration Errors
<details open>
<summary>WSL Errors</summary>

```bash
Creating candigv2_federation-service_1 ... error

ERROR: for candigv2_federation-service_1  Cannot create container for service federation-service: not a directory

ERROR: for federation-service  Cannot create container for service federation-service: not a directory
ERROR: Encountered errors while bringing up the project.
make: *** [Makefile:378: compose-federation-service] Error 1
```
If you are seeing the above directory not found error in WSL it is a issue with the communication between WSL and Windows docker in relation to the tmp folder. To get past this you need to do the following:

Current directory: **../CanDIGv2**
```bash
#Copy the servers.json and services.json into the config folder instead:
cp tmp/federation/* lib/federation-service/federation_service/configs 
```
You will need to comment out the 'secrets' section in the lib/federation-service/docker-compose.yml file. It will look like the code chunk below: 

```yml
    ...
    logging: *default-logging
    # secrets:
    #   - source: federation-servers
    #     target: /app/federation_service/configs/servers.json
    #   - source: federation-services
    #     target: /app/federation_service/configs/services.json
    entrypoint: ["uwsgi", "federation.ini", "--http", "0.0.0.0:4232"]
```
Start the federation-service up:
```bash
make build-federation-service
make compose-federation-service
```
To check that it is running you can look at the candigv2_federation-service_1 container in your Window Docker GUI. You can also run the following in terminal:
```bash
curl http://docker.localhost:4232/federation/services
```
The below output will return:
```json
{
  "candig-server": "http://docker.localhost:5080/candig",
  "htsget-app": "http://docker.localhost:5080/genomics",
  "katsu": "http://docker.localhost:5080/katsu"
}
```
</details>

## Running Federation Service Behind Tyk

Once the federation-service is running, you will need to update your tyk configuration templates in order to allow other federation servers to peer with each other. To do this, you will need to add the `issuer` and `client_ids` of the trusted nodes into any of the `api_*.json.tpl` files in `/lib/tyk/configuration_templates/`. This must be done for each service defined in `services.json` that you want federation peer(s) to access. For example, if you wanted to allow the UHN CanDIGv2 node to make federated searches to `katsu` data service, you would need to modify the `/lib/tyk/configuration_templates/api_katsu_chord.json.tpl` file and change the `providers` section to:

```json
...
    "providers": [
            {
                "issuer": "${KEYCLOAK_PUBLIC_URL}/auth/realms/${KEYCLOAK_REALM}",
                "client_ids": {
                    "${KEYCLOAK_CLIENT_ID_64}": "${TYK_POLICY_ID}"
                }
            },
            {
                "issuer": "https://candigauth.uhnresearch.ca/auth/realms/candig",
                "client_ids": {
                    "Y2FuZGlnX3Vobg==": "candig_policy"
                }
            }
        ]
    },
...
```

After you have made the necessary changes, you can apply them to your tyk instance by running `make redeploy-tyk`. Once the tyk service has be updated, you can verify the service by requesting the peer(s) to perform an HTTP request to the `/federation/servers` endpoint of your federation-service. Additionally, can request the federated peer perform a search using a OIDC jwt as a Bearer token in their request header. This may be successful, but could potentially fail if the username and access token has not been granted access through OPA.

## Where to Find Your CanDIG Node's OIDC Provider

If you have a running tyk gateway, you can see your `providers` config under `lib/tyk/tmp/apps/api_*.json`. Provide your `issuer`, `client_id`, and `tyk_policy_id` to your respective federation peers to enable federated search capabilities on their CanDIGv2 nodes.

Keep in mind, if you change your `KEYCLOAK_CLIENT_ID`, `TYK_POLICY_ID`, or `KEYCLOAK_PUBLIC_URL` in `.env` you will need to notify and provide the updated `providers` config to other CanDIGv2 nodes or you may no longer be able to run federated search.
