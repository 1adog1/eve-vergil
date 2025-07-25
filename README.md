# Eve Vergil

Eve Vergil is a structure status reporting application for Eve Online, designed for use with [neucore](https://github.com/tkhamez/neucore). 

The app builds an aggregate structure list from the corporations configured. The list can then be dumped to a CSV or JSON file. A report of important information can also be generated and sent to a Discord or Slack channel.

## Requirements

* Python ≥ 3.13
  * [requests](https://pypi.org/project/requests/)
* A Neucore App
  * The `app-esi-login` and `app-esi-token` roles
  * An EVE Login that requires `Director` with the following scopes:
    * `esi-universe.read_structures.v1`
    * `esi-corporations.read_structures.v1`
    * `esi-assets.read_corporation_assets.v1`
    * `esi-corporations.read_starbases.v1`
    * `esi-industry.read_corporation_mining.v1`
    * `esi-characters.read_corporation_roles.v1`
    
## Setup
* Rename the Configuration File in `/config/config.ini.dist` to `/config/config.ini` and setup as needed. 
  * Alternatively, use the Environment Variables mentioned in the file.

## Run Options
* `-r`, `--report`                        Send a report to the configured channel
* `-b`, `--boundaries`                    Add BEGIN/END boundaries to report
* `-c`, `--csv CSV`                       Export structures and starbases to csv with file prefix CSV
* `-j`, `--json JSON`                     Export structures and starbases to json with file prefix JSON
* `-m`, `--missing MISSING`               Export missing target corporations to json with file name MISSING
* `-f`, `--fuel FUEL`                     Report if less than FUEL hours of fuel remaining
* `-l`, `--liquid_ozone LIQUID_OZONE`     Report if less than LIQUID_OZONE ozone remaining in an ansiblex
* `-o`, `--offline_services`              Include offline service notices in report
* `-e`, `--extractions`                   Include extraction notices in report
* `-s`, `--siege`                         Include reinforcement notices in report
* `-d`, `--deploying`                     Include anchoring notices in report
* `-u`, `--unanchoring`                   Include unanchoring notices in report
* `-p`, `--pos`                           Include starbase notices in report (works alongside the --offline_services, --siege, --deploying, and --unanchoring flags)
* `-a`, `--auth`                          Include missing target corporations in report
* `-t`, `--tickers`                       Uses corp tickers in report
* `-n`, `--no_corp_names`                 Hide structure owners in report