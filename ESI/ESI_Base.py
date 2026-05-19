import json
import requests
import time

class Base:

    defaultSuccessCodes = [200, 204]
    defaultCompatibilityDate = "2026-05-19"
        
    def makeRequest(
        self, 
        endpoint, 
        url, 
        method = "GET", 
        payload = None, 
        accessToken = None, 
        compatibilityDate = None,
        expectResponse = True, 
        successCodes = [], 
        retries = 0,
        retryDelay = 1
    ):
    
        responseData = {"Success": False, "Data": [], "Status Code": None, "Headers": None}
        
        for retryCounter in range(retries + 1):
        
            requestMethod = getattr(requests, method.lower())
            
            headers = {
                "accept": "application/json",
                "X-Compatibility-Date": (compatibilityDate if compatibilityDate is not None else self.defaultCompatibilityDate)
            }
            
            if accessToken is not None:
            
                headers["Authorization"] = "Bearer " + accessToken
                
            if payload is not None:
            
                requestData = json.dumps(payload)
                headers["Content-Type"] = "application/json"
                
            else:
            
                requestData = None
            
            request = requestMethod(
                url = url, 
                data = requestData, 
                headers = headers
            )

            responseData["Status Code"] = request.status_code
            responseData["Headers"] = dict(request.headers)
            
            if request.status_code in (self.defaultSuccessCodes + successCodes):
            
                responseData["Success"] = True
                
                if expectResponse:
                
                    try:
                        responseData["Data"] = json.loads(request.text)
                    except:
                        pass
                    
                return responseData
                
            elif retryCounter == retries:
            
                responseData["Success"] = False
                
                if expectResponse:
                
                    try:
                    
                        responseData["Data"] = json.loads(request.text)
                    
                    except:
                    
                        pass
                    
                return responseData
                
            else:
                
                time.sleep(retryDelay)
            