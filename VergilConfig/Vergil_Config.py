__all__ = ["Config"]

import os
import configparser

from pathlib import Path

# If you moved the /config directory, put its full path here:
CONFIG_DIRECTORY = None

def cleanup_config(variable):

    return str(variable).strip("\"").strip("'") if variable is not None else None

class EveAuth:

    def __init__(self, ClientContactInfo):

        self.client_contact_info = cleanup_config(ClientContactInfo)

class NeucoreAuth:

    def __init__(self, AppID, AppSecret, AppURL, LoginName):

        self.app_id = cleanup_config(AppID)
        self.app_secret = cleanup_config(AppSecret)
        self.app_url = cleanup_config(AppURL)
        self.login_name = cleanup_config(LoginName)

class AppConfig:

    def __init__(
        self,
        TargetAlliances,
        TargetCorps,
        TargetExclusions,
        ReportTitle,
        WebhookPlatform,
        WebhookURL
    ):

        self.target_alliances = cleanup_config(TargetAlliances).replace(" ", "").split(",")
        self.target_corps = cleanup_config(TargetCorps).replace(" ", "").split(",")
        self.target_exclusions = cleanup_config(TargetExclusions).replace(" ", "").split(",")
        self.report_title = cleanup_config(ReportTitle)
        self.webhook_platform = cleanup_config(WebhookPlatform)
        self.webhook_url = cleanup_config(WebhookURL)

        if "" in self.target_alliances:
            self.target_alliances.remove("")
        if "" in self.target_corps:
            self.target_corps.remove("")
        if "" in self.target_exclusions:
            self.target_exclusions.remove("")

class Versioning:

    def __init__(
            self,
            AppName,
            AppMajorVersion,
            AppMinorVersion,
            AppPatchVersion,
            AppDelimiter,
            AppGithubLink,
            ClientContactInfo
        ):

        self.app_name = cleanup_config(AppName)
        self.app_version = cleanup_config(AppDelimiter).join([
            cleanup_config(AppMajorVersion), 
            cleanup_config(AppMinorVersion), 
            cleanup_config(AppPatchVersion)
        ])
        self.app_github = cleanup_config(AppGithubLink)
        self.client_contact_info = cleanup_config(ClientContactInfo)

class Config:

    def __init__(self):

        config_directory = (Path(__file__).parent / ".." / "config") if CONFIG_DIRECTORY is None else Path(CONFIG_DIRECTORY)

        if not config_directory.exists():
            raise Exception("{location} does not exist!".format(location = str(config_directory)))
        
        config_file = config_directory / "config.ini"

        if config_file.exists():

            config = configparser.ConfigParser()
            config.read(str(config_file.resolve(True)))

            self.eve_auth = EveAuth(ClientContactInfo = config["Eve Authentication"]["ClientContactInfo"])

            self.neucore_auth = NeucoreAuth(
                AppID = config["NeuCore Authentication"]["AppID"], 
                AppSecret = config["NeuCore Authentication"]["AppSecret"], 
                AppURL = config["NeuCore Authentication"]["AppURL"],
                LoginName = config["NeuCore Authentication"]["LoginName"]
            )

            self.app = AppConfig(
                TargetAlliances = config["App"]["TargetAlliances"],
                TargetCorps = config["App"]["TargetCorps"],
                TargetExclusions = config["App"]["TargetExclusions"],
                ReportTitle = config["App"]["ReportTitle"],
                WebhookPlatform = config["App"]["WebhookPlatform"],
                WebhookURL = config["App"]["WebhookURL"]
            )

        else:

            self.eve_auth = EveAuth(ClientContactInfo = os.environ["ENV_STRUCTURE_OVERVIEW_EVE_CLIENT_CONTACT_INFO"])

            self.neucore_auth = NeucoreAuth(
                AppID = os.environ["ENV_STRUCTURE_OVERVIEW_NEUCORE_APP_ID"], 
                AppSecret = os.environ["ENV_STRUCTURE_OVERVIEW_NEUCORE_APP_SECRET"], 
                AppURL = os.environ["ENV_STRUCTURE_OVERVIEW_NEUCORE_APP_URL"],
                LoginName = os.environ["ENV_STRUCTURE_OVERVIEW_NEUCORE_LOGIN_NAME"]
            )

            self.app = AppConfig(
                TargetAlliances = os.environ["ENV_STRUCTURE_OVERVIEW_TARGET_ALLIANCES"],
                TargetCorps = os.environ["ENV_STRUCTURE_OVERVIEW_TARGET_CORPS"],
                TargetExclusions = os.environ["ENV_STRUCTURE_OVERVIEW_TARGET_EXCLUSIONS"],
                ReportTitle = os.environ["ENV_STRUCTURE_OVERVIEW_REPORT_TITLE"] if "ENV_STRUCTURE_OVERVIEW_REPORT_TITLE" in os.environ else None,
                WebhookPlatform = os.environ["ENV_STRUCTURE_OVERVIEW_WEBHOOK_PLATFORM"] if "ENV_STRUCTURE_OVERVIEW_WEBHOOK_PLATFORM" in os.environ else None,
                WebhookURL = os.environ["ENV_STRUCTURE_OVERVIEW_WEBHOOK_URL"] if "ENV_STRUCTURE_OVERVIEW_WEBHOOK_URL" in os.environ else None
            )

        versioning_file = config_directory / "VERSIONING"
        versioning = configparser.ConfigParser()
        versioning.read(str(versioning_file.resolve(True)))

        self.versioning = Versioning(
            AppName = versioning["App"]["app_name"],
            AppMajorVersion = versioning["App"]["major_version"],
            AppMinorVersion = versioning["App"]["minor_version"],
            AppPatchVersion = versioning["App"]["patch_version"],
            AppDelimiter = versioning["App"]["delimiter"],
            AppGithubLink = versioning["App"]["github_link"],
            ClientContactInfo = self.eve_auth.client_contact_info
        )

