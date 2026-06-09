# Major Version Superintendent - 0 - 0 Update

## Versioning
- App versions and changes are now tracked.

## Configuration
- A new `ClientContactInfo` config option has been created.
- Config data is now built and accessible via a new `VersionConfig` module. 

## ESI
- A User-Agent built from a combination of app version data and `ClientContactInfo` is now sent with ESI requests. 

## Sovereignty
- Sovereignty Hub Reagent Bay values now correctly take into account `last_updated`.