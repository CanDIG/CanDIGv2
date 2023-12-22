# Adding a new service to CanDIGv2

For detailed instructions, see https://candig.atlassian.net/wiki/spaces/CA/pages/807731227/Creating+a+New+Microservice

If you've got a service to add from a separately-maintained repo, use these template instructions.

Start by creating a repo inside the CanDIG organisation from the [repository-template](https://github.com/new?template_name=repository-template&template_owner=CanDIG)

Brief instructions:
* Edit the provided [Dockerfile template](https://github.com/CanDIG/repository-template/blob/develop/Dockerfile). Verify that your repo can spin up in a Docker container successfully.
* Create a new directory under `lib` for your service.
* Add your repo as a submodule in this directory.
* Add a docker-compose file in this directory, based on the provided template.
* If there are files that need to be processed BEFORE the container is created, add a %_preflight.sh script based on the template.
* If there are steps that need to be performed AFTER the container is created, add a %_setup.sh script based on the template.
* Create a pull request!
