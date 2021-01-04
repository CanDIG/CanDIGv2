## CanDIGv2 AuthZ Module

##### Configuration
See `example.env`, and create a `.env` file it's image according to your needs. 

##### Run the module

From the project directory;
- Run `make compose-authz-setup` to boot and configure all of the necessary authentication and authorization containers. These include `Tyk`, `Keycloak`, `Vault`, `OPA`, and a custom python wrapper called an `Abiter` to control access levels based on the policies registered in `OPA`
- Run `make compose-authz-clean` to shutdown all authN and authZ containers and delete their docker volumes

### Note

Please ensure the operator has root permissions accessible with `sudo`. This allows the `make compose-authz-clean` to delete the data.