# Adding a new service to CanDIGv2

If you've got a service to add from a separately-maintained repo, use these template instructions.

* Create a standalone Docker container for your service, using the Dockerfile template. Verify that your repo can spin up in a Docker container successfully.
* Create a new directory under `lib` for your service.
* Add your repo as a submodule in this directory.
* Add a docker-compose file in this directory, based on the provided template.
* Create a pull request!
