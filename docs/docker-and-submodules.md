# Docker Syncing in CanDIGv2

## Docker
[Docker Getting Started](https://docs.docker.com/get-started/)

[Docker Compose](https://docs.docker.com/compose/gettingstarted/)

Each submodule will have a docker-compose.yml file and DockerFile

## Our Docker Quirks

### Syncing/Retrieving Submodule Changes 

For authx, tyk, and keycloak you need to run the clean command for your changes to be properly picked up and communicated between the modules.

```bash
make clean-authx
make init-authx
```

After making your change inside your submodules repo (example: a title change in candig-data-portal) you should be able to do the following

Current directory post changes **.../CanDIGv2/lib/module/module**

```bash
git status      # show change in submodule
cd ../../..     # change directory to CanDIGv2
docker ps       # see the name of your submodule
make build-%    # % represents the name of your module
make compose-%  # % represents the name of your module
```

You can find the name of the module from the `NAMES` column in the output from `docker ps`.

After you run these commands you should see your changes are now live. If you were making changes for candig-data-portal you will now see these on the web browser.

If you want to understand how these commands are working you can find their source code in the MakeFile in CanDIGv2.

## Submodules

The below link should give you a better understanding of submodules.

[Submodules in Git](https://git-scm.com/book/en/v2/Git-Tools-Submodules)

### Viewing all submodules

Current Directory **.../CanDIGv2**

```bash
cd lib
git submodule
```

### Status Changes to Submodules

If you wanted to see all the submodules you made changes to you could run the following. 

Current Directory **.../CanDIGv2** 
```bash
git status
```

Example output
```bash
❯ git status                                                                                                         ─╯
On branch develop
Your branch is up to date with 'origin/develop'.

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git checkout -- <file>..." to discard changes in working directory)
  (commit or discard the untracked or modified content in submodules)

        modified:   lib/candig-data-portal/candig-data-portal (new commits, modified content)
        modified:   lib/katsu/katsu_service (new commits)
        modified:   lib/federation-service/federation_service (new commits, modified content)
        modified:   lib/htsget-server/htsget_app (new commits)
        modified:   lib/opa/opa (new commits)

Untracked files:
  (use "git add <file>..." to include in what will be committed)

        docs/docker-and-syncing.md

no changes added to commit (use "git add" and/or "git commit -a")
```

This will allow you to see all the changes in your submodules under lib/ as well as any changes you made to CanDIGv2.

You can also go into each submodules individual repo to view its specific changes.
