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

class UpwellStructure:

    def __init__(
        self,
        id,
        name,
        type_id,
        type_name,
        owner_id,
        owner_name,
        owner_ticker,
        system_id,
        system_name,
        region_id,
        region_name,
        state,
        services,
        online_services,
        offline_services,
        has_drill,
        fuel_expiry,
        timer,
        unanchor_timer, 
        reinforcement_hour,
        ):

        self.id = id
        self.name = name
        self.type_id = type_id
        self.type = type_name
        self.owner_id = owner_id
        self.owner_name = owner_name
        self.owner_ticker = owner_ticker
        self.system_id = system_id
        self.system = system_name
        self.region_id = region_id
        self.region = region_name
        self.state = state
        self.high_slots = {}
        self.mid_slots = {}
        self.low_slots = {}
        self.rigs = {}
        self.service_modules = {}
        self.services = services
        self.online_services = online_services
        self.offline_services = offline_services
        self.has_drill = has_drill
        self.fuel = {}
        self.ozone = 0
        self.fuel_expiry = fuel_expiry
        self.timer = timer
        self.unanchor_timer = unanchor_timer
        self.reinforcement_hour = reinforcement_hour

    def export(self):

        self.fitting = "[{type_name}, {name}]\n\n{lows}\n\n{mids}\n\n{highs}\n\n{rigs}\n\n{services}".format(
            type_name = self.type,
            name = self.name,
            lows = "\n".join([y for x, y in sorted(self.low_slots.items())]),
            mids = "\n".join([y for x, y in sorted(self.mid_slots.items())]),
            highs = "\n".join([y for x, y in sorted(self.high_slots.items())]),
            rigs = "\n".join([y for x, y in sorted(self.rigs.items())]),
            services = "\n".join([y for x, y in sorted(self.service_modules.items())]),
        )

        return {
            "Name": self.name,
            "Type": self.type,
            "Owner": self.owner_name,
            "Owner Ticker": self.owner_ticker,
            "System": self.system,
            "Region": self.region,
            "State": self.state,
            "Fitting": self.fitting,
            "Online Services": "\n".join(self.online_services),
            "Offline Services": "\n".join(self.offline_services),
            "Has Drill": self.has_drill,
            "Fuel": "\n".join(["{quantity:,} {type_name}s".format(quantity=x["Quantity"], type_name=x["Name"]) for x in self.fuel.values()]),
            "Ozone": self.ozone if self.type_id == 35841 else None,
            "Fuel Expires": self.fuel_expiry,
            "Timer": self.timer,
            "Unanchor Timer": self.unanchor_timer,
            "Reinforcement Hour": self.reinforcement_hour
        }

class Starbase:

    def __init__(
        self,
        id,
        moon_id,
        moon,
        type_id,
        type_name,
        owner_id,
        owner_name,
        owner_ticker,
        system_id,
        system_name,
        region_id,
        region_name,
        state,
        timer,
        unanchor_timer
    ):

        self.id = id
        self.moon_id = moon_id
        self.moon = moon
        self.type_id = type_id
        self.type = type_name
        self.owner_id = owner_id
        self.owner_name = owner_name
        self.owner_ticker = owner_ticker
        self.system_id = system_id
        self.system = system_name
        self.region_id = region_id
        self.region = region_name
        self.state = state
        self.fuel = {}
        self.strontium = 0
        self.timer = timer
        self.unanchor_timer = unanchor_timer

    def export(self):

        return {
            "Moon": self.moon,
            "Type": self.type,
            "Owner": self.owner_name,
            "Owner Ticker": self.owner_ticker,
            "System": self.system,
            "Region": self.region,
            "State": self.state,
            "Fuel": "\n".join(["{quantity:,} {type_name}s".format(quantity=x["Quantity"], type_name=x["Name"]) for x in self.fuel.values()]),
            "Strontium": self.strontium,
            "Timer": self.timer,
            "Unanchor Timer": self.unanchor_timer
        }

class Extraction:

    def __init__(self, id, moon_id, start_time, end_time, auto_time):

        self.id = id
        self.moon_id = moon_id
        self.start_time = start_time
        self.end_time = end_time
        self.auto_time = auto_time

class Corporation:
    
    def __init__(self, id, source_id):
        
        self.id = id
        self.name = None
        self.ticker = None
        self.source = source_id
        self.structure_data = {}
        self.extractions = {}
        self.starbase_data = {}
        self.fuel = {}
        
        self.get_name()
        
    def get_name(self):
        
        esi_handler = ESI.Handler()
        
        name_request = esi_handler.call("/corporations/{corporation_id}/", corporation_id=self.id, retries=2)
        
        if name_request["Success"]:
            
            self.name = name_request["Data"]["name"]
            self.ticker = name_request["Data"]["ticker"]
            
        else:
            
            raise Exception(
                "CORPORATION NAME ERROR\n\nRepsonse Data: {data}\n\nResponse Headers: {headers}".format(
                    data=name_request["Data"],
                    headers=name_request["Headers"]
                )
            )
        
    def get_structures(self, auth_handler, login_name, geographic_data, type_data):
        
        access_token = auth_handler.getAccessToken(self.source, login_name)
        
        if access_token is None:
            raise Exception("FAILED TO GET ACCESS TOKEN FROM NEUCORE FOR {source}".format(source=self.source))
        
        esi_handler = ESI.Handler(access_token)
        
        current_page = 1
        max_page = 1
        
        while (current_page <= max_page):
            structures_request = esi_handler.call("/corporations/{corporation_id}/structures/", corporation_id=self.id, page=current_page, retries=2)
            
            if structures_request["Success"]:
                
                max_page = int(structures_request["Headers"]["X-Pages"])
                
                for each_structure in structures_request["Data"]:

                    self.structure_data[each_structure["structure_id"]] = UpwellStructure(
                        id = each_structure["structure_id"],
                        name = (each_structure["name"] if "name" in each_structure else None),
                        type_id = each_structure["type_id"],
                        type_name = type_data[str(each_structure["type_id"])],
                        owner_id = self.id,
                        owner_name = self.name,
                        owner_ticker = self.ticker,
                        system_id = each_structure["system_id"],
                        system_name = geographic_data[str(each_structure["system_id"])]["name"],
                        region_id = geographic_data[str(each_structure["system_id"])]["region_id"],
                        region_name = geographic_data[str(each_structure["system_id"])]["region"],
                        state = each_structure["state"],
                        services = ([x["name"] for x in each_structure["services"]] if "services" in each_structure else None),
                        online_services = ([x["name"] for x in each_structure["services"] if x["state"] == "online"] if "services" in each_structure else None),
                        offline_services = ([x["name"] for x in each_structure["services"] if x["state"] == "offline"] if "services" in each_structure else None),
                        has_drill = ("services" in each_structure and {"name": "Moon Drilling", "state": "online"} in each_structure["services"]),
                        fuel_expiry = (each_structure["fuel_expires"] if "fuel_expires" in each_structure else None),
                        timer = (each_structure["state_timer_end"] if "state_timer_end" in each_structure else None),
                        unanchor_timer = (each_structure["unanchors_at"] if "unanchors_at" in each_structure else None),
                        reinforcement_hour = (each_structure["reinforce_hour"] if "reinforce_hour" in each_structure else None)
                    )
                
            else:
                
                raise Exception(
                    "STRUCTURES ERROR\n\nRepsonse Data: {data}\n\nResponse Headers: {headers}".format(
                        data=structures_request["Data"],
                        headers=structures_request["Headers"]
                    )
                )
            
            current_page += 1
    
    def get_extractions(self, auth_handler, login_name):
        
        access_token = auth_handler.getAccessToken(self.source, login_name)
        
        if access_token is None:
            raise Exception("FAILED TO GET ACCESS TOKEN FROM NEUCORE FOR {source}".format(source=self.source))
        
        esi_handler = ESI.Handler(access_token)
        
        current_page = 1
        max_page = 1
        
        while (current_page <= max_page):
            extractions_request = esi_handler.call("/corporation/{corporation_id}/mining/extractions/", corporation_id=self.id, page=current_page, retries=2)
            
            if extractions_request["Success"]:
                
                max_page = int(extractions_request["Headers"]["X-Pages"])
                
                for each_extraction in extractions_request["Data"]:

                    self.extractions[each_extraction["structure_id"]] = Extraction(
                        id = each_extraction["structure_id"],
                        moon_id = each_extraction["moon_id"],
                        start_time = each_extraction["extraction_start_time"],
                        end_time = each_extraction["chunk_arrival_time"],
                        auto_time = each_extraction["natural_decay_time"]
                    )
                
            else:
                
                raise Exception(
                    "EXTRACTIONS ERROR\n\nRepsonse Data: {data}\n\nResponse Headers: {headers}".format(
                        data=extractions_request["Data"],
                        headers=extractions_request["Headers"]
                    )
                )
            
            current_page += 1
        
    def get_starbases(self, auth_handler, login_name, geographic_data, type_data):
        
        access_token = auth_handler.getAccessToken(self.source, login_name)
        
        if access_token is None:
            raise Exception("FAILED TO GET ACCESS TOKEN FROM NEUCORE FOR {source}".format(source=self.source))
        
        esi_handler = ESI.Handler(access_token)
                
        current_page = 1
        max_page = 1
        
        while (current_page <= max_page):
            starbase_request = esi_handler.call("/corporations/{corporation_id}/starbases/", corporation_id=self.id, page=current_page, retries=2)
            
            if starbase_request["Success"]:
                
                max_page = int(starbase_request["Headers"]["X-Pages"])
                
                for each_pos in starbase_request["Data"]:

                    if "moon_id" in each_pos:

                        moon_request = esi_handler.call("/universe/moons/{moon_id}/", moon_id=each_pos["moon_id"], retries=2)
                        
                        if moon_request["Success"]:
                            moon_name = moon_request["Data"]["name"]
                            
                        else:
                            raise Exception(
                                "MOONS ERROR\n\nRepsonse Data: {data}\n\nResponse Headers: {headers}".format(
                                    data=moon_request["Data"],
                                    headers=moon_request["Headers"]
                                )
                            )
                        
                    else:
                        moon_name = None

                    self.starbase_data[each_pos["starbase_id"]] = Starbase(
                        id = each_pos["starbase_id"],
                        moon_id = each_pos["moon_id"] if "moon_id" in each_pos else None,
                        moon = moon_name,
                        type_id = each_pos["type_id"],
                        type_name = type_data[str(each_pos["type_id"])],
                        owner_id = self.id,
                        owner_name = self.name,
                        owner_ticker = self.ticker,
                        system_id = each_pos["system_id"],
                        system_name = geographic_data[str(each_pos["system_id"])]["name"],
                        region_id = geographic_data[str(each_pos["system_id"])]["region_id"],
                        region_name = geographic_data[str(each_pos["system_id"])]["region"],
                        state = each_pos["state"],
                        timer = (each_pos["reinforced_until"] if "reinforced_until" in each_pos else None),
                        unanchor_timer = (each_pos["unanchor_at"] if "unanchor_at" in each_pos else None)
                    )
                
            else:
                
                raise Exception(
                    "STARBASES ERROR\n\nRepsonse Data: {data}\n\nResponse Headers: {headers}".format(
                        data=starbase_request["Data"],
                        headers=starbase_request["Headers"]
                    )
                )
            
            current_page += 1
                
    def get_assets(self, auth_handler, login_name, type_data):

        current_page = 1
        max_page = 1
        
        while (current_page <= max_page):
            
            access_token = auth_handler.getAccessToken(self.source, login_name)
            
            if access_token is None:
                raise Exception("FAILED TO GET ACCESS TOKEN FROM NEUCORE FOR {source}".format(source=self.source))
            
            esi_handler = ESI.Handler(access_token)
            
            assets_request = esi_handler.call("/corporations/{corporation_id}/assets/", corporation_id=self.id, page=current_page, retries=2)
            
            if assets_request["Success"]:
                
                max_page = int(assets_request["Headers"]["X-Pages"])
                
                for each_asset in assets_request["Data"]:

                    if each_asset["location_id"] in self.structure_data:

                        if each_asset["location_flag"].startswith("HiSlot"):

                            slot = int(each_asset["location_flag"].removeprefix("HiSlot"))
                            type_name = type_data[str(each_asset["type_id"])]
                            self.structure_data[each_asset["location_id"]].high_slots[slot] = type_name

                        if each_asset["location_flag"].startswith("MedSlot"):

                            slot = int(each_asset["location_flag"].removeprefix("MedSlot"))
                            type_name = type_data[str(each_asset["type_id"])]
                            self.structure_data[each_asset["location_id"]].mid_slots[slot] = type_name

                        if each_asset["location_flag"].startswith("LoSlot"):

                            slot = int(each_asset["location_flag"].removeprefix("LoSlot"))
                            type_name = type_data[str(each_asset["type_id"])]
                            self.structure_data[each_asset["location_id"]].low_slots[slot] = type_name

                        if each_asset["location_flag"].startswith("RigSlot"):

                            slot = int(each_asset["location_flag"].removeprefix("RigSlot"))
                            type_name = type_data[str(each_asset["type_id"])]
                            self.structure_data[each_asset["location_id"]].rigs[slot] = type_name

                        if each_asset["location_flag"].startswith("ServiceSlot"):

                            slot = int(each_asset["location_flag"].removeprefix("ServiceSlot"))
                            type_name = type_data[str(each_asset["type_id"])]
                            self.structure_data[each_asset["location_id"]].service_modules[slot] = type_name

                        if each_asset["location_flag"] == "StructureFuel":

                            if each_asset["type_id"] == 16273:

                                self.structure_data[each_asset["location_id"]].ozone += each_asset["quantity"]

                            else:

                                if each_asset["type_id"] not in self.structure_data[each_asset["location_id"]].fuel:

                                    self.structure_data[each_asset["location_id"]].fuel[each_asset["type_id"]] = {"Name": type_data[str(each_asset["type_id"])], "Quantity": 0}

                                self.structure_data[each_asset["location_id"]].fuel[each_asset["type_id"]]["Quantity"] += each_asset["quantity"]

                    if each_asset["location_id"] in self.starbase_data:

                        if each_asset["type_id"] == 16275:

                            self.starbase_data[each_asset["location_id"]].strontium += each_asset["quantity"]

                        else:

                            if each_asset["type_id"] not in self.starbase_data[each_asset["location_id"]].fuel:

                                self.starbase_data[each_asset["location_id"]].fuel[each_asset["type_id"]] = {"Name": type_data[str(each_asset["type_id"])], "Quantity": 0}

                            self.starbase_data[each_asset["location_id"]].fuel[each_asset["type_id"]]["Quantity"] += each_asset["quantity"]
                
            else:
                
                raise Exception(
                    "ASSETS ERROR\n\nRepsonse Data: {data}\n\nResponse Headers: {headers}".format(
                        data=assets_request["Data"],
                        headers=assets_request["Headers"]
                    )
                )
            
            current_page += 1

class App:
    
    def __init__(self, target_alliances, target_corporations, target_exclusions, core_info):
        
        self.target_corporations = target_corporations
        self.target_alliances = target_alliances
        self.target_exclusions = target_exclusions
        self.corporations = target_corporations
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
        self.process_corporations()
        
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
        
        known_tokens = self.auth_handler.getTokenCharacters(self.core_info["LoginName"])
        
        for each_token in known_tokens:
            
            corporation_id = int(each_token["corporationId"])
            character_id = int(each_token["characterId"])
            
            if corporation_id in self.corporations and self.corporation_data[corporation_id] is None:
                
                self.corporation_data[corporation_id] = Corporation(corporation_id, character_id)
                
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
            
    def process_corporations(self):
        
        for each_corporation in self.corporation_data:
            
            if self.corporation_data[each_corporation] is not None:
                
                print("Checking " + str(each_corporation) + "...")
                self.corporation_data[each_corporation].get_structures(self.auth_handler, self.core_info["LoginName"], self.geographic_data, self.type_ids)
                self.corporation_data[each_corporation].get_extractions(self.auth_handler, self.core_info["LoginName"])
                self.corporation_data[each_corporation].get_starbases(self.auth_handler, self.core_info["LoginName"], self.geographic_data, self.type_ids)
                self.corporation_data[each_corporation].get_assets(self.auth_handler, self.core_info["LoginName"], self.type_ids)
                
                self.structures = self.structures | self.corporation_data[each_corporation].structure_data
                self.extractions = self.extractions | self.corporation_data[each_corporation].extractions
                self.starbases = self.starbases | self.corporation_data[each_corporation].starbase_data
                
            else:
                
                self.unknowns[each_corporation] = self.ids_to_parse[each_corporation]
                
        self.structures = dict(sorted(self.structures.items(), key=lambda x: (str(x[1].owner_name), str(x[1].name))))
        self.starbases = dict(sorted(self.starbases.items(), key=lambda x: (str(x[1].owner_name), str(x[1].moon))))
                
    def export_json(self, file_name):
        
        print("Exporting JSONs...")
        
        with open((file_name.removesuffix(".json") + "_citadels.json"), "w") as json_file:
            json.dump({x: y.export() for x, y in self.structures.items()}, json_file, indent=1)
            
        with open((file_name.removesuffix(".json") + "_starbases.json"), "w") as json_file:
            json.dump({x: y.export() for x, y in self.starbases.items()}, json_file, indent=1)
        
    def export_csv(self, file_name):
        
        print("Exporting CSVs...")

        structure_export_data = {x: y.export() for x, y in self.structures.items()}
        starbase_export_data = {x: y.export() for x, y in self.starbases.items()}
        
        with open((file_name.removesuffix(".csv") + "_citadels.csv"), "w", newline="") as csv_file:
            fields = list(structure_export_data.values())[0].keys()
            csv_writer = DictWriter(csv_file, fieldnames=fields)
            
            csv_writer.writeheader()
            for each_structure in structure_export_data.values():
                
                for key, each_val in each_structure.items():
                    each_structure[key] = (" " + each_val) if (isinstance(each_val, str) and each_val.startswith("-")) else each_val
                
                csv_writer.writerow(each_structure)
                
        with open((file_name.removesuffix(".csv") + "_starbases.csv"), "w", newline="") as csv_file:
            fields = list(starbase_export_data.values())[0].keys()
            csv_writer = DictWriter(csv_file, fieldnames=fields)
            
            csv_writer.writeheader()
            for each_starbase in starbase_export_data.values():
                
                for key, each_val in each_starbase.items():
                    each_starbase[key] = (" " + each_val) if (isinstance(each_val, str) and each_val.startswith("-")) else each_val
                
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
        include_boundaries,
        include_fuel,
        include_liquid_ozone,
        include_pos,
        include_offline_services,
        include_extractions,
        include_siege,
        include_deploying,
        include_unanchoring,
        include_auth,
        use_tickers,
        no_corp_names
    ):
        
        report_template = "{name} ({type}) — {message}\n" if no_corp_names else "[{owner}] {name} ({type}) — {message}\n"
        
        report_components = []
        
        if include_boundaries:
            report_components.append(f"*----- BEGIN {title} -----*\n\n")
        
        if include_deploying:
            
            report_parts = [
                report_template.format(
                    name=x.name,
                    type=x.type,
                    owner=x.owner_ticker if use_tickers else x.owner_name,
                    message="Anchors: " + x.timer
                )
                for y, x in self.structures.items()
                if x.state == "anchoring" and x.timer is not None
            ]
            
            report_components += self.split_report(report_parts, "Anchoring Alerts")

        if include_unanchoring:
            
            report_parts = [
                report_template.format(
                    name=x.name,
                    type=x.type,
                    owner=x.owner_ticker if use_tickers else x.owner_name,
                    message="Unanchors: " + x.unanchor_timer
                )
                for y, x in self.structures.items()
                if x.unanchor_timer is not None
            ]
            
            report_components += self.split_report(report_parts, "Unanchoring Alerts")
        
        if include_fuel is not None:
            
            report_parts = [
                report_template.format(
                    name=x.name,
                    type=x.type,
                    owner=x.owner_ticker if use_tickers else x.owner_name,
                    message="Fuel Expires: " + x.fuel_expiry
                )
                for y, x in self.structures.items()
                if x.fuel_expiry is not None and (datetime.fromisoformat(x.fuel_expiry).timestamp() - time.time()) < (include_fuel * 60 * 60)
            ]
            
            report_components += self.split_report(report_parts, "Fuel Alerts")
            
        if include_liquid_ozone is not None:
            
            report_parts = [
                report_template.format(
                    name=x.name,
                    type=x.type,
                    owner=x.owner_ticker if use_tickers else x.owner_name,
                    message="Remaining Ozone: {ozone:,}".format(ozone=x.ozone)
                )
                for y, x in self.structures.items()
                if x.type_id == 35841 and x.ozone < include_liquid_ozone
            ]
            
            report_components += self.split_report(report_parts, "Liquid Ozone Alerts")
            
        if include_siege:
            
            report_parts = [
                report_template.format(
                    name=x.name,
                    type=x.type,
                    owner=x.owner_ticker if use_tickers else x.owner_name,
                    message=(x.state.replace("_", " ").title() + " until " + x.timer)
                )
                for y, x in self.structures.items()
                if "reinforce" in x.state and x.timer is not None
            ]
            
            report_components += self.split_report(report_parts, "Siege Alerts")
            
        if include_offline_services:
            
            report_parts = [
                report_template.format(
                    name=x.name,
                    type=x.type,
                    owner=x.owner_ticker if use_tickers else x.owner_name,
                    message=("Offline Services: " + ", ".join(x.offline_services))
                )
                for y, x in self.structures.items()
                if x.offline_services
            ]
            
            report_components += self.split_report(report_parts, "Offline Service Alerts")
            
        if include_extractions:
            
            report_parts = [
                report_template.format(
                    name=x.name,
                    type=x.type,
                    owner=x.owner_ticker if use_tickers else x.owner_name,
                    message="No Extraction Scheduled" if y not in self.extractions else "Auto-Detonation at: " + self.extractions[y].auto_time
                )
                for y, x in self.structures.items()
                if x.has_drill and (y not in self.extractions or datetime.fromisoformat(self.extractions[y].end_time).timestamp() < time.time())
            ]
            
            report_components += self.split_report(report_parts, "Extraction Alerts")
            
        if include_pos and include_deploying:
            
            report_parts = [
                report_template.format(
                    name=(x.moon if x.moon is not None else x.system + " - Unknown Moon"),
                    type=x.type,
                    owner=x.owner_ticker if use_tickers else x.owner_name,
                    message=x.state.title()
                )
                for y, x in self.starbases.items()
                if x.state == "onlining"
            ]
            
            report_components += self.split_report(report_parts, "POS Onlining Alerts")

        if include_pos and include_unanchoring:
            
            report_parts = [
                report_template.format(
                    name=(x.moon if x.moon is not None else x.system + " - Unknown Moon"),
                    type=x.type,
                    owner=x.owner_ticker if use_tickers else x.owner_name,
                    message=x.state.title()
                )
                for y, x in self.starbases.items()
                if x.state == "unanchoring"
            ]
            
            report_components += self.split_report(report_parts, "POS Unanchoring Alerts")
            
        if include_pos and include_siege:
            
            report_parts = [
                report_template.format(
                    name=(x.moon if x.moon is not None else x.system + " - Unknown Moon"),
                    type=x.type,
                    owner=x.owner_ticker if use_tickers else x.owner_name,
                    message="Reinforced until: " + x.timer
                )
                for y, x in self.starbases.items()
                if x.timer is not None
            ]
            
            report_components += self.split_report(report_parts, "POS Siege Alerts")
            
        if include_pos and include_offline_services:
            
            report_parts = [
                report_template.format(
                    name=(x.moon if x.moon is not None else x.system + " - Unknown Moon"),
                    type=x.type,
                    owner=x.owner_ticker if use_tickers else x.owner_name,
                    message="Offline"
                )
                for y, x in self.starbases.items()
                if x.state == "offline"
            ]
            
            report_components += self.split_report(report_parts, "POS Offline Alerts")
            
        if include_auth:
            
            auth_string = "\n".join(list(self.unknowns.values()))
            
            if auth_string:
                report_components.append(f"Target Corporations Not Authed\n```\n{auth_string}\n```")
                
        if include_boundaries:
            report_components.append(f"*----- END {title} -----*\n\n")
        
        for each_message in report_components:
            relay = RelayTerminus(each_message, platform, url)
            relay.send(5)
