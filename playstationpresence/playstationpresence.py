#!/usr/bin/env python3
import asyncio
import requests
import time
from psnawp_api import psnawp
from pypresence import Presence
from playstationpresence.lib.files import load_config, load_game_data
from playstationpresence.lib.notifiable import Notifiable
from playstationpresence.lib.rpc_retry import rpc_retry
from threading import Event

class PlaystationPresence:
    def __init__(self):
        self.notifier = None
        self.rpc = None
        self.exit_event = Event()
        self.old_info: dict = {}
        self.config: dict = load_config()
        self.supported_games: set[str] = load_game_data()
        self.psapi = psnawp.PSNAWP(self.config['npsso'])
        self.psnid = self.config['PSNID']
        self.initRpc()

    def initRpc(self):
        self.rpc = Presence(self.config['discordClientId'], pipe=0, loop=asyncio.new_event_loop())
        self.rpc.connect()

    def quit(self):
        self.exit_event.set()

        if self.notifier is not None:
            self.notifier.visible = False
            self.notifier.stop()
    
    def notify(self, message):
        print(message)

        if self.notifier is not None:
            self.notifier.title = message
            self.notifier.notify(message, "playstationpresence")

    @rpc_retry
    def clearStatus(self):
        self.rpc.clear()
        self.notify(f"Status changed to Offline")

    @rpc_retry
    def updateStatus(self, state: str, large_image: str, large_text: str, tray_tooltip: str):
        start_time = int(time.time())
        self.rpc.update(state=state, start=start_time, small_image="ps5_main", small_text=self.psnid, large_image=large_image, large_text=large_text)
        self.notify(f"Status changed to {tray_tooltip}")

    def mainloop(self, notifier: Notifiable):
        if notifier is not None:
            self.notifier = notifier
            self.notifier.visible = True

        while not self.exit_event.is_set():
            mainpresence: dict = None
            user_online_id = None

            try:
                user_online_id = self.psapi.user(online_id=self.psnid)
                mainpresence = user_online_id.get_presence()
            except requests.exceptions.ConnectionError as e:
                print("Error when trying to read presence")
                print(e)

            if user_online_id is not None and mainpresence is not None:
                platform_info: dict = mainpresence['primaryPlatformInfo']
                game_info: list[dict] = mainpresence.get('gameTitleInfoList', None)
                
                if platform_info['onlineStatus'] == "offline":
                    if self.old_info != None:
                        self.clearStatus()
                        self.old_info = None
                else:
                    if game_info == None:
                        if self.old_info.get('npTitleId', "") != None:
                            self.updateStatus("Not in game", "ps5_main", "Homescreen", "Not in game")
                            self.old_info = { 'npTitleId': None }
                    elif self.old_info.get('npTitleId', "") != game_info[0]['npTitleId']:
                        game: dict[str, str] = game_info[0]
                        large_icon = game['npTitleId'].lower() if game['npTitleId'] in self.supported_games else "ps5_main"
                        self.updateStatus(game['titleName'], large_icon, game['titleName'], f"Playing {game['titleName']}")
                        self.old_info = game

            self.exit_event.wait(20) #Adjust this to be higher if you get ratelimited

        self.rpc.close()