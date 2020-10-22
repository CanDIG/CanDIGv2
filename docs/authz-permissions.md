# Authorization Permissions

JWTs that are sent by Vault contain permissions for OPA to act on. This
document notes the details of the structure of the JWTs and other related
information.

- TODO: Ask Ksenia for the final CanDIG model
- TODO: Perform checks on Vault tokens

## JWT

- `iss`: Issuer 
- `iat`: Issued time
- `exp`: Expiration time
- `jti`: Token ID
- `sub`: Suject ID (TODO: how to link to IdP's ID)
- `ga4gh_passport_v1`: List of the visas, could easily just be one item
  for now but the idea is to use GA4GH terminology. Child `ga4gh_visa_v1`.
  - `ga4gh_visa_v1`: a JWT with items
    - `type`: Either of these (there are more but we need these)
      - `LinkedIdentities`: [LinkedIdentities, GA4GH]
      - `ControlledAccessGrants`: [ControlledAccessGrants, GA4GH]
    - `value`: A string that represents any of the scope,
      process, identifier and version of the assertion. The format of
      the string can vary by the Passport Visa Type.
      For CanDIG, we perhaps need the value to be the dataset ID and
      level of the access. (TODO: data spec from Ksenia will help)
    - `source`: A URL Field that provides at a minimum the
      organization that made the assertion. If there is no organization making
      the assertion, the "source" MUST be set to "https://no.organization".
    - `asserted`: time at assertion
    - `by`; [by field, GA4GH] (TODO: specify who? self? dac?)
    - `iss`: 
    - `sub`:
    - `iat`:
    - `exp`:


## References

- GA4GH Passport V1: https://github.com/ga4gh-duri/ga4gh-duri.github.io/blob/master/researcher_ids/ga4gh_passport_v1.md#by


[LinkedIdentities, GA4GH]: https://github.com/ga4gh-duri/ga4gh-duri.github.io/blob/master/researcher_ids/ga4gh_passport_v1.md#linkedidentities
[ControlledAccessGrants, GA4GH]: https://github.com/ga4gh-duri/ga4gh-duri.github.io/blob/master/researcher_ids/ga4gh_passport_v1.md#controlledaccessgrants
[by field, GA4GH]: https://github.com/ga4gh-duri/ga4gh-duri.github.io/blob/master/researcher_ids/ga4gh_passport_v1.md#by