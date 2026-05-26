class UpwellStructure:

    reagent_consumption = {
        81826: {            # Metenox Moon Drill
            81143: 200      # 200 Magmatic Gas per Hour
        }
    }

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
        constellation_id, 
        constellation, 
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
        self.constellation_id = constellation_id
        self.constellation = constellation
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
        self.reagent_expiry = None
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
            "Constellation": self.constellation,
            "Region": self.region,
            "State": self.state,
            "Fitting": self.fitting,
            "Online Services": "\n".join(self.online_services),
            "Offline Services": "\n".join(self.offline_services),
            "Has Drill": self.has_drill,
            "Fuel": "\n".join(["{quantity:,} {type_name}s".format(quantity=x["Quantity"], type_name=x["Name"]) for x in self.fuel.values()]),
            "Ozone": self.ozone if self.type_id == 35841 else None,
            "Fuel Expires": self.fuel_expiry,
            "Reagents Expire": self.reagent_expiry,
            "Timer": self.timer,
            "Unanchor Timer": self.unanchor_timer,
            "Reinforcement Hour": self.reinforcement_hour
        }

class Starbase:

    fuel_consumption = {
        12235: {4247: 40},  # Amarr Control Tower                       40 Helium Fuel Blocks per Hour
        20059: {4247: 20},  # Amarr Control Tower Medium                20 Helium Fuel Blocks per Hour
        20060: {4247: 10},  # Amarr Control Tower Small                 10 Helium Fuel Blocks per Hour
        27530: {4247: 36},  # Blood Control Tower                       36 Helium Fuel Blocks per Hour
        27589: {4247: 18},  # Blood Control Tower Medium                18 Helium Fuel Blocks per Hour
        27592: {4247: 9},   # Blood Control Tower Small                 9 Helium Fuel Blocks per Hour
        27532: {4247: 32},  # Dark Blood Control Tower                  32 Helium Fuel Blocks per Hour
        27591: {4247: 16},  # Dark Blood Control Tower Medium           16 Helium Fuel Blocks per Hour
        27594: {4247: 8},   # Dark Blood Control Tower Small            8 Helium Fuel Blocks per Hour
        27780: {4247: 36},  # Sansha Control Tower                      36 Helium Fuel Blocks per Hour
        27782: {4247: 18},  # Sansha Control Tower Medium               18 Helium Fuel Blocks per Hour
        27784: {4247: 9},   # Sansha Control Tower Small                9 Helium Fuel Blocks per Hour
        27786: {4247: 32},  # True Sansha Control Tower                 32 Helium Fuel Blocks per Hour
        27788: {4247: 16},  # True Sansha Control Tower Medium          16 Helium Fuel Blocks per Hour
        27790: {4247: 8},   # True Sansha Control Tower Small           8 Helium Fuel Blocks per Hour

        16213: {4051: 40},  # Caldari Control Tower                     40 Nitrogen Fuel Blocks per Hour
        20061: {4051: 20},  # Caldari Control Tower Medium              20 Nitrogen Fuel Blocks per Hour
        20062: {4051: 10},  # Caldari Control Tower Small               10 Nitrogen Fuel Blocks per Hour
        27533: {4051: 36},  # Guristas Control Tower                    36 Nitrogen Fuel Blocks per Hour
        27595: {4051: 18},  # Guristas Control Tower Medium             18 Nitrogen Fuel Blocks per Hour
        27598: {4051: 9},   # Guristas Control Tower Small              9 Nitrogen Fuel Blocks per Hour
        27535: {4051: 32},  # Dread Guristas Control Tower              32 Nitrogen Fuel Blocks per Hour
        27597: {4051: 16},  # Dread Guristas Control Tower Medium       16 Nitrogen Fuel Blocks per Hour
        27600: {4051: 8},   # Dread Guristas Control Tower Small        8 Nitrogen Fuel Blocks per Hour

        12236: {4312: 40},  # Gallente Control Tower                    40 Oxygen Fuel Blocks per Hour
        20063: {4312: 20},  # Gallente Control Tower Medium             20 Oxygen Fuel Blocks per Hour
        20064: {4312: 10},  # Gallente Control Tower Small              10 Oxygen Fuel Blocks per Hour
        27536: {4312: 36},  # Serpentis Control Tower                   36 Oxygen Fuel Blocks per Hour
        27601: {4312: 18},  # Serpentis Control Tower Medium            18 Oxygen Fuel Blocks per Hour
        27604: {4312: 9},   # Serpentis Control Tower Small             9 Oxygen Fuel Blocks per Hour
        27538: {4312: 32},  # Shadow Control Tower                      32 Oxygen Fuel Blocks per Hour
        27603: {4312: 16},  # Shadow Control Tower Medium               16 Oxygen Fuel Blocks per Hour
        27606: {4312: 8},   # Shadow Control Tower Small                8 Oxygen Fuel Blocks per Hour

        16214: {4246: 40},  # Minmatar Control Tower                    40 Hydrogen Fuel Blocks per Hour
        20065: {4246: 20},  # Minmatar Control Tower Medium             20 Hydrogen Fuel Blocks per Hour
        20066: {4246: 10},  # Minmatar Control Tower Small              10 Hydrogen Fuel Blocks per Hour
        27539: {4246: 36},  # Angel Control Tower                       36 Hydrogen Fuel Blocks per Hour
        27607: {4246: 18},  # Angel Control Tower Medium                18 Hydrogen Fuel Blocks per Hour
        27610: {4246: 9},   # Angel Control Tower Small                 9 Hydrogen Fuel Blocks per Hour
        27540: {4246: 32},  # Domination Control Tower                  32 Hydrogen Fuel Blocks per Hour
        27609: {4246: 16},  # Domination Control Tower Medium           16 Hydrogen Fuel Blocks per Hour
        27612: {4246: 8},   # Domination Control Tower Small            8 Hydrogen Fuel Blocks per Hour
    }

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
        constellation_id, 
        constellation, 
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
        self.constellation_id = constellation_id
        self.constellation = constellation
        self.region_id = region_id
        self.region = region_name
        self.state = state
        self.fuel = {}
        self.fuel_expiry = None
        self.strontium = 0
        self.strontium_hours = 0
        self.timer = timer
        self.unanchor_timer = unanchor_timer

    def export(self):

        return {
            "Moon": self.moon,
            "Type": self.type,
            "Owner": self.owner_name,
            "Owner Ticker": self.owner_ticker,
            "System": self.system,
            "Constellation": self.constellation,
            "Region": self.region,
            "State": self.state,
            "Fuel": "\n".join(["{quantity:,} {type_name}s".format(quantity=x["Quantity"], type_name=x["Name"]) for x in self.fuel.values()]),
            "Fuel Expires": self.fuel_expiry,
            "Strontium": self.strontium,
            "Strontium Hours": self.strontium_hours,
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

class SovHub:

    def __init__(
        self, 
        id, 
        owner_id,
        owner_name,
        owner_ticker,
        system_id, 
        system, 
        constellation_id, 
        constellation, 
        region_id, 
        region, 
        fuel_acl_id, 
        reagent_bay,
        reagent_usage, 
        reagent_expirations, 
        resources, 
        workforce_configuration, 
        configured_import_sources,
        configured_export,
        workforce_state, 
        current_import_sources,
        current_export,
        upgrades
    ):
        
        self.id = id
        self.owner_id = owner_id
        self.owner_name = owner_name
        self.owner_ticker = owner_ticker

        self.system_id = system_id
        self.system = system
        self.constellation_id = constellation_id
        self.constellation = constellation
        self.region_id = region_id
        self.region = region
        self.fuel_acl_id = fuel_acl_id
        
        self.reagent_bay = reagent_bay
        self.reagent_usage = reagent_usage
        self.reagent_expirations = reagent_expirations
        self.next_expiring_reagent = min(self.reagent_expirations.values(), key=lambda x: x["Hours Remaining"]) if self.reagent_expirations else {"Name": None, "Hours Remaining": None, "Expires": None}

        self.allocated_power = resources["power"]["allocated"]
        self.available_power = resources["power"]["available"]
        self.allocated_workforce = resources["workforce"]["allocated"]
        self.available_workforce = resources["workforce"]["available"]

        self.workforce_configuration = workforce_configuration
        self.configured_import_sources = configured_import_sources
        self.configured_export = configured_export
        self.workforce_state = workforce_state
        self.current_import_sources = current_import_sources
        self.current_export = current_export

        self.online_upgrades = {
            x: y
            for x, y in upgrades.items()
            if y["State"] == "Online"
        }
        self.offline_upgrades = {
            x: y
            for x, y in upgrades.items()
            if y["State"] == "Offline"
        }
        self.low_power_upgrades = {
            x: y
            for x, y in upgrades.items()
            if y["State"] in ["Low", "Pending", "Unspecified"]
        }

    def export(self):

        if self.workforce_configuration == "import":
            configured_workforce = "\n".join(["{amount:,} FROM {system}".format(system=x["Name"], amount=x["Amount"]) for x in self.configured_import_sources.values()])
        elif self.workforce_configuration == "export":
            configured_workforce = "{amount:,} TO {system}".format(system=self.configured_export["Name"], amount=self.configured_export["Amount"])
        else:
            configured_workforce = None

        if self.workforce_state == "import":
            current_workforce = "\n".join(["{amount:,} FROM {system}".format(system=x["Name"], amount=x["Amount"]) for x in self.current_import_sources.values()])
        elif self.workforce_state == "export":
            current_workforce = "{amount:,} TO {system}".format(system=self.current_export["Name"], amount=self.current_export["Amount"])
        else:
            current_workforce = None

        return {
            "Owner": self.owner_name,
            "Owner Ticker": self.owner_ticker,
            "System": self.system,
            "Constellation": self.constellation,
            "Region": self.region,
            "Online Upgrades": "\n".join([x["Name"] for x in self.online_upgrades.values()]),
            "Offline Upgrades": "\n".join([x["Name"] for x in self.offline_upgrades.values()]),
            "Low Power Upgrades": "\n".join([x["Name"] for x in self.low_power_upgrades.values()]),
            "Reagents": "\n".join(["{quantity:,} {type_name}".format(quantity=x["Quantity"], type_name=x["Name"]) for x in self.reagent_bay.values()]),
            "Reagent Usage": "\n".join(["{usage:,} {type_name} per hour".format(usage=x["Usage"], type_name=x["Name"]) for x in self.reagent_usage.values()]),
            "Reagent Expirations": "\n".join(["{type_name}: {expiry}".format(expiry=x["Expires"], type_name=x["Name"]) for x in self.reagent_expirations.values()]),
            "Next Expiring": self.next_expiring_reagent["Name"],
            "Next Expires": self.next_expiring_reagent["Expires"],
            "Total Power": self.available_power,
            "Remaining Power": (self.available_power - self.allocated_power),
            "Total Workforce": self.available_workforce,
            "Remaining Workforce": (self.available_workforce - self.allocated_workforce),
            "Workforce Configuration": self.workforce_configuration,
            "Configured Flow": configured_workforce,
            "Workforce State": self.workforce_state,
            "Current Flow": current_workforce
        }
