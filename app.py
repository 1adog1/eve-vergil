import inspect
import os
import json
import time

from datetime import datetime
from csv import DictWriter

import ESI
from Terminus import RelayTerminus

def dataFile(extraFolder):

    filename = inspect.getframeinfo(inspect.currentframe()).filename
    path = os.path.join(os.path.dirname(os.path.abspath(filename)))

    dataLocation = str(path) + extraFolder

    return(dataLocation)

class Corporation:
    
    def __init__(self, id, source_id):
        
        self.id = id
        self.name = None
        self.ticker = None
        self.source = source_id
        self.structure_data = {}
        self.extractions = {}
        self.starbase_data = {}
        
        self.get_name()
        
    def get_name(self):
        
        esi_handler = ESI.Handler()
        
        name_request = esi_handler.call("/corporations/{corporation_id}/", corporation_id=self.id, retries=1)
        
        if name_request["Success"]:
            
            self.name = name_request["Data"]["name"]
            self.ticker = name_request["Data"]["ticker"]
            
        else:
            
            raise Exception("CORPORATION NAME ERROR")
        
    def get_structures(self, auth_handler, login_name, geographic_data, type_data, include_ids):
        
        access_token = auth_handler.getAccessToken(self.source, login_name)
        
        if access_token is None:
            raise Exception("ACCESS TOKEN ERROR")
        
        esi_handler = ESI.Handler(access_token)
        
        current_page = 1
        max_page = 1
        
        while (current_page <= max_page):
            structures_request = esi_handler.call("/corporations/{corporation_id}/structures/", corporation_id=self.id, page=current_page, retries=1)
            
            if structures_request["Success"]:
                
                max_page = int(structures_request["Headers"]["X-Pages"])
                
                for each_structure in structures_request["Data"]:
                    
                    if include_ids:
                        self.structure_data[each_structure["structure_id"]] = {
                            "ID": each_structure["structure_id"],
                            "Name": (each_structure["name"] if "name" in each_structure else None),
                            "Type ID": each_structure["type_id"],
                            "Type Name": type_data[str(each_structure["type_id"])],
                            "Owner ID": self.id,
                            "Owner Name": self.name,
                            "Owner Ticker": self.ticker,
                            "System ID": each_structure["system_id"],
                            "Region ID": geographic_data[str(each_structure["system_id"])]["region_id"],
                            "System Name": geographic_data[str(each_structure["system_id"])]["name"],
                            "Region Name": geographic_data[str(each_structure["system_id"])]["region"],
                            "State": each_structure["state"],
                            "Fuel Expires": (each_structure["fuel_expires"] if "fuel_expires" in each_structure else None),
                            "Online Services": "\n".join([x["name"] for x in each_structure["services"] if x["state"] == "online"]) if "services" in each_structure else None,
                            "Offline Services": "\n".join([x["name"] for x in each_structure["services"] if x["state"] == "offline"]) if "services" in each_structure else None,
                            "Has Drill": ("services" in each_structure and {"name": "Moon Drilling", "state": "online"} in each_structure["services"]),
                            "RF Timer": (each_structure["state_timer_end"] if "state_timer_end" in each_structure else None),
                            "Reinforce Hour": (each_structure["reinforce_hour"] if "reinforce_hour" in each_structure else None),
                            "Unanchor Timer": (each_structure["unanchors_at"] if "unanchors_at" in each_structure else None)
                        }
                    else:
                        self.structure_data[each_structure["structure_id"]] = {
                            "Name": (each_structure["name"] if "name" in each_structure else None),
                            "Type Name": type_data[str(each_structure["type_id"])],
                            "Owner Name": self.name,
                            "Owner Ticker": self.ticker,
                            "System Name": geographic_data[str(each_structure["system_id"])]["name"],
                            "Region Name": geographic_data[str(each_structure["system_id"])]["region"],
                            "State": each_structure["state"],
                            "Fuel Expires": (each_structure["fuel_expires"] if "fuel_expires" in each_structure else None),
                            "Online Services": "\n".join([x["name"] for x in each_structure["services"] if x["state"] == "online"]) if "services" in each_structure else None,
                            "Offline Services": "\n".join([x["name"] for x in each_structure["services"] if x["state"] == "offline"]) if "services" in each_structure else None,
                            "Has Drill": ("services" in each_structure and {"name": "Moon Drilling", "state": "online"} in each_structure["services"]),
                            "RF Timer": (each_structure["state_timer_end"] if "state_timer_end" in each_structure else None),
                            "Reinforce Hour": (each_structure["reinforce_hour"] if "reinforce_hour" in each_structure else None),
                            "Unanchor Timer": (each_structure["unanchors_at"] if "unanchors_at" in each_structure else None)
                        }
                
            else:
                
                raise Exception("STRUCTURES ERROR")
            
            current_page += 1
            
    def get_extractions(self, auth_handler, login_name):
        
        access_token = auth_handler.getAccessToken(self.source, login_name)
        
        if access_token is None:
            raise Exception("ACCESS TOKEN ERROR")
        
        esi_handler = ESI.Handler(access_token)
        
        current_page = 1
        max_page = 1
        
        while (current_page <= max_page):
            extractions_request = esi_handler.call("/corporation/{corporation_id}/mining/extractions/", corporation_id=self.id, page=current_page, retries=1)
            
            if extractions_request["Success"]:
                
                max_page = int(extractions_request["Headers"]["X-Pages"])
                
                for each_extraction in extractions_request["Data"]:
                    
                    self.extractions[each_extraction["structure_id"]] = {
                        "Structure ID": each_extraction["structure_id"],
                        "Start Time": each_extraction["extraction_start_time"],
                        "End Time": each_extraction["chunk_arrival_time"],
                        "Auto-Detonate Time": each_extraction["natural_decay_time"],
                        "Moon ID": each_extraction["moon_id"]
                    }
                
            else:
                
                raise Exception("EXTRACTIONS ERROR")
            
            current_page += 1
        
    def get_starbases(self, auth_handler, login_name, geographic_data, type_data, include_ids):
        
        access_token = auth_handler.getAccessToken(self.source, login_name)
        
        if access_token is None:
            raise Exception("ACCESS TOKEN ERROR")
        
        esi_handler = ESI.Handler(access_token)
        
        moons_to_check = {}
        
        current_page = 1
        max_page = 1
        
        while (current_page <= max_page):
            starbase_request = esi_handler.call("/corporations/{corporation_id}/starbases/", corporation_id=self.id, page=current_page, retries=1)
            
            if starbase_request["Success"]:
                
                max_page = int(starbase_request["Headers"]["X-Pages"])
                
                for each_pos in starbase_request["Data"]:
                    
                    if include_ids:
                        self.starbase_data[each_pos["starbase_id"]] = {
                            "ID": each_pos["starbase_id"],
                            "Type ID": each_pos["type_id"],
                            "Type Name": type_data[str(each_pos["type_id"])],
                            "Owner ID": self.id,
                            "Owner Name": self.name,
                            "Owner Ticker": self.ticker,
                            "Moon ID": each_pos["moon_id"] if "moon_id" in each_pos else None,
                            "System ID": each_pos["system_id"],
                            "Region ID": geographic_data[str(each_pos["system_id"])]["region_id"],
                            "Moon Name": None,
                            "System Name": geographic_data[str(each_pos["system_id"])]["name"],
                            "Region Name": geographic_data[str(each_pos["system_id"])]["region"],
                            "State": each_pos["state"],
                            "RF Timer": (each_pos["reinforced_until"] if "reinforced_until" in each_pos else None),
                            "Unanchored At": (each_pos["unanchor_at"] if "unanchor_at" in each_pos else None)
                        }
                    else:
                        self.starbase_data[each_pos["starbase_id"]] = {
                            "Type Name": type_data[str(each_pos["type_id"])],
                            "Owner Name": self.name,
                            "Owner Ticker": self.ticker,
                            "Moon ID": each_pos["moon_id"] if "moon_id" in each_pos else None,
                            "Moon Name": None,
                            "System Name": geographic_data[str(each_pos["system_id"])]["name"],
                            "Region Name": geographic_data[str(each_pos["system_id"])]["region"],
                            "State": each_pos["state"],
                            "RF Timer": (each_pos["reinforced_until"] if "reinforced_until" in each_pos else None),
                            "Unanchored At": (each_pos["unanchor_at"] if "unanchor_at" in each_pos else None)
                        }
                        
                    if "moon_id" in each_pos and each_pos["moon_id"] not in moons_to_check:
                        moons_to_check[each_pos["moon_id"]] = None
                
            else:
                
                raise Exception("STARBASES ERROR")
            
            current_page += 1
            
        for each_moon in moons_to_check:
            
            moon_request = esi_handler.call("/universe/moons/{moon_id}/", moon_id=each_moon, retries=1)
            
            if moon_request["Success"]:
                moons_to_check[each_moon] = moon_request["Data"]["name"]
                
            else:
                raise Exception("MOONS ERROR")
                
        for each_starbase in self.starbase_data:
            self.starbase_data[each_starbase]["Moon Name"] = moons_to_check[self.starbase_data[each_starbase]["Moon ID"]] if self.starbase_data[each_starbase]["Moon ID"] is not None else None
            if not include_ids:
                del self.starbase_data[each_starbase]["Moon ID"]

class App:
    
    def __init__(self, target_alliances, target_corporations, target_exclusions, core_info, include_ids):
        
        self.target_corporations = target_corporations
        self.target_alliances = target_alliances
        self.target_exclusions = target_exclusions
        self.corporations = []
        self.corporation_data = {}
        
        self.auth_handler = ESI.NeucoreAuth(core_info["AppID"], core_info["AppSecret"], core_info["AppURL"])
        self.core_info = core_info
        self.esi_handler = ESI.Handler()
        
        self.ids_to_parse = {}
        self.structures = {}
        self.extractions = {}
        self.starbases = {}
        self.unknowns = {}
        
        self.pull_static()
        self.build_targets()
        self.get_valid_tokens()
        self.get_names()
        self.process_corporations(include_ids)
        
    def pull_static(self):
        
        with open(dataFile("/static") + "/TypeIDs.json") as knownData:
            self.type_ids = json.load(knownData)
            
        with open(dataFile("/static") + "/geographicInformationV3.json") as knownData:
            self.geographic_data = json.load(knownData)
            
    def build_targets(self):
        
        for each_alliance in self.target_alliances:
            
            corporations_request = self.esi_handler.call("/alliances/{alliance_id}/corporations/", alliance_id=each_alliance, retries=1)
            
            if corporations_request["Success"]:
                self.corporations += corporations_request["Data"]
                
            else:
                raise Exception("CORPORATIONS ERROR")
                
        self.corporations = [int(ids) for ids in self.corporations if str(ids) not in self.target_exclusions]
                
        self.corporation_data = {int(ids): None for ids in self.corporations}
        
        for each_corporation in self.corporation_data:
            if int(each_corporation) not in self.ids_to_parse:
                self.ids_to_parse[int(each_corporation)] = None
        
    def get_valid_tokens(self):
        
        known_tokens = self.auth_handler.getTokenCharacters(self.core_info["LoginName"])
        
        for each_token in known_tokens:
            
            corporation_id = int(each_token["corporationId"])
            character_id = int(each_token["characterId"])
            
            if corporation_id in self.corporations and self.corporation_data[corporation_id] is None:
                
                self.corporation_data[corporation_id] = Corporation(corporation_id, character_id)
                
                print("Found token for " + str(corporation_id) + " from " + str(character_id) + "...")
                
    def get_names(self):
        
        names_request = self.esi_handler.call("/universe/names/", ids=list(self.ids_to_parse.keys()), retries=1)
        
        if names_request["Success"]:
            
            for each_name in names_request["Data"]:
                
                self.ids_to_parse[each_name["id"]] = each_name["name"]
            
        else:
            
            raise Exception("NAMES ERROR")
            
    def process_corporations(self, include_ids):
        
        for each_corporation in self.corporation_data:
            
            if self.corporation_data[each_corporation] is not None:
                
                print("Checking " + str(each_corporation) + "...")
                self.corporation_data[each_corporation].get_structures(self.auth_handler, self.core_info["LoginName"], self.geographic_data, self.type_ids, include_ids)
                self.corporation_data[each_corporation].get_extractions(self.auth_handler, self.core_info["LoginName"])
                self.corporation_data[each_corporation].get_starbases(self.auth_handler, self.core_info["LoginName"], self.geographic_data, self.type_ids, include_ids)
                
                self.structures = self.structures | self.corporation_data[each_corporation].structure_data
                self.extractions = self.extractions | self.corporation_data[each_corporation].extractions
                self.starbases = self.starbases | self.corporation_data[each_corporation].starbase_data
                
            else:
                
                self.unknowns[each_corporation] = self.ids_to_parse[each_corporation]
                
        self.structures = dict(sorted(self.structures.items(), key=lambda x: (str(x[1]["Owner Name"]), str(x[1]["System Name"]))))
        self.starbases = dict(sorted(self.starbases.items(), key=lambda x: (str(x[1]["Owner Name"]), str(x[1]["Moon Name"]))))
                
    def export_json(self, file_name):
        
        print("Exporting JSONs...")
        
        with open((file_name.removesuffix(".json") + "_citadels.json"), "w") as json_file:
            json.dump(self.structures, json_file, indent=1)
            
        with open((file_name.removesuffix(".json") + "_starbases.json"), "w") as json_file:
            json.dump(self.starbases, json_file, indent=1)
        
    def export_csv(self, file_name):
        
        print("Exporting CSVs...")
        
        with open((file_name.removesuffix(".csv") + "_citadels.csv"), "w", newline='') as csv_file:
            fields = list(self.structures.values())[0].keys()
            csv_writer = DictWriter(csv_file, fieldnames=fields)
            
            csv_writer.writeheader()
            for each_structure in self.structures.values():
                csv_writer.writerow(each_structure)
                
        with open((file_name.removesuffix(".csv") + "_starbases.csv"), "w", newline='') as csv_file:
            fields = list(self.starbases.values())[0].keys()
            csv_writer = DictWriter(csv_file, fieldnames=fields)
            
            csv_writer.writeheader()
            for each_starbase in self.starbases.values():
                csv_writer.writerow(each_starbase)
        
    def export_unknowns(self, file_name):
        
        print("Exporting Unknowns...")
        
        with open(file_name, "w") as unknowns_file:
            json.dump(self.unknowns, unknowns_file, indent=1)
        
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
        
    def make_report(self,
        platform, 
        url, 
        title, 
        fuel_threshold,
        include_fuel,
        include_pos,
        include_offline_services,
        include_extractions,
        include_siege,
        include_unanchoring,
        include_auth,
        use_tickers,
        no_corp_names
    ):
        
        report_template = "{name} ({type}) — {message}\n" if no_corp_names else "[{owner}] {name} ({type}) — {message}\n"
        
        report_components = [f"*{title}*\n\n"]
        
        if include_unanchoring:
            
            report_parts = [
                report_template.format(
                    name=x["Name"],
                    type=x["Type Name"],
                    owner=x["Owner Ticker"] if use_tickers else x["Owner Name"],
                    message="Unanchors: " + x["Unanchor Timer"]
                )
                for y, x in self.structures.items()
                if x["Unanchor Timer"] is not None
            ]
            
            report_components += self.split_report(report_parts, "Unanchoring Alerts")
        
        if include_fuel:
            
            report_parts = [
                report_template.format(
                    name=x["Name"],
                    type=x["Type Name"],
                    owner=x["Owner Ticker"] if use_tickers else x["Owner Name"],
                    message="Fuel Expires: " + x["Fuel Expires"]
                )
                for y, x in self.structures.items()
                if x["Fuel Expires"] is not None and (datetime.fromisoformat(x["Fuel Expires"]).timestamp() - time.time()) < (fuel_threshold * 60 * 60)
            ]
            
            report_components += self.split_report(report_parts, "Fuel Alerts")
            
        if include_siege:
            
            report_parts = [
                report_template.format(
                    name=x["Name"],
                    type=x["Type Name"],
                    owner=x["Owner Ticker"] if use_tickers else x["Owner Name"],
                    message=(x["State"].replace("_", " ").title() + " until " + x["RF Timer"])
                )
                for y, x in self.structures.items()
                if x["RF Timer"] is not None
            ]
            
            report_components += self.split_report(report_parts, "Siege Alerts")
            
        if include_offline_services:
            
            report_parts = [
                report_template.format(
                    name=x["Name"],
                    type=x["Type Name"],
                    owner=x["Owner Ticker"] if use_tickers else x["Owner Name"],
                    message=("Offline Services: " + x["Offline Services"].replace("\n", ", "))
                )
                for y, x in self.structures.items()
                if x["Offline Services"]
            ]
            
            report_components += self.split_report(report_parts, "Offline Service Alerts")
            
        if include_extractions:
            
            report_parts = [
                report_template.format(
                    name=x["Name"],
                    type=x["Type Name"],
                    owner=x["Owner Ticker"] if use_tickers else x["Owner Name"],
                    message="No Extraction Scheduled" if y not in self.extractions else "Auto-Detonation at: " + self.extractions[y]["Auto-Detonate Time"]
                )
                for y, x in self.structures.items()
                if x["Has Drill"] and (y not in self.extractions or datetime.fromisoformat(self.extractions[y]["End Time"]).timestamp() < time.time())
            ]
            
            report_components += self.split_report(report_parts, "Extraction Alerts")
            
        if include_pos and include_unanchoring:
            
            report_parts = [
                report_template.format(
                    name=x["System Name"] + " - Unknown Moon",
                    type=x["Type Name"],
                    owner=x["Owner Ticker"] if use_tickers else x["Owner Name"],
                    message=x["State"].title()
                )
                for y, x in self.starbases.items()
                if x["State"] in ["onlining", "unanchoring"]
            ]
            
            report_components += self.split_report(report_parts, "POS State Change Alerts")
            
        if include_pos and include_siege:
            
            report_parts = [
                report_template.format(
                    name=x["Moon Name"],
                    type=x["Type Name"],
                    owner=x["Owner Ticker"] if use_tickers else x["Owner Name"],
                    message="Reinforced until: " + x["RF Timer"]
                )
                for y, x in self.starbases.items()
                if x["RF Timer"] is not None
            ]
            
            report_components += self.split_report(report_parts, "POS Siege Alerts")
            
        if include_pos and include_offline_services:
            
            report_parts = [
                report_template.format(
                    name=x["Moon Name"],
                    type=x["Type Name"],
                    owner=x["Owner Ticker"] if use_tickers else x["Owner Name"],
                    message="Offline"
                )
                for y, x in self.starbases.items()
                if x["State"] == "offline"
            ]
            
            report_components += self.split_report(report_parts, "POS Offline Alerts")
            
        if include_auth:
            
            auth_string = "\n".join(list(self.unknowns.values()))
            
            if auth_string:
                report_components.append(f"Target Corporations Not Authed\n```\n{auth_string}\n```")
        
        for each_message in report_components:
            relay = RelayTerminus(each_message, platform, url)
            relay.send(5)
