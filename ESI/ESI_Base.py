import json
import requests
import time

class Base:

    defaultSuccessCodes = [200, 204]
    defaultCompatibilityDate = "2026-05-19"

    def rate_limit_backoff(self, headers):

        if "X-Ratelimit-Limit" in headers:
            
            rate_limit_group = headers["X-Ratelimit-Group"]
            rate_limit_declaration = headers["X-Ratelimit-Limit"].split("/")
            rate_limit_count = int(rate_limit_declaration[0])

            rate_limit_duration_string = rate_limit_declaration[1]

            strip_hours = rate_limit_duration_string.rstrip("h")
            strip_minutes = rate_limit_duration_string.rstrip("m")
            if strip_hours != rate_limit_duration_string:
                rate_limit_duration = int(strip_hours) * 3600
            elif strip_minutes != rate_limit_duration_string:
                rate_limit_duration = int(strip_minutes) * 60
            else:
                print("Unknown rate limit duration: " + rate_limit_duration_string)
                return
            
            rate_limit_remaining = int(headers["X-Ratelimit-Remaining"])

            if rate_limit_remaining < (rate_limit_count * 0.10):

                wait_duration = int(rate_limit_duration / (rate_limit_remaining / 2))

                print(
                    "{used} of the {limit} rate limit for group {group} used. Waiting for {duration:,} seconds...".format(
                        used = (rate_limit_count - rate_limit_remaining),
                        limit = headers["X-Ratelimit-Limit"],
                        group = rate_limit_group,
                        duration = wait_duration
                    )
                )
                time.sleep(wait_duration)
        
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
                    
                self.rate_limit_backoff(responseData["Headers"])

                return responseData
                
            elif retryCounter == retries:
            
                responseData["Success"] = False
                
                if expectResponse:
                
                    try:
                    
                        responseData["Data"] = json.loads(request.text)
                    
                    except:
                    
                        pass
                    
                return responseData
            
            elif request.status_code == 429 and "Retry-After" in responseData["Headers"]:

                print("Rate Limit Exceeded! Waiting {duration} seconds...".format(duration = responseData["Headers"]["Retry-After"]))
                time.sleep(int(responseData["Headers"]["Retry-After"]))
                
            else:
                
                time.sleep(retryDelay)
            