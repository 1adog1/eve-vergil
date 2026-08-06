# Minor Version Superintendent - 1 - 0 Update

## Options
- Added an overview run option, which exports data more designed for public consumption.

## Citadels
- Fighter Tubes, Fighter Bays, and Ammo Holds are now tracked and exported as part of the structure fitting.

## Sovereignty
- Security Status and Security Band are now tracked and exported.

## Configuration
- Added Region / Constellation / System filtering.
- Added citadel exclusions for specific types.
- Added citadel exclusions for types that don't have industry rigs.

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