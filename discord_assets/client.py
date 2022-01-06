# Adapted from https://github.com/Tustin/PlayStationDiscord-Games/blob/master/discord_assets.py
import requests


class AssetClient:
    _API_ENDPOINT = 'https://discordapp.com/api/v6'

    def __init__(self, discordClientId, discordToken):
        self.clientId = discordClientId
        self.token = discordToken

    def get_assets(self):
        r = requests.get(f'{self._API_ENDPOINT}/oauth2/applications/{self.clientId}/assets', headers={'Authorization': f'{self.token}'})
        r.raise_for_status()
        return r.json()

    def add_asset(self, name, image_data):
        data = {
            'name': name,
            'image': image_data,
            'type': 1
        }
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'{self.token}'
        }
        r = requests.post(f'{self._API_ENDPOINT}/oauth2/applications/{self.clientId}/assets', headers=headers, json=data)
        r.raise_for_status()
        return r.json()

    def delete_asset(self, id):
        r = requests.delete(f'{self._API_ENDPOINT}/oauth2/applications/{self.clientId}/assets/{id}', headers={'Authorization': f'{self.token}'})
        r.raise_for_status()
