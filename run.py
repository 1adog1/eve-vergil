import argparse

from pathlib import Path
from datetime import datetime, UTC

from VergilConfig import Config

import app

argument_parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

argument_parser.add_argument(
    "operation", 
    help="the operation the app should perform", 
    choices=["report", "export", "overview"]
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
    help="the directory to place export and overview files in",
    default=str((Path(__file__).parent / "output").resolve(True))
)
argument_parser.add_argument(
    "-n", 
    "--name_prefix", 
    help="the prefix to assign to the export and overview filenames",
    default=datetime.now(UTC).strftime("%Y-%m-%d_%H-%M-%S")
)
argument_parser.add_argument(
    "-e", 
    "--extensions", 
    help="the file types to exports and overviews will use", 
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

configVariables = Config()

processor = app.App(
    configVariables.app,
    configVariables.neucore_auth, 
    configVariables.versioning,
    arguments.build_data
)

if arguments.operation in ["export", "overview"]:

    if "json" in arguments.extensions:
        processor.export_json(arguments.operation, arguments.directory, arguments.name_prefix)
    if "csv" in arguments.extensions:
        processor.export_csv(arguments.operation, arguments.directory, arguments.name_prefix)
    if "missing" in arguments.build_data:
        processor.export_unknowns(arguments.directory, arguments.name_prefix)

if arguments.operation == "report":

    processor.make_report(
        configVariables.app.webhook_platform, 
        configVariables.app.webhook_url, 
        configVariables.app.report_title, 
        arguments.citadel_reports,
        arguments.pos_reports,
        arguments.sov_reports,
        arguments.fuel,
        arguments.reagents,
        arguments.liquid_ozone,
        arguments.report_options
    )
