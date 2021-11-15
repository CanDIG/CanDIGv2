# CanDIGv2 Authentication and Authorization Module

## Components 

- Keycloak
- Tyk

## Deploy

Make sure the relevant details in `.env` are correct.

`make init-authx`

## Clean

`make clean-authx`

## Adding New API (WIP)

Let's say the new API is called `example` and the route it redirects to us `http://example.org`. 
This section will help you figure out how to add the details to the setup but is still a work in progress.
The code to deploy a new API does not exist yet.

- Copy an API template file like `lib/tyk/configuration_templates/api_candig.json.tpl` and give it a name.
  e.g. api_example.json.tpl
- Change the appropriate pieces inside this template.
- Add the following variables to your environment file `.env`
  ```
  TYK_EXAMPLE_API_ID=666
  TYK_EXAMPLE_API_NAME=Example
  TYK_EXAMPLE_API_SLUG=example
  TYK_EXAMPLE_API_TARGET=http://example.org
  TYK_EXAMPLE_API_LISTEN_PATH=/example
  ```
  See section `## Extra APIs can be added here`
- Add the new section of the API to `lib/tyk/configuration_templates/policies.json.tpl` under
  the key `access_rights`
- Add the new section of the API tp `lib/tyk/configuration_templates/key_request.json.tpl` under 
  the key `access_rights`
- Add the new line to copy the file to the image in the `lib/tyk/Dockerfile`
- Add the new line to `envsubst` in `lib/tyk/tyk_setup.sh` (see section `# Extra APIs can be added here`)
- Redeploy the container OR use Tyk API (TODO: ask Jimmy about this)
- Regenerate the key. `lib/tyk/tyk_key_generation.sh` has clues for now. 
  If the environment variables needed by the `tyk_key_generation.sh` are set, then the script should work

## Technical Debt Notes

- This setup is flaky at best because of a myriad of styles used:
- Tyk's setup adds a `tmp` directory inside the lib/tyk which is sad because it deviates 
  from the repo's setup of a global `tmp` directory.
- Tyk's setup does not have a way via this repo/make to add new APIs or call key requests etc.
- Keycloak's setup `curl`s APIs with `-k` option which is insecure.
- Add commands to add new APIs (see above).