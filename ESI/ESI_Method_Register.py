from ESI import ESI_Methods

class MethodRegister(ESI_Methods.Methods):

    def initalizeMethodList(self):
    
        self.methodList = {}
        
        self.register(
            endpoint = "/alliances/{alliance_id}/corporations/", 
            method = "alliance_corporations",
            requiredArguments = ["alliance_id"]
        )
        
        self.register(
            endpoint = "/universe/names/", 
            method = "universe_names",
            requiredArguments = ["ids"]
        )
        
        self.register(
            endpoint = "/corporations/{corporation_id}/structures/", 
            method = "corporation_structures",
            requiredArguments = ["corporation_id"]
        )
    
    def register(self, endpoint, method, requiredArguments):
    
        self.methodList[endpoint] = {"Name": method, "Required Arguments": requiredArguments}
    