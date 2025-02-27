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
