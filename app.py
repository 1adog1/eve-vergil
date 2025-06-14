import inspect
import os
import json

from csv import DictWriter

import ESI

def dataFile(extraFolder):

    filename = inspect.getframeinfo(inspect.currentframe()).filename
    path = os.path.join(os.path.dirname(os.path.abspath(filename)))

    dataLocation = str(path) + extraFolder

    return(dataLocation)

class Corporation:
    
    def __init__(self, id, source_id):
        
        self.id = id
        self.name = None
        self.source = source_id
        self.structure_data = {}
        
    def get_structures(self, auth_handler, login_name, geographic_data, type_data, include_ids):
        
        access_token = auth_handler.getAccessToken(self.source, login_name)
        
        if access_token is None:
            print("ACCESS TOKEN ERROR")
            return
        
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
                            "System ID": each_structure["system_id"],
                            "Region ID": geographic_data[str(each_structure["system_id"])]["region_id"],
                            "System Name": geographic_data[str(each_structure["system_id"])]["name"],
                            "Region Name": geographic_data[str(each_structure["system_id"])]["region"],
                            "State": each_structure["state"],
                            "Fuel Expires": (each_structure["fuel_expires"] if "fuel_expires" in each_structure else None),
                            "RF Timer": (each_structure["state_timer_end"] if "state_timer_end" in each_structure else None),
                            "Reinforce Hour": (each_structure["reinforce_hour"] if "reinforce_hour" in each_structure else None),
                            "Unanchor Timer": (each_structure["unanchors_at"] if "unanchors_at" in each_structure else None)
                        }
                    else:
                        self.structure_data[each_structure["structure_id"]] = {
                            "Name": (each_structure["name"] if "name" in each_structure else None),
                            "Type Name": type_data[str(each_structure["type_id"])],
                            "Owner Name": self.name,
                            "System Name": geographic_data[str(each_structure["system_id"])]["name"],
                            "Region Name": geographic_data[str(each_structure["system_id"])]["region"],
                            "State": each_structure["state"],
                            "Fuel Expires": (each_structure["fuel_expires"] if "fuel_expires" in each_structure else None),
                            "RF Timer": (each_structure["state_timer_end"] if "state_timer_end" in each_structure else None),
                            "Reinforce Hour": (each_structure["reinforce_hour"] if "reinforce_hour" in each_structure else None),
                            "Unanchor Timer": (each_structure["unanchors_at"] if "unanchors_at" in each_structure else None)
                        }
                
            else:
                
                print("STRUCTURES ERROR")
                break
            
            current_page += 1

class App:
    
    def __init__(self, target_alliances, target_corporations, core_info, include_ids):
        
        self.target_corporations = target_corporations
        self.target_alliances = target_alliances
        self.corporations = []
        self.corporation_data = {}
        
        self.auth_handler = ESI.NeucoreAuth(core_info["AppID"], core_info["AppSecret"], core_info["AppURL"])
        self.core_info = core_info
        self.esi_handler = ESI.Handler()
        
        self.ids_to_parse = {}
        self.structures = {}
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
                print("CORPORATIONS ERROR")
                
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
            
            print("NAMES ERROR")
            
    def process_corporations(self, include_ids):
        
        for each_corporation in self.corporation_data:
            
            if self.corporation_data[each_corporation] is not None:
                
                print("Checking " + str(each_corporation) + "...")
                self.corporation_data[each_corporation].name = self.ids_to_parse[each_corporation]
                self.corporation_data[each_corporation].get_structures(self.auth_handler, self.core_info["LoginName"], self.geographic_data, self.type_ids, include_ids)
                
                self.structures = self.structures | self.corporation_data[each_corporation].structure_data
                
            else:
                
                self.unknowns[each_corporation] = self.ids_to_parse[each_corporation]
                
    def export_json(self, file_name):
        
        with open(file_name, "w") as json_file:
            json.dump(self.structures, json_file, indent=1)
        
    def export_csv(self, file_name):
        
        with open(file_name, "w", newline='') as csv_file:
            fields = list(self.structures.values())[0].keys()
            csv_writer = DictWriter(csv_file, fieldnames=fields)
            
            csv_writer.writeheader()
            for each_structure in self.structures.values():
                csv_writer.writerow(each_structure)
        
    def export_unknowns(self, file_name):
        
        with open(file_name, "w") as unknowns_file:
            json.dump(self.unknowns, unknowns_file, indent=1)
        
    def make_report(self, platform, webhook):
        
        pass
