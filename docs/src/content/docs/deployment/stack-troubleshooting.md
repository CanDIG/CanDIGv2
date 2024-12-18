---
title: Troubleshooting the stack
description: Troubleshooting issues with the stack
---

### Conda env not activated

If you get an error when running a make command, something like:

```bash
bash: python: command not found
```

or an error message about `dotenv` not being found.

Ensure the candig conda environment is activated in your terminal with `conda activate candig`.

### docker volumes not remade

If you get an error where after cleaning an individual service, when composing, it gets stuck at

```bash
waiting for x service to start ...
```

Use CTRL + c to exit the process then try running `make docker-volumes` and then try composing again with `make compose-<name of service>`

### No rule to make target

It is common to move around within the repo and not realise where you are. If you try to run a make command and get the error

```bash
make: *** No rule to make target `clean-candig-ingest'.  Stop.
```

Check to make sure you are in the root of the CanDIGv2 repo as the commands only work while in the same directory as the Makefile.

If you are still having trouble, feel free to [reach out to us](https://github.com/CanDIG/CanDIGv2/issues/new/choose) on GitHub.

### Common Errors

#### Uncaught server error: java.lang.NullPointerException: Cannot invoke "String.equals(Object)" because "requestHost" is null

This error occurs when a service tries to access Keycloak through [a URL that includes an underscore](https://stackoverflow.com/a/76991211/2148998). This has been known to occur when setting up reverse proxies that attempt to redirect requests to Keycloak via the container name `candigv2_keycloak_1` -- instead it is much better to use its alias `keycloak`.
