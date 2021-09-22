#!/usr/bin/env python3
import asyncio
import marshmallow_dataclass
import time
from psnawp_api import psnawp
from pypresence import Presence
from playstationpresence.dataclasses.game import Game
from playstationpresence.dataclasses.presence_info import PresenceInfo
from playstationpresence.dataclasses.user_presence import UserPresence
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
        self.old_info = PresenceInfo()
        self.config = load_config()
        self.supported_games: set[str] = load_game_data()
        self.psapi = psnawp.PSNAWP(self.config.npsso)
        self.initRpc()

    def initRpc(self):
        self.rpc = Presence(self.config.discordClientId, pipe=0, loop=asyncio.new_event_loop())
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
        self.rpc.update(state=state, start=start_time, small_image="ps5_main", small_text=self.config.psnid, large_image=large_image, large_text=large_text)
        self.notify(f"Status changed to {tray_tooltip}")

    def processPresenceInfo(self, mainpresence: UserPresence):
        if mainpresence is None:
            return

        onlineStatus = mainpresence.primaryPlatformInfo.onlinestatus
        game_info = mainpresence.gameTitleInfoList
        
        if onlineStatus == "offline":
            if self.old_info.onlineStatus != onlineStatus:
                self.clearStatus()
                self.old_info.updateStatus(onlineStatus, titleId=None)
        elif game_info == None:
            if self.old_info.onlineStatus != "online" or self.old_info.titleId != None:
                self.updateStatus("Not in game", "ps5_main", "Homescreen", "Not in game")
                self.old_info.updateStatus(onlineStatus, titleId=None)
        elif self.old_info.titleId != game_info[0].npTitleId:
            game: Game = game_info[0]
            large_icon = game.npTitleId.lower() if game.npTitleId in self.supported_games else "ps5_main"
            self.updateStatus(game.titleName, large_icon, game.titleName, f"Playing {game.titleName}")
            self.old_info.updateStatus(onlineStatus, game.npTitleId)

    def mainloop(self, notifier: Notifiable):
        if notifier is not None:
            self.notifier = notifier
            self.notifier.visible = True

        _presence_schema = marshmallow_dataclass.class_schema(UserPresence)()

        while not self.exit_event.is_set():
            mainpresence = None
            user_online_id = None

            try:
                user_online_id = self.psapi.user(online_id=self.config.psnid)
                mainpresence = _presence_schema.load(user_online_id.get_presence())
            except Exception as e:
                print("Error when trying to read presence")
                print(e)

            self.processPresenceInfo(mainpresence)
            self.exit_event.wait(20) #Adjust this to be higher if you get ratelimited

        self.clearStatus()
        self.rpc.close()