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
    * `esi-structures.read_corporation.v1`
    
## Setup
* Rename the Configuration File in `/config/config.ini.dist` to `/config/config.ini` and setup as needed. 
  * Alternatively, use the Environment Variables mentioned in the file.

## Run Options
* `operation`
  * Required argument setting the operation the app will preform:
    * `report` sends a report to the configured Slack or Discord channel
    * `export` dumps the full loaded dataset in human-readable form to one or more files
    * `overview` dumps the loaded dataset in a form designed for public consumption
* `-b`, `--build_data DATA_TYPES`
  * A space-separated list of data types to build, defaults to all:
    * `citadels`
    * `starbases`
    * `sov`
    * `missing` builds a list of corporations who were targeted but not authed
* `-d`, `--directory DIRECTORY`
  * The directory exports are sent to, defaults to the included `output` folder
* `-n`, `--name_prefix NAME_PREFIX`
  * A prefix to give to exported filenames, defaults to the current datetime `YYYY-MM-DD_hh-mm-ss`
* `-e`, `--extensions EXTENSIONS`
  * A space-separated list of file types to export:
    * `csv`
    * `json`
* `-c`, `--citadel_reports CITADEL_REPORT_TYPES`
  * A space-separated list of things to report for citadels:
    * `fuel`
    * `reagents`
    * `ozone`
    * `offline_services`
    * `extractions`
    * `reinforcement`
    * `anchoring`
    * `unanchoring`
* `-f`, `--fuel FUEL_THRESHOLD`
  * A threshold of fuel in a Citadel or Starbase in hours remaining, below which a report is generated, defaults to `72`
* `-r`, `--reagents REAGENT_THRESHOLD`
  * A threshold of reagents in a Citadel or Sov Hub in hours remaining, below which a report is generated, defaults to `72`
* `-l`, `--liquid_ozone LIQUID_OZONE_THRESHOLD`
  * A threshold of liquid ozone in an Ansiblex, below which a report is generated, defaults to `100000`
* `-p`, `--pos_reports POS_REPORT_TYPES`
  * A space-separated list of things to report for Starbases:
    * `fuel`
    * `offline`
    * `reinforcement`
    * `anchoring`
    * `unanchoring`
* `-s`, `--sov_reports SOV_REPORT_TYPES`
  * A space-separated list of things to report for Sov Hubs:
    * `reagents`
    * `low_power_services`
* `-o`, `--report_options REPORT_OPTIONS`
  * A space-separated list of other report options:
    * `boundaries` Adds `BEGIN`/`END` messages surrounding the report
    * `missing` Adds a report that lists corporations who were targeted but not authed
    * `tickers` Tickers are used instead of full corporation names for structure owners
    * `hide_owners` Owners are not shown next to structures