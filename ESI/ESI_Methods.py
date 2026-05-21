from ESI import ESI_Base

class Methods(ESI_Base.Base):

    esiURL = "https://esi.evetech.net/"
    
    def alliance_corporations(self, arguments):
            
        return self.makeRequest(
            endpoint = "/alliances/{alliance_id}/corporations/",
            url = (self.esiURL + "alliances/" + str(arguments["alliance_id"]) + "/corporations/?datasource=tranquility"), 
            retries = (arguments["retries"] if "retries" in arguments else 0)
        )
        
    def corporation(self, arguments):
            
        return self.makeRequest(
            endpoint = "/corporations/{corporation_id}/",
            url = (self.esiURL + "corporations/" + str(arguments["corporation_id"]) + "/?datasource=tranquility"), 
            retries = (arguments["retries"] if "retries" in arguments else 0)
        )
    
    def universe_names(self, arguments):
    
        return self.makeRequest(
            endpoint = "/universe/names/",
            url = (self.esiURL + "universe/names/?datasource=tranquility"), 
            method = "POST", 
            payload = arguments["ids"], 
            retries = (arguments["retries"] if "retries" in arguments else 0)
        )
        
    def universe_moons(self, arguments):
            
        return self.makeRequest(
            endpoint = "/universe/moons/{moon_id}/",
            url = (self.esiURL + "universe/moons/" + str(arguments["moon_id"]) + "/?datasource=tranquility"), 
            retries = (arguments["retries"] if "retries" in arguments else 0)
        )
        
    def corporation_structures(self, arguments):
        
        page = (arguments["page"] if "page" in arguments else 1)
    
        return self.makeRequest(
            endpoint = "/corporations/{corporation_id}/structures/",
            url = (self.esiURL + "corporations/" + str(arguments["corporation_id"]) + "/structures/?datasource=tranquility&page=" + str(page)), 
            accessToken = self.accessToken, 
            retries = (arguments["retries"] if "retries" in arguments else 0)
        )
        
    def corporation_extractions(self, arguments):
        
        page = (arguments["page"] if "page" in arguments else 1)
    
        return self.makeRequest(
            endpoint = "/corporation/{corporation_id}/mining/extractions/",
            url = (self.esiURL + "corporation/" + str(arguments["corporation_id"]) + "/mining/extractions/?datasource=tranquility&page=" + str(page)), 
            accessToken = self.accessToken, 
            retries = (arguments["retries"] if "retries" in arguments else 0)
        )
        
    def corporation_starbases(self, arguments):
        
        page = (arguments["page"] if "page" in arguments else 1)
    
        return self.makeRequest(
            endpoint = "/corporations/{corporation_id}/starbases/",
            url = (self.esiURL + "corporations/" + str(arguments["corporation_id"]) + "/starbases/?datasource=tranquility&page=" + str(page)), 
            accessToken = self.accessToken, 
            retries = (arguments["retries"] if "retries" in arguments else 0)
        )
        
    def corporation_assets(self, arguments):
        
        page = (arguments["page"] if "page" in arguments else 1)
    
        return self.makeRequest(
            endpoint = "/corporations/{corporation_id}/assets/",
            url = (self.esiURL + "corporations/" + str(arguments["corporation_id"]) + "/assets/?datasource=tranquility&page=" + str(page)), 
            accessToken = self.accessToken, 
            retries = (arguments["retries"] if "retries" in arguments else 0),
            retryDelay = 5
        )

    def sov_hub_list(self, arguments):
            
        return self.makeRequest(
            endpoint = "/corporations/{corporation_id}/structures/sovereignty-hubs/",
            url = (self.esiURL + "corporations/" + str(arguments["corporation_id"]) + "/structures/sovereignty-hubs/?datasource=tranquility"), 
            accessToken = self.accessToken, 
            retries = (arguments["retries"] if "retries" in arguments else 0)
        )
    
    def sov_hubs(self, arguments):
            
        return self.makeRequest(
            endpoint = "/corporations/{corporation_id}/structures/sovereignty-hubs/{sovereignty_hub_id}/",
            url = (self.esiURL + "corporations/" + str(arguments["corporation_id"]) + "/structures/sovereignty-hubs/" + str(arguments["sovereignty_hub_id"]) + "/?datasource=tranquility"), 
            accessToken = self.accessToken, 
            retries = (arguments["retries"] if "retries" in arguments else 0)
        )
