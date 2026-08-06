import inspect
import os
import json
import time

from datetime import datetime
from csv import DictWriter

import ESI
from Terminus import RelayTerminus
from EveSubjects import Corporation

def dataFile(extraFolder):

    filename = inspect.getframeinfo(inspect.currentframe()).filename
    path = os.path.join(os.path.dirname(os.path.abspath(filename)))

    dataLocation = str(path) + extraFolder

    return(dataLocation)

class App:
    
    def __init__(
            self, 
            app_variables,
            neucore_variables, 
            version_variables, 
            data_to_build
        ):
        
        self.target_corporations = app_variables.target_corps
        self.target_alliances = app_variables.target_alliances
        self.target_exclusions = app_variables.target_exclusions
        self.corporations = app_variables.target_corps
        self.corporation_data = {}
        
        self.auth_handler = ESI.NeucoreAuth(neucore_variables.app_id, neucore_variables.app_secret, neucore_variables.app_url)
        self.app_variables = app_variables
        self.neucore_variables = neucore_variables
        self.version_variables = version_variables
        self.esi_handler = ESI.Handler(self.version_variables)
        
        self.ids_to_parse = {}
        self.structures = {}
        self.extractions = {}
        self.starbases = {}
        self.sov = {}
        self.unknowns = {}
        
        self.pull_static()
        self.build_targets()
        self.get_valid_tokens()
        self.get_names()
        self.process_corporations(data_to_build)
        
    def pull_static(self):
        
        with open(dataFile("/static") + "/TypeIDs.json") as knownData:
            self.type_ids = json.load(knownData)
            
        with open(dataFile("/static") + "/geographicInformationV3.json") as knownData:
            self.geographic_data = json.load(knownData)
            
    def build_targets(self):
        
        for each_alliance in self.target_alliances:
            
            corporations_request = self.esi_handler.call("/alliances/{alliance_id}/corporations/", alliance_id=each_alliance, retries=2)
            
            if corporations_request["Success"]:
                self.corporations += corporations_request["Data"]
                
            else:
                raise Exception(
                    "CORPORATIONS ERROR\n\nRepsonse Data: {data}\n\nResponse Headers: {headers}".format(
                        data=corporations_request["Data"],
                        headers=corporations_request["Headers"]
                    )
                )
                
        self.corporations = [int(ids) for ids in self.corporations if str(ids) not in self.target_exclusions]
                
        self.corporation_data = {int(ids): None for ids in self.corporations}
        
        for each_corporation in self.corporation_data:
            if int(each_corporation) not in self.ids_to_parse:
                self.ids_to_parse[int(each_corporation)] = None
        
    def get_valid_tokens(self):
        
        known_tokens = self.auth_handler.getTokenCharacters(self.neucore_variables.login_name)
        
        for each_token in known_tokens:
            
            corporation_id = int(each_token["corporationId"])
            character_id = int(each_token["characterId"])
            
            if corporation_id in self.corporations and self.corporation_data[corporation_id] is None:
                
                self.corporation_data[corporation_id] = Corporation(corporation_id, character_id, self.app_variables, self.version_variables)
                
                print("Found token for " + str(corporation_id) + " from " + str(character_id) + "...")
                
    def get_names(self):
        
        names_request = self.esi_handler.call("/universe/names/", ids=list(self.ids_to_parse.keys()), retries=2)
        
        if names_request["Success"]:
            
            for each_name in names_request["Data"]:
                
                self.ids_to_parse[each_name["id"]] = each_name["name"]
            
        else:
            
            raise Exception(
                "NAMES ERROR\n\nRepsonse Data: {data}\n\nResponse Headers: {headers}".format(
                    data=names_request["Data"],
                    headers=names_request["Headers"]
                )
            )
            
    def process_corporations(self, data_types):
        
        for each_corporation in self.corporation_data:
            
            if self.corporation_data[each_corporation] is not None:
                
                print("Checking " + str(each_corporation) + "...")

                if "citadels" in data_types:
                    self.corporation_data[each_corporation].get_structures(self.auth_handler, self.neucore_variables.login_name, self.geographic_data, self.type_ids)
                    self.corporation_data[each_corporation].get_extractions(self.auth_handler, self.neucore_variables.login_name)

                if "starbases" in data_types:
                    self.corporation_data[each_corporation].get_starbases(self.auth_handler, self.neucore_variables.login_name, self.geographic_data, self.type_ids)

                if "sov" in data_types:
                    self.corporation_data[each_corporation].get_sov(self.auth_handler, self.neucore_variables.login_name, self.geographic_data, self.type_ids)

                if "citadels" in data_types or "starbases" in data_types:
                    self.corporation_data[each_corporation].get_assets(self.auth_handler, self.neucore_variables.login_name, self.type_ids)
                    self.corporation_data[each_corporation].process_asset_data()
                
                self.structures = self.structures | self.corporation_data[each_corporation].structure_data
                self.extractions = self.extractions | self.corporation_data[each_corporation].extractions
                self.starbases = self.starbases | self.corporation_data[each_corporation].starbase_data
                self.sov = self.sov | self.corporation_data[each_corporation].sov_data
                
            elif "missing" in data_types:
                
                self.unknowns[each_corporation] = self.ids_to_parse[each_corporation]
                
        self.structures = dict(sorted(self.structures.items(), key=lambda x: (str(x[1].owner_name), str(x[1].region), str(x[1].constellation), str(x[1].name))))
        self.starbases = dict(sorted(self.starbases.items(), key=lambda x: (str(x[1].owner_name), str(x[1].region), str(x[1].constellation), str(x[1].moon))))
        self.sov = dict(sorted(self.sov.items(), key=lambda x: (str(x[1].owner_name), str(x[1].region), str(x[1].constellation), str(x[1].system))))
                
    def export_json(self, mode, directory, file_prefix):
        
        print("Exporting JSONs...")
        
        if self.structures:
            with open((directory + "/" + mode + "_" + file_prefix + "_citadels.json"), "w") as json_file:
                json.dump({x: getattr(y, mode)() for x, y in self.structures.items() if (mode != "overview" or y.overview_approved())}, json_file, indent=1)
        else:
            print("No citadels found, skipping export.")

        if self.starbases:
            with open((directory + "/" + mode + "_" + file_prefix + "_starbases.json"), "w") as json_file:
                json.dump({x: getattr(y, mode)() for x, y in self.starbases.items() if (mode != "overview" or y.overview_approved())}, json_file, indent=1)
        else:
            print("No starbases found, skipping export.")

        if self.sov:
            with open((directory + "/" + mode + "_" + file_prefix + "_sov.json"), "w") as json_file:
                json.dump({x: getattr(y, mode)() for x, y in self.sov.items()}, json_file, indent=1)
        else:
            print("No sov found, skipping export.")
        
    def export_csv(self, mode, directory, file_prefix):
        
        print("Exporting CSVs...")

        structure_export_data = {x: getattr(y, mode)() for x, y in self.structures.items() if (mode != "overview" or y.overview_approved())}
        starbase_export_data = {x: getattr(y, mode)() for x, y in self.starbases.items() if (mode != "overview" or y.overview_approved())}
        sov_export_data = {x: getattr(y, mode)() for x, y in self.sov.items()}
        
        if structure_export_data:
            with open((directory + "/" + mode + "_" + file_prefix + "_citadels.csv"), "w", newline="") as csv_file:
                fields = list(structure_export_data.values())[0].keys()
                csv_writer = DictWriter(csv_file, fieldnames=fields)
                
                csv_writer.writeheader()
                for each_structure in structure_export_data.values():
                    
                    for key, each_val in each_structure.items():
                        each_structure[key] = (" " + each_val) if (isinstance(each_val, str) and each_val.startswith("-")) else each_val
                    
                    csv_writer.writerow(each_structure)
        else:
            print("No citadels found, skipping export.")


        if starbase_export_data:    
            with open((directory + "/" + mode + "_" + file_prefix + "_starbases.csv"), "w", newline="") as csv_file:
                fields = list(starbase_export_data.values())[0].keys()
                csv_writer = DictWriter(csv_file, fieldnames=fields)
                
                csv_writer.writeheader()
                for each_starbase in starbase_export_data.values():
                    
                    for key, each_val in each_starbase.items():
                        each_starbase[key] = (" " + each_val) if (isinstance(each_val, str) and each_val.startswith("-")) else each_val
                    
                    csv_writer.writerow(each_starbase)
        else:
            print("No starbases found, skipping export.")

        if sov_export_data:    
            with open((directory + "/" + mode + "_" + file_prefix + "_sov.csv"), "w", newline="") as csv_file:
                fields = list(sov_export_data.values())[0].keys()
                csv_writer = DictWriter(csv_file, fieldnames=fields)
                
                csv_writer.writeheader()
                for each_sov_hub in sov_export_data.values():
                    
                    for key, each_val in each_sov_hub.items():
                        each_sov_hub[key] = (" " + each_val) if (isinstance(each_val, str) and each_val.startswith("-")) else each_val
                    
                    csv_writer.writerow(each_sov_hub)
        else:
            print("No sov found, skipping export.")
        
    def export_unknowns(self, directory, file_prefix):
        
        print("Exporting Unknowns...")
        
        if self.unknowns:
            with open((directory + "/" + file_prefix + "_unknowns.json"), "w") as unknowns_file:
                json.dump(self.unknowns, unknowns_file, indent=1)
        else:
            print("No unknowns found, skipping export.")
        
    def split_report(self, parts, section_name):
        
        components = []
        
        if parts:
            
            element_counter = 0
            message_counter = 1
            
            while element_counter < len(parts):
                
                report_string = ""
                
                while element_counter < len(parts):
                    
                    if len(report_string + parts[element_counter]) > 1900:
                        break
                        
                    report_string += parts[element_counter]
                    element_counter += 1
                
                components.append(f"{section_name} ({message_counter})\n```\n{report_string}```")
                message_counter += 1
                
        return components
        
    def make_report(
        self,   
        platform, 
        url, 
        title, 
        citadel_report_types,
        pos_report_types,
        sov_report_types,
        fuel_threshold,
        reagent_threshold,
        ozone_threshold,
        other_report_options
    ):
        
        report_template = "{name} ({type}) — {message}\n" if ("hide_owners" in other_report_options) else "[{owner}] {name} ({type}) — {message}\n"
        
        report_components = []
        
        if "boundaries" in other_report_options:
            report_components.append(f"*----- BEGIN {title} -----*\n\n")
        
        if "anchoring" in citadel_report_types:
            
            report_parts = [
                report_template.format(
                    name=x.name,
                    type=x.type,
                    owner=x.owner_ticker if ("tickers" in other_report_options) else x.owner_name,
                    message="Anchors: " + x.timer
                )
                for y, x in self.structures.items()
                if x.state == "anchoring" and x.timer is not None
            ]
            
            report_components += self.split_report(report_parts, "Anchoring Alerts")

        if "unanchoring" in citadel_report_types:
            
            report_parts = [
                report_template.format(
                    name=x.name,
                    type=x.type,
                    owner=x.owner_ticker if ("tickers" in other_report_options) else x.owner_name,
                    message="Unanchors: " + x.unanchor_timer
                )
                for y, x in self.structures.items()
                if x.unanchor_timer is not None
            ]
            
            report_components += self.split_report(report_parts, "Unanchoring Alerts")
        
        if "fuel" in citadel_report_types:
            
            report_parts = [
                report_template.format(
                    name=x.name,
                    type=x.type,
                    owner=x.owner_ticker if ("tickers" in other_report_options) else x.owner_name,
                    message="Fuel Expires: " + x.fuel_expiry
                )
                for y, x in self.structures.items()
                if x.fuel_expiry is not None and (datetime.fromisoformat(x.fuel_expiry).timestamp() - time.time()) < (fuel_threshold * 60 * 60)
            ]
            
            report_components += self.split_report(report_parts, "Fuel Alerts")

        if "reagents" in citadel_report_types:

            report_parts = [
                report_template.format(
                    name=x.name,
                    type=x.type,
                    owner=x.owner_ticker if ("tickers" in other_report_options) else x.owner_name,
                    message="Reagents Expire: " + x.reagent_expiry
                )
                for y, x in self.structures.items()
                if x.reagent_expiry is not None and (datetime.fromisoformat(x.reagent_expiry).timestamp() - time.time()) < (reagent_threshold * 60 * 60)
            ]
            
            report_components += self.split_report(report_parts, "Reagent Alerts")
            
        if "ozone" in citadel_report_types:
            
            report_parts = [
                report_template.format(
                    name=x.name,
                    type=x.type,
                    owner=x.owner_ticker if ("tickers" in other_report_options) else x.owner_name,
                    message="Remaining Ozone: {ozone:,}".format(ozone=x.ozone)
                )
                for y, x in self.structures.items()
                if x.type_id == 35841 and x.ozone < ozone_threshold
            ]
            
            report_components += self.split_report(report_parts, "Liquid Ozone Alerts")
            
        if "reinforcement" in citadel_report_types:
            
            report_parts = [
                report_template.format(
                    name=x.name,
                    type=x.type,
                    owner=x.owner_ticker if ("tickers" in other_report_options) else x.owner_name,
                    message=(x.state.replace("_", " ").title() + " until " + x.timer)
                )
                for y, x in self.structures.items()
                if "reinforce" in x.state and x.timer is not None
            ]
            
            report_components += self.split_report(report_parts, "Siege Alerts")
            
        if "offline_services" in citadel_report_types:
            
            report_parts = [
                report_template.format(
                    name=x.name,
                    type=x.type,
                    owner=x.owner_ticker if ("tickers" in other_report_options) else x.owner_name,
                    message=("Offline Services: " + ", ".join(x.offline_services))
                )
                for y, x in self.structures.items()
                if x.offline_services
            ]
            
            report_components += self.split_report(report_parts, "Offline Service Alerts")
            
        if "extractions" in citadel_report_types:
            
            report_parts = [
                report_template.format(
                    name=x.name,
                    type=x.type,
                    owner=x.owner_ticker if ("tickers" in other_report_options) else x.owner_name,
                    message="No Extraction Scheduled" if y not in self.extractions else "Auto-Detonation at: " + self.extractions[y].auto_time
                )
                for y, x in self.structures.items()
                if x.has_drill and (y not in self.extractions or datetime.fromisoformat(self.extractions[y].end_time).timestamp() < time.time())
            ]
            
            report_components += self.split_report(report_parts, "Extraction Alerts")
            
        if "anchoring" in pos_report_types:
            
            report_parts = [
                report_template.format(
                    name=(x.moon if x.moon is not None else x.system + " - Unknown Moon"),
                    type=x.type,
                    owner=x.owner_ticker if ("tickers" in other_report_options) else x.owner_name,
                    message=x.state.title()
                )
                for y, x in self.starbases.items()
                if x.state == "onlining"
            ]
            
            report_components += self.split_report(report_parts, "POS Onlining Alerts")

        if "unanchoring" in pos_report_types:
            
            report_parts = [
                report_template.format(
                    name=(x.moon if x.moon is not None else x.system + " - Unknown Moon"),
                    type=x.type,
                    owner=x.owner_ticker if ("tickers" in other_report_options) else x.owner_name,
                    message=x.state.title()
                )
                for y, x in self.starbases.items()
                if x.state == "unanchoring"
            ]
            
            report_components += self.split_report(report_parts, "POS Unanchoring Alerts")

        if "fuel" in pos_report_types:

            report_parts = [
                report_template.format(
                    name=(x.moon if x.moon is not None else x.system + " - Unknown Moon"),
                    type=x.type,
                    owner=x.owner_ticker if ("tickers" in other_report_options) else x.owner_name,
                    message="Fuel Expires: " + x.fuel_expiry
                )
                for y, x in self.starbases.items()
                if x.fuel_expiry is not None and (datetime.fromisoformat(x.fuel_expiry).timestamp() - time.time()) < (fuel_threshold * 60 * 60)
            ]
            
            report_components += self.split_report(report_parts, "POS Fuel Alerts")
            
        if "reinforcement" in pos_report_types:
            
            report_parts = [
                report_template.format(
                    name=(x.moon if x.moon is not None else x.system + " - Unknown Moon"),
                    type=x.type,
                    owner=x.owner_ticker if ("tickers" in other_report_options) else x.owner_name,
                    message="Reinforced until: " + x.timer
                )
                for y, x in self.starbases.items()
                if x.timer is not None
            ]
            
            report_components += self.split_report(report_parts, "POS Siege Alerts")
            
        if "offline" in pos_report_types:
            
            report_parts = [
                report_template.format(
                    name=(x.moon if x.moon is not None else x.system + " - Unknown Moon"),
                    type=x.type,
                    owner=x.owner_ticker if ("tickers" in other_report_options) else x.owner_name,
                    message="Offline"
                )
                for y, x in self.starbases.items()
                if x.state == "offline"
            ]
            
            report_components += self.split_report(report_parts, "POS Offline Alerts")

        if "reagents" in sov_report_types:

            report_parts = [
                report_template.format(
                    name=x.system,
                    type="Sovereignty Hub",
                    owner=x.owner_ticker if ("tickers" in other_report_options) else x.owner_name,
                    message=z["Name"] + " Expires: " + z["Expires"]
                )
                for y, x in self.sov.items()
                for z in x.reagent_expirations.values()
                if (datetime.fromisoformat(z["Expires"]).timestamp() - time.time()) < (reagent_threshold * 60 * 60)
            ]
            
            report_components += self.split_report(report_parts, "Sov Reagent Alerts")

        if "low_power_services" in sov_report_types:
            
            report_parts = [
                report_template.format(
                    name=x.system,
                    type="Sovereignty Hub",
                    owner=x.owner_ticker if ("tickers" in other_report_options) else x.owner_name,
                    message=("Low Power Upgrades: " + ", ".join([z["Name"] for z in x.low_power_upgrades.values()])),
                )
                for y, x in self.sov.items()
                if x.low_power_upgrades
            ]
            
            report_components += self.split_report(report_parts, "Sov Low Power Service Alerts")
            
        if ("missing" in other_report_options):
            
            auth_string = "\n".join(list(self.unknowns.values()))
            
            if auth_string:
                report_components.append(f"Target Corporations Not Authed\n```\n{auth_string}\n```")
                
        if ("boundaries" in other_report_options):
            report_components.append(f"*----- END {title} -----*\n\n")
        
        for each_message in report_components:
            relay = RelayTerminus(each_message, platform, url)
            relay.send(5)
