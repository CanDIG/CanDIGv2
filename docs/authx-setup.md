# CanDIGv2 Authentication and Authorization Module

## Components 

- Keycloak
- Tyk

## Deploy

Make sure the relevant details in `.env` are correct.

`make init-authx`

## Clean

`make clean-authx`

## Technical Debt Notes

- This setup is flaky at best because of a myriad of styles used:
- Tyk's setup adds a `tmp` directory inside the lib/tyk which is sad because it deviates 
  from the repo's setup of a global `tmp` directory.
- Tyk's setup does not have a way via this repo/make to add new APIs or call key requests etc.
- Keycloak's setup `curl`s APIs with `-k` option which is insecure.