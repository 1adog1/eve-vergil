from datetime import datetime, timedelta, UTC
from math import floor

import ESI
from EveObjects import UpwellStructure, Starbase, SovHub, Extraction

reference_time = datetime.now(UTC)

class Corporation:
    
    def __init__(self, id, source_id):
        
        self.id = id
        self.name = None
        self.ticker = None
        self.source = source_id
        self.structure_data = {}
        self.extractions = {}
        self.starbase_data = {}
        self.sov_data = {}
        
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

    def get_sov(self, auth_handler, login_name, geographic_data, type_data):

        access_token = auth_handler.getAccessToken(self.source, login_name)
        
        if access_token is None:
            raise Exception("FAILED TO GET ACCESS TOKEN FROM NEUCORE FOR {source}".format(source=self.source))
        
        esi_handler = ESI.Handler(access_token)

        sov_hub_list_request = esi_handler.call("/corporations/{corporation_id}/structures/sovereignty-hubs/", corporation_id=self.id, retries=2)

        if sov_hub_list_request["Success"]:

            sov_hub_list = [x["id"] for x in sov_hub_list_request["Data"]["sovereignty_hubs"]]

        else:
            
            raise Exception(
                "SOV HUB LIST ERROR\n\nRepsonse Data: {data}\n\nResponse Headers: {headers}".format(
                    data=sov_hub_list_request["Data"],
                    headers=sov_hub_list_request["Headers"]
                )
            )
        
        for each_sov_hub in sov_hub_list:

            # We could be making quite a few of these requests
            access_token = auth_handler.getAccessToken(self.source, login_name)
            
            if access_token is None:
                raise Exception("FAILED TO GET ACCESS TOKEN FROM NEUCORE FOR {source}".format(source=self.source))
            
            esi_handler = ESI.Handler(access_token)

            sov_hub_request = esi_handler.call("/corporations/{corporation_id}/structures/sovereignty-hubs/{sovereignty_hub_id}/", corporation_id=self.id, sovereignty_hub_id=each_sov_hub, retries=2)

            if sov_hub_request["Success"]:
                
                sov_hub_data = sov_hub_request["Data"]

                # Some of this we need to build here with the help of our type / geographic data
                reagent_bay = {
                    x["type_id"]: {
                        "Name": type_data[str(x["type_id"])],
                        "Quantity": x["amount"]
                    }
                    for x in sov_hub_data["reagent_bay"]["reagents"]
                }
                reagent_usage = {
                    x["type_id"]: {
                        "Name": type_data[str(x["type_id"])],
                        "Usage": x["burning_per_hour"]
                    }
                    for x in sov_hub_data["reagent_bay"]["reagents"]
                }
                reagent_expirations = {
                    x["type_id"]: {
                        "Name": type_data[str(x["type_id"])],
                        "Hours Remaining": floor(x["amount"] / x["burning_per_hour"]),
                        "Expires": (reference_time + timedelta(hours=(floor(x["amount"] / x["burning_per_hour"]) + 1))).replace(minute=0, second=0, microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")
                    }
                    for x in sov_hub_data["reagent_bay"]["reagents"] if x["burning_per_hour"] is not None and x["burning_per_hour"] != 0
                }
                upgrades = {
                    x["type_id"]: {
                        "Name": type_data[str(x["type_id"])],
                        "State": x["power_state"]
                    }
                    for x in sov_hub_data["upgrades"]
                }

                # Workforce Configuration - This is a "one of" condition, this is messy but it should work
                for each_configuration, configuration_data in sov_hub_data["workforce_transport"]["configuration"].items():

                    workforce_configuration = each_configuration

                    if workforce_configuration == "import":
                        configured_import_sources = {
                            x["solar_system_id"]: {
                                "Name": geographic_data[str(x["solar_system_id"])]["name"],
                                "Region ID": geographic_data[str(x["solar_system_id"])]["region_id"],
                                "Region": geographic_data[str(x["solar_system_id"])]["region"],
                                "Amount": 0
                            }
                            for x in configuration_data["sources"]
                        }
                    else:
                        configured_import_sources = {}

                    if workforce_configuration == "export":
                        configured_export = {
                            "ID": configuration_data["solar_system_id"],
                            "Name": geographic_data[str(configuration_data["solar_system_id"])]["name"],
                            "Region ID": geographic_data[str(configuration_data["solar_system_id"])]["region_id"],
                            "Region": geographic_data[str(configuration_data["solar_system_id"])]["region"],
                            "Amount": configuration_data["amount"]
                        }
                    else:
                        configured_export = {}

                # Workforce State - This is a "one of" condition, this is messy but it should work
                for each_state, state_data in sov_hub_data["workforce_transport"]["state"].items():
                    
                    workforce_state = each_state

                    if workforce_state == "import":
                        current_import_sources = {
                            x["solar_system_id"]: {
                                "Name": geographic_data[str(x["solar_system_id"])]["name"],
                                "Region ID": geographic_data[str(x["solar_system_id"])]["region_id"],
                                "Region": geographic_data[str(x["solar_system_id"])]["region"],
                                "Amount": 0
                            }
                            for x in state_data["sources"]
                        }
                    else:
                        current_import_sources = {}

                    if workforce_state == "export":
                        current_export = {
                            "ID": state_data["solar_system_id"],
                            "Name": geographic_data[str(state_data["solar_system_id"])]["name"],
                            "Region ID": geographic_data[str(state_data["solar_system_id"])]["region_id"],
                            "Region": geographic_data[str(state_data["solar_system_id"])]["region"],
                            "Amount": state_data["amount"]
                        }
                    else:
                        current_export = {}

                # Finally Building our SovHub Object
                self.sov_data[sov_hub_data["solar_system_id"]] = SovHub(
                    id = sov_hub_data["id"],
                    owner_id = self.id,
                    owner_name = self.name,
                    owner_ticker = self.ticker,
                    system_id = sov_hub_data["solar_system_id"],
                    system = geographic_data[str(sov_hub_data["solar_system_id"])]["name"],
                    region_id = geographic_data[str(sov_hub_data["solar_system_id"])]["region_id"],
                    region = geographic_data[str(sov_hub_data["solar_system_id"])]["region"],
                    fuel_acl_id = sov_hub_data["fuel_access_list_id"] if "fuel_access_list_id" in sov_hub_data else None,
                    reagent_bay = reagent_bay,
                    reagent_usage = reagent_usage,
                    reagent_expirations = reagent_expirations,
                    resources = sov_hub_data["resources"],
                    workforce_configuration = workforce_configuration, 
                    configured_import_sources = configured_import_sources,
                    configured_export = configured_export,
                    workforce_state = workforce_state, 
                    current_import_sources = current_import_sources,
                    current_export = current_export,
                    upgrades = upgrades
                )

            else:
                
                raise Exception(
                    "SOV HUB ERROR\n\nRepsonse Data: {data}\n\nResponse Headers: {headers}".format(
                        data=sov_hub_request["Data"],
                        headers=sov_hub_request["Headers"]
                    )
                )
            
        # Building Import Amounts
        for each_system, each_sov_hub in self.sov_data.items():

            if each_sov_hub.workforce_configuration == "import":

                for each_import_system, each_import_data in each_sov_hub.configured_import_sources.items():

                    if self.sov_data[each_import_system].configured_export["ID"] == each_system:
                        each_import_data["Amount"] = self.sov_data[each_import_system].configured_export["Amount"]

            if each_sov_hub.workforce_state == "import":

                for each_import_system, each_import_data in each_sov_hub.current_import_sources.items():
                    
                    if self.sov_data[each_import_system].current_export["ID"] == each_system:
                        each_import_data["Amount"] = self.sov_data[each_import_system].current_export["Amount"]
                
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

    def usage_calculations(self):

        for each_structure in self.structure_data:

            current = self.structure_data[each_structure]

            # Reagent Usage
            if current.online_services and current.type_id in current.reagent_consumption:
                
                minimum_time = None

                for each_reagent in current.reagent_consumption[current.type_id]:

                    if each_reagent in current.fuel:

                        hours_remaining = floor(current.fuel[each_reagent]["Quantity"] / current.reagent_consumption[current.type_id][each_reagent])
                        minimum_time = hours_remaining if (minimum_time is None or hours_remaining < minimum_time) else minimum_time

                    else:

                        minimum_time = 0

                current.reagent_expiry = (reference_time + timedelta(hours=(minimum_time + 1))).replace(minute=0, second=0, microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")

        for each_starbase in self.starbase_data:

            current = self.starbase_data[each_starbase]

            # Fuel Usage
            if current.state != "offline" and current.type_id in current.fuel_consumption:

                hours_remaining = 0

                for each_fuel in current.fuel_consumption[current.type_id]:

                    if each_fuel in current.fuel:

                        hours_remaining += floor(current.fuel[each_fuel]["Quantity"] / current.fuel_consumption[current.type_id][each_fuel])

                current.fuel_expiry = (reference_time + timedelta(hours=(hours_remaining + 1))).replace(minute=0, second=0, microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")

            # Strontium Hours
            if current.state != "reinforced":

                strontium_consumption = None

                if current.type.endswith("Control Tower"):
                    strontium_consumption = 400
                if current.type.endswith("Control Tower Medium"):
                    strontium_consumption = 200
                if current.type.endswith("Control Tower Small"):
                    strontium_consumption = 100

                if strontium_consumption is not None:

                    current.strontium_hours = round((current.strontium / strontium_consumption), 3)
