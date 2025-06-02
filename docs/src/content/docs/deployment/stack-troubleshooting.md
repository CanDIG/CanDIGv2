---
title: Troubleshooting the stack
description: Troubleshooting issues with the stack
next: false
---

## Integration tests failing

If any integration tests fail, it is usually best to go back to the first test that failed, as subesquent tests often rely on earlier tests passing to succeed. Therefore the root cause is usually with the first failure.

If `test_tyk` fails, all other tests will fail because the stack relies on tyk being up and running as expected. If you see `test_tyk` fail, you may as well `ctrl+c` to stop the tests running and start investigating the issue with tyk. Some places to start looking for the issue are:
- is the tyk container up and running?
  - check your docker desktop or `docker ps` to see if tyk and all other containers are running
- is there anything in the tyk docker logs that indicates an issue?
  - view the logs with `docker logs candigv2_tyk_1` or in Docker desktop
  - if anything looks amiss, make a github issue with the details
- did anything go wrong in the build logs?
  - the build log can be found in `tmp/error.txt` 
- is anything else in the central logs looking weird?
  - the central logs for all docker containers can be found in `/tmp/logs/`, the most current one will be named with `buffer.<uuid>.log` whereas previous days' logs are named `.yyyymmdd_0.log`
 
If any of the `ingest_admin_*` tests fail, the later query tests will fail since they rely on having data ingested into the system to get the expected query results.

If any specific test is failing, looking at the individual container for the services that is failing, or the centralized log (`/tmp/logs`) is usually the best place to start debugging. If at any stage you are unsure on where to start after integration test failures, please make a [github issue](https://github.com/CanDIG/CanDIGv2/issues/new/choose).

If a failure relates to any of the services listed in the `CANDIG_AUTH_MODULES` in the `.env` file, and you find you need to rebuild any of these modules, you will need to rebuild all of these modules using `make clean-authx` and `make init-authx`. 

## Conda env not activated

If you get an error when running a make command, something like:

```bash
bash: python: command not found
```

or an error message about `dotenv` not being found.

Ensure the candig conda environment is activated in your terminal with `conda activate candig`.

## docker volumes not remade

If you get an error where after cleaning an individual service, when composing, it gets stuck at

```bash
waiting for x service to start ...
```

Use CTRL + c to exit the process then try running `make docker-volumes` and then try composing again with `make compose-<name of service>`

## No rule to make target

It is common to move around within the repo and not realise where you are. If you try to run a make command and get the error

```bash
make: *** No rule to make target `clean-candig-ingest'.  Stop.
```

Check to make sure you are in the root of the CanDIGv2 repo as the commands only work while in the same directory as the Makefile.

If you are still having trouble, feel free to [reach out to us](https://github.com/CanDIG/CanDIGv2/issues/new/choose) on GitHub.

### Common Errors

#### Uncaught server error: java.lang.NullPointerException: Cannot invoke "String.equals(Object)" because "requestHost" is null

This error occurs when a service tries to access Keycloak through [a URL that includes an underscore](https://stackoverflow.com/a/76991211/2148998). This has been known to occur when setting up reverse proxies that attempt to redirect requests to Keycloak via the container name `candigv2_keycloak_1` -- instead it is much better to use its alias `keycloak`.

#### Unauthorized {'type': 'about:blank', 'title': 'Method Not Allowed', 'detail': 'Method Not Allowed', 'status': 405}

On federated systems, this may occur when the URL given to Federation contains a trailing `'/'` in it. It is currently unknown why this occurs

## Tyk provider issues

In the logs you are getting errors such as the below when trying to access any endpoints.

e.g.:
```bash
level=warning msg="JWT Invalid" api_id=91 api_name=federation error="Validation error. Validation error. The provider https://<$CANDIG_AUTH_DOMAIN>/auth/realms/candig does not have a client id matching any of the token audiences [https://<$CANDIG_AUTH_DOMAIN>/auth/realms/candig]" mw=OpenIDMW org_id= origin=10.9.234.195 path=/federation/v1/service-info
time="Apr 01 18:45:40" level=warning msg="Attempted access with invalid key." api_id=91 api_name=federation key="****JWT]" mw=OpenIDMW org_id= origin=10.9.234.195 path=/federation/v1/service-info
```
Check your tyk config files for anything that looks weird, e.g.
`lib/tyk/tmp/apps/91.json` has the correct issuer and client_ids as configured in your `.env`

Should be something like:

```json
"providers": [
            {
                "issuer": "https://<$CANDIG_AUTH_DOMAIN>",
                "client_ids": {
                    "<$KEYCLOAK_CLIENT_ID in base64 encoding>": "candig_policy"
                }
            }
        ]
```

For the client id, as an example, if you kept the default value for `KEYCLOAK_CLIENT_ID` (`local_candig`) in the `example.env`, the value would be 

```bash
echo -n "local_candig" | base64
bG9jYWxfY2FuZGln
```

Check your `.env` does not have any issues with parsing invisible white space or comments.

## Tyk cannot find secret key

Your stack doesn't seem to be working and there are tyk related error messages such as `Key not authorised` even though you believe you are using a valid token.

Double check your build log (`tmp/progress.txt`) for messages such as: 
```
cat: /opt/CanDIGv2/tmp/tyk/secret-key: No such file or directory
mv: cannot stat 'tmp/secrets/tyk-secret-key': No such file or directory
cat: /opt/CanDIGv2/tmp/tyk/secret-key: No such file or directory
```

To fix, try regenerating the tyk secret with `make secret-tyk-secret-key`.

Then recompose both tyk and federation with:

```
make recompose-tyk
make recompose-federation
```

## Opa returns 401 Unauthorized

Sometimes 401 Unauthorized errors are caused by Opa not being able to find the data it needs to validate the bearer token. These will have a message of "request rejected by administrative policy" and will not leave any decisions in the log.

These are caused by Opa's master system.authz policy rejecting access to any downstream policies, including all of CanDIG's permission policies. Usually, this is happening because Opa can't access its Vault service store or the IDP. Try re-running `make compose-opa` to reconnect the Opa containers to Vault.

If you are still having trouble diagnosing the problem, you can temporarily set Opa's system.authz authorization to allow all requests by default:
```
# Reject requests by default
default allow := false # switch this to true
```
Then run `make recompose-opa`. You can then access the endpoints `/v1/data/idp`, `/v1/data/vault`, and `/v1/data/calculate`, which allows you to see more details about the internal logic of Opa's decisionmaking.

Be sure to switch `default allow` back to False when you're done.
