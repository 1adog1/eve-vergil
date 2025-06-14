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
    "-u", 
    "--unknowns", 
    help="unknowns file name", 
    type=str,
    default=None
)
argument_parser.add_argument(
    "-i", 
    "--ids", 
    help="include ids", 
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
    webhookPlatform = config["App"]["WebhookPlatform"]
    webhookURL = config["App"]["WebhookURL"]
    coreInfo = config["NeuCore Authentication"]

else:

    try:

        targetAlliances = str(os.environ["ENV_STRUCTURE_OVERVIEW_TARGET_ALLIANCES"]).replace(" ", "").split(",")
        targetCorps = str(os.environ["ENV_STRUCTURE_OVERVIEW_TARGET_CORPS"]).replace(" ", "").split(",")
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

processor = app.App(targetAlliances, targetCorps, coreInfo, arguments.ids)

if arguments.json is not None:
    processor.export_json(arguments.json)
if arguments.csv is not None:
    processor.export_csv(arguments.csv)
if arguments.unknowns is not None:
    processor.export_unknowns(arguments.unknowns)
#TBA
if arguments.report:
    processor.make_report(webhookPlatform, webhookURL)