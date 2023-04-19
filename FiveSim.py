import requests
import os
from dotenv import load_dotenv

load_dotenv()

class FiveSim:
    def __init__(self):
        self.bearer = os.getenv('FIVESIM_BEARER_TOKEN')
        self.country = os.getenv('FIVESIM_COUNTRY')
        self.server = os.getenv('FIVESIM_OPERATOR')
        self.product = 'telegram'
        
    def request(self, url, body):
        try:
            headers = {
                'Authorization': f"Bearer {self.bearer}",
                'Accept': 'application/json',
            }

            response = requests.get(url, headers=headers)
            return response.text
        except Exception as e:
            print(e)
            
    def getProfileUser(self):
        try:
            response = self.request('https://5sim.net/v1/user/profile', {})
            return response
        except Exception as e:
            print(e)
            
    def buyActivationNumber(self):
        try:
            response = self.request(f'https://5sim.net/v1/user/buy/activation/{self.country}/{self.server}/{self.product}', {})
            return response
        except Exception as e:
            print(e)
            
    def checkOrder(self, id):
        try:
            response = self.request(f'https://5sim.net/v1/user/check/{id}', {})
            return response
        except Exception as e:
            print(e)
            
    def updateStatus(self, status, id):
        try:
            response = self.request(f'https://5sim.net/v1/user/{status}/{id}', {})
            return response
        except Exception as e:
            print(e)