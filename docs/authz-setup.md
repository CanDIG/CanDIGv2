## CanDIGv2 AuthZ Module

##### Configuration
Ensure a project `.env` is properly configured.

##### Run the module

From the project directory;
- Run `make compose-authx-setup-candig-server` to boot and configure a `candig-server` and all of the necessary authentication and authorization containers. These include `Tyk`, `Keycloak`, `Vault`, `OPA`, and a custom wrapper called an `Arbiter` to control access levels. It mediates inbound requests based on the policies registered in `OPA` and a resource (by default, this will be a `candig-server`, see the project `.env`).
- Run `make compose-authx-clean` to shutdown the server and all authN and authZ containers and delete their docker volumes
