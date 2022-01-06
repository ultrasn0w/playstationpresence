#!/usr/bin/env python3
import asyncio
import time
from psnawp_api import psnawp
from pypresence import Presence
from playstationpresence.lib.files import load_config, load_game_data
from playstationpresence.lib.notifiable import Notifiable
from playstationpresence.lib.rpc_retry import rpc_retry
from requests.exceptions import *
from threading import Event


class PlaystationPresence:
    def __init__(self):
        self.notifier = None
        self.rpc = None
        self.exit_event = Event()
        self.old_info: dict = {'onlineStatus': None, 'titleId': None}
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
    def updateStatus(self, show_time: bool, state: str, large_image: str, details: str):
        if show_time:
            start_time = int(time.time())
            self.rpc.update(state=state, start=start_time, small_image="ps5_main", small_text=self.psnid, large_image=large_image, large_text=state, details=details)
        else:
            self.rpc.update(state=state, small_image="ps5_main", small_text=self.psnid, large_image=large_image, large_text=state, details=details)

        self.notify(f"Status changed to {state}")

    def processPresenceInfo(self, mainpresence: dict):
        if mainpresence is None:
            return

        # Read PSN API data
        onlineStatus: str = mainpresence['primaryPlatformInfo']['onlineStatus']
        onlinePlatform: str = mainpresence['primaryPlatformInfo']['platform']
        game_info: list[dict] = mainpresence.get('gameTitleInfoList', None)

        # Check online status
        if onlineStatus == "offline":
            if self.old_info['onlineStatus'] != onlineStatus:
                self.clearStatus()
                self.old_info = {'onlineStatus': onlineStatus, 'titleId': None}
        elif game_info == None:
            # Set home menu state
            if self.old_info['onlineStatus'] != "online" or self.old_info['titleId'] != None:
                self.updateStatus(False, "Home Menu", "ps5_main", f"Online on {onlinePlatform}")
                self.old_info = {'onlineStatus': onlineStatus, 'titleId': None}
        elif self.old_info['titleId'] != game_info[0]['npTitleId']:
            # New title id is different -> update
            # Read game data
            game: dict[str, str] = game_info[0]
            # large_icon logic
            if game['npTitleId'] in self.supported_games:
                large_icon = game['npTitleId'].lower()
            else:
                large_icon = "ps5_main"
            # Update status
            self.updateStatus(
                True, game['titleName'], large_icon, f"Playing on {game['launchPlatform']}")
            self.old_info = {'onlineStatus': onlineStatus, 'titleId': game['npTitleId']}

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
                # Uncomment for debug info about currently running game
                # print(mainpresence)
            except (ConnectionError, HTTPError) as e:
                print("Error when trying to read presence")
                print(e)

            self.processPresenceInfo(mainpresence)
            # Adjust this to be higher if you get ratelimited
            self.exit_event.wait(20)

        self.clearStatus()
        self.rpc.close()
