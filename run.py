import inspect
import os
import configparser
import argparse

from pathlib import Path

import app

argument_parser = argparse.ArgumentParser()
argument_parser.add_argument(
    "-r", 
    "--report", 
    help="send a report to the configured channel", 
    action="store_true"
)
argument_parser.add_argument(
    "-b", 
    "--boundaries", 
    help="add begin/end boundaries to report", 
    action="store_true"
)
argument_parser.add_argument(
    "-c", 
    "--csv", 
    help="csv file name", 
    type=str,
    default=None
)
argument_parser.add_argument(
    "-j", 
    "--json", 
    help="json file name", 
    type=str,
    default=None
)
argument_parser.add_argument(
    "-m", 
    "--missing", 
    help="missing corporations file name", 
    type=str,
    default=None
)
argument_parser.add_argument(
    "-i", 
    "--ids", 
    help="include ids in export", 
    action="store_true"
)
argument_parser.add_argument(
    "-f", 
    "--fuel", 
    help="minimum hours of fuel remaining to report", 
    type=int,
    default=None
)
argument_parser.add_argument(
    "-l", 
    "--liquid_ozone", 
    help="minimum liquid ozone in an ansiblex to report", 
    type=int,
    default=None
)
argument_parser.add_argument(
    "-o", 
    "--offline_services", 
    help="include offline service notices in report", 
    action="store_true"
)
argument_parser.add_argument(
    "-e", 
    "--extractions", 
    help="include extraction notices in report", 
    action="store_true"
)
argument_parser.add_argument(
    "-s", 
    "--siege", 
    help="include reinforcement notices in report", 
    action="store_true"
)
argument_parser.add_argument(
    "-u", 
    "--unanchoring", 
    help="include unanchoring notices in report", 
    action="store_true"
)
argument_parser.add_argument(
    "-p", 
    "--pos", 
    help="include starbase notices in report", 
    action="store_true"
)
argument_parser.add_argument(
    "-a", 
    "--auth", 
    help="include missing target corporations in report", 
    action="store_true"
)
argument_parser.add_argument(
    "-t", 
    "--tickers", 
    help="uses corp tickers in report", 
    action="store_true"
)
argument_parser.add_argument(
    "-n", 
    "--no_corp_names", 
    help="hide structure owners in report", 
    action="store_true"
)
arguments = argument_parser.parse_args()

#If you've moved your config.ini file, set this variable to the path of the folder containing it (no trailing slash).
CONFIG_PATH_OVERRIDE = None

def dataFile(extraFolder):

    filename = inspect.getframeinfo(inspect.currentframe()).filename
    path = os.path.join(os.path.dirname(os.path.abspath(filename)))

    dataLocation = str(path) + extraFolder

    return(dataLocation)

configPath = (CONFIG_PATH_OVERRIDE) if (CONFIG_PATH_OVERRIDE is not None) else (dataFile("/config"))

if Path(configPath + "/config.ini").is_file():

    config = configparser.ConfigParser()
    config.read(dataFile("/config") + "/config.ini")

    targetAlliances = str(config["App"]["TargetAlliances"]).replace(" ", "").split(",")
    targetCorps = str(config["App"]["TargetCorps"]).replace(" ", "").split(",")
    targetExclusions = str(config["App"]["TargetExclusions"]).replace(" ", "").split(",")
    reportTitle = config["App"]["ReportTitle"]
    webhookPlatform = config["App"]["WebhookPlatform"]
    webhookURL = config["App"]["WebhookURL"]
    coreInfo = config["NeuCore Authentication"]

else:

    try:

        targetAlliances = str(os.environ["ENV_STRUCTURE_OVERVIEW_TARGET_ALLIANCES"]).replace(" ", "").split(",")
        targetCorps = str(os.environ["ENV_STRUCTURE_OVERVIEW_TARGET_CORPS"]).replace(" ", "").split(",")
        targetExclusions = str(os.environ["ENV_STRUCTURE_OVERVIEW_TARGET_EXCLUSIONS"]).replace(" ", "").split(",")
        reportTitle = os.environ["ENV_STRUCTURE_OVERVIEW_REPORT_TITLE"] if "ENV_STRUCTURE_OVERVIEW_REPORT_TITLE" in os.environ else None
        webhookPlatform = os.environ["ENV_STRUCTURE_OVERVIEW_WEBHOOK_PLATFORM"] if "ENV_STRUCTURE_OVERVIEW_WEBHOOK_PLATFORM" in os.environ else None
        webhookURL = os.environ["ENV_STRUCTURE_OVERVIEW_WEBHOOK_URL"] if "ENV_STRUCTURE_OVERVIEW_WEBHOOK_URL" in os.environ else None
        coreInfo = {
            "AppID": os.environ["ENV_STRUCTURE_OVERVIEW_NEUCORE_APP_ID"], 
            "AppSecret": os.environ["ENV_STRUCTURE_OVERVIEW_NEUCORE_APP_SECRET"], 
            "AppURL": os.environ["ENV_STRUCTURE_OVERVIEW_NEUCORE_APP_URL"],
            "LoginName": os.environ["ENV_STRUCTURE_OVERVIEW_NEUCORE_LOGIN_NAME"]
        }

    except:

        raise Warning("No Configuration File or Required Environment Variables Found!")

#Cleanup of possible parsing issues
if "" in targetAlliances:
    targetAlliances.remove("")
if "" in targetCorps:
    targetCorps.remove("")
if "" in targetExclusions:
    targetExclusions.remove("")

processor = app.App(targetAlliances, targetCorps, targetExclusions, coreInfo, arguments.ids)

if arguments.json is not None:
    processor.export_json(arguments.json)
if arguments.csv is not None:
    processor.export_csv(arguments.csv)
if arguments.missing is not None:
    processor.export_unknowns(arguments.missing)
if arguments.report:
    processor.make_report(
        webhookPlatform, 
        webhookURL, 
        reportTitle, 
        arguments.boundaries,
        arguments.fuel,
        arguments.liquid_ozone,
        arguments.pos,
        arguments.offline_services,
        arguments.extractions,
        arguments.siege,
        arguments.unanchoring,
        arguments.auth,
        arguments.tickers,
        arguments.no_corp_names
    )