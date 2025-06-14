import base64
import requests
import json
import time

class NeucoreAuth:
    
    def __init__(self, app_id, app_secret, app_url):
        
        self.access_token_storage = {}
        
        self.url = app_url
        raw_auth_header = str(app_id) + ":" + app_secret
        self.auth_header = "Bearer " + base64.urlsafe_b64encode(raw_auth_header.encode("utf-8")).decode()
        
    def getTokenCharacters(self, login_name):
        
        headers = {"Authorization" : self.auth_header, "accept": "application/json", "Content-Type": "application/json"}

        core_request = requests.get(
            self.url + "api/app/v1/esi/eve-login/" + str(login_name) + "/token-data", 
            headers=headers
        )
        
        if core_request.status_code == requests.codes.ok:
            
            response = json.loads(core_request.text)

            return response
            
        else:
            
            return None
            
        
    def getAccessToken(self, character_id, login_name):
        
        timeToCheck = int(time.time()) + 15
        
        if (
            login_name in self.access_token_storage 
            and int(character_id) in self.access_token_storage[login_name]
            and self.access_token_storage[login_name][int(character_id)]["expires"] > timeToCheck
        ):
            
            return self.access_token_storage[login_name][int(character_id)]["token"]
            
        else:
            
            headers = {"Authorization" : self.auth_header, "accept": "application/json", "Content-Type": "application/json"}

            core_request = requests.get(
                self.url + "api/app/v1/esi/access-token/" + str(character_id), 
                params={"eveLoginName": login_name}, 
                headers=headers
            )
            
            if core_request.status_code == requests.codes.ok:
                
                response = json.loads(core_request.text)
                
                if login_name not in self.access_token_storage:
                    
                    self.access_token_storage[login_name] = {}
                                        
                self.access_token_storage[login_name][int(character_id)] = response
                    
                return response["token"]
                
            else:
                
                return None
