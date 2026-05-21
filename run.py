import inspect
import os
import configparser
import argparse

from pathlib import Path
from datetime import datetime, UTC

import app

#If you've moved your config.ini file, set this variable to the path of the folder containing it (no trailing slash).
CONFIG_PATH_OVERRIDE = None

def dataFile(extraFolder):

    filename = inspect.getframeinfo(inspect.currentframe()).filename
    path = os.path.join(os.path.dirname(os.path.abspath(filename)))

    dataLocation = str(path) + extraFolder

    return(dataLocation)

configPath = (CONFIG_PATH_OVERRIDE) if (CONFIG_PATH_OVERRIDE is not None) else (dataFile("/config"))

argument_parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

argument_parser.add_argument(
    "operation", 
    help="the operation the app should perform", 
    choices=["report", "export"]
)
argument_parser.add_argument(
    "-b", 
    "--build_data", 
    help="the datasets to build for each corp", 
    nargs="+",
    choices=["citadels", "starbases", "sov", "missing"],
    default=["citadels", "starbases", "sov", "missing"]
)
argument_parser.add_argument(
    "-d", 
    "--directory", 
    help="the directory to place exported files in",
    default=dataFile("/output")
)
argument_parser.add_argument(
    "-n", 
    "--name_prefix", 
    help="the prefix to assign to the exported filenames",
    default=datetime.now(UTC).strftime("%Y-%m-%d_%H-%M-%S")
)
argument_parser.add_argument(
    "-e", 
    "--extensions", 
    help="the file types to export", 
    nargs="+",
    choices=["csv", "json"],
    default=["csv", "json"]
)
argument_parser.add_argument(
    "-c", 
    "--citadel_reports", 
    help="the citadel reports to generate", 
    nargs="*",
    choices=["fuel", "reagents", "ozone", "offline_services", "extractions", "reinforcement", "anchoring", "unanchoring"],
    default=[]
)
argument_parser.add_argument(
    "-f", 
    "--fuel", 
    help="minimum hours of fuel remaining to report", 
    type=int,
    default=72
)
argument_parser.add_argument(
    "-r", 
    "--reagents", 
    help="minimum hours of reagents remaining to report", 
    type=int,
    default=72
)
argument_parser.add_argument(
    "-l", 
    "--liquid_ozone", 
    help="minimum liquid ozone in an ansiblex to report", 
    type=int,
    default=100000
)
argument_parser.add_argument(
    "-p", 
    "--pos_reports", 
    help="the pos reports to generate", 
    nargs="*",
    choices=["fuel", "offline", "reinforcement", "anchoring", "unanchoring"],
    default=[]
)
argument_parser.add_argument(
    "-s", 
    "--sov_reports", 
    help="the sov reports to generate", 
    nargs="*",
    choices=["reagents", "low_power_services"],
    default=[]
)
argument_parser.add_argument(
    "-o", 
    "--report_options", 
    help="other report options", 
    nargs="*",
    choices=["boundaries", "missing", "tickers", "hide_owners"],
    default=[]
)

arguments = argument_parser.parse_args()

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

processor = app.App(targetAlliances, targetCorps, targetExclusions, coreInfo, arguments.build_data)

if arguments.operation == "export":

    if "json" in arguments.extensions:
        processor.export_json(arguments.directory, arguments.name_prefix)
    if "csv" in arguments.extensions:
        processor.export_csv(arguments.directory, arguments.name_prefix)
    if "missing" in arguments.build_data:
        processor.export_unknowns(arguments.directory, arguments.name_prefix)

if arguments.operation == "report":

    processor.make_report(
        webhookPlatform, 
        webhookURL, 
        reportTitle, 
        arguments.citadel_reports,
        arguments.pos_reports,
        arguments.sov_reports,
        arguments.fuel,
        arguments.reagents,
        arguments.liquid_ozone,
        arguments.report_options
    )
