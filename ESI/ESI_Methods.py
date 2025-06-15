from ESI import ESI_Base

class Methods(ESI_Base.Base):

    esiURL = "https://esi.evetech.net/"
    
    def alliance_corporations(self, arguments):
            
        return self.makeRequest(
            endpoint = "/alliances/{alliance_id}/corporations/",
            url = (self.esiURL + "latest/alliances/" + str(arguments["alliance_id"]) + "/corporations/?datasource=tranquility"), 
            retries = (arguments["retries"] if "retries" in arguments else 0)
        )
        
    def corporation(self, arguments):
            
        return self.makeRequest(
            endpoint = "/corporations/{corporation_id}/",
            url = (self.esiURL + "latest/corporations/" + str(arguments["corporation_id"]) + "/?datasource=tranquility"), 
            retries = (arguments["retries"] if "retries" in arguments else 0)
        )
    
    def universe_names(self, arguments):
    
        return self.makeRequest(
            endpoint = "/universe/names/",
            url = (self.esiURL + "latest/universe/names/?datasource=tranquility"), 
            method = "POST", 
            payload = arguments["ids"], 
            retries = (arguments["retries"] if "retries" in arguments else 0)
        )
        
    def universe_moons(self, arguments):
            
        return self.makeRequest(
            endpoint = "/universe/moons/{moon_id}/",
            url = (self.esiURL + "latest/universe/moons/" + str(arguments["moon_id"]) + "/?datasource=tranquility"), 
            retries = (arguments["retries"] if "retries" in arguments else 0)
        )
        
    def corporation_structures(self, arguments):
        
        page = (arguments["page"] if "page" in arguments else 1)
    
        return self.makeRequest(
            endpoint = "/corporations/{corporation_id}/structures/",
            url = (self.esiURL + "latest/corporations/" + str(arguments["corporation_id"]) + "/structures/?datasource=tranquility&page=" + str(page)), 
            accessToken = self.accessToken, 
            retries = (arguments["retries"] if "retries" in arguments else 0)
        )
        
    def corporation_extractions(self, arguments):
        
        page = (arguments["page"] if "page" in arguments else 1)
    
        return self.makeRequest(
            endpoint = "/corporation/{corporation_id}/mining/extractions/",
            url = (self.esiURL + "latest/corporation/" + str(arguments["corporation_id"]) + "/mining/extractions/?datasource=tranquility&page=" + str(page)), 
            accessToken = self.accessToken, 
            retries = (arguments["retries"] if "retries" in arguments else 0)
        )
        
    def corporation_starbases(self, arguments):
        
        page = (arguments["page"] if "page" in arguments else 1)
    
        return self.makeRequest(
            endpoint = "/corporations/{corporation_id}/starbases/",
            url = (self.esiURL + "latest/corporations/" + str(arguments["corporation_id"]) + "/starbases/?datasource=tranquility&page=" + str(page)), 
            accessToken = self.accessToken, 
            retries = (arguments["retries"] if "retries" in arguments else 0)
        )