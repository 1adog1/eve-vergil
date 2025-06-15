import time
import json
import requests

from datetime import datetime

class RelayTerminus:

    def __init__(self, message, platform, url):

        self.message = message
        self.platform = platform
        self.url = url

        if platform == "Slack":

            self.formatForSlack()

        elif platform == "Discord":

            self.formatForDiscord()

    def formatForSlack(self):

        self.formattedData = {
            "text": self.message
        }

    def formatForDiscord(self):

        self.formattedData = {
            "content": self.message
        }

    def send(self, retries):

        for tries in range(retries + 1):

            toPost = requests.post(self.url, data=json.dumps(self.formattedData), headers={"Content-Type":"application/json"})

            if toPost.status_code in [200, 204]:

                return True

            elif tries == retries:

                print("Failed to Send a Message to {platform}!".format(platform=self.platform))
                break

            elif toPost.status_code == 429:

                if "Retry-After" in toPost.headers:

                    retryTime = float(toPost.headers["Retry-After"]) if (float(toPost.headers["Retry-After"]) < 100) else (float(toPost.headers["Retry-After"]) / 1000)

                else:

                    retryTime = 10
                    print("We Were Rate Limited But Either Not Given a Retry-After Header or Given a Wait Time of >90 Seconds!")

                print("Rate Limited While Sending Message to {platform} - Trying Again in {timer:.2f} Seconds.".format(platform=self.platform, timer=retryTime))
                time.sleep(retryTime)

            else:

                print("Unknown Error Sending Message to {platform} - Trying Again in 5 Seconds.".format(platform=self.platform))
                time.sleep(5)

        return False
