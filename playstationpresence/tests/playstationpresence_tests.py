import unittest
from playstationpresence.playstationpresence import PlaystationPresence
from unittest.mock import patch

class PlaystationPresenceTests(unittest.TestCase):
    __mock_config = {
        "discordClientId": "mock-discord-id",
        "npsso": "mock-token",
        "PSNID": "mock-psnid"
    }

    __test_title = { 'npTitleId': "test-titleId", 'titleName': "test-titleName" }
    __test_title2 = { 'npTitleId': "test-titleId2", 'titleName': "test-titleName2" }

    @patch("playstationpresence.lib.files.load_config")
    @patch("playstationpresence.lib.files.load_game_data")
    @patch("playstationpresence.playstationpresence.PlaystationPresence.initRpc")
    @patch("psnawp_api.psnawp.PSNAWP")
    def get_presence_instance(self, mock_load_config, mock_load_game_data, mock_initRpc, mock_psnawp):
        mock_load_config.return_value = self.__mock_config

        return PlaystationPresence()

    def test_processPresenceInfo_nonePresence(self):
        presence = self.get_presence_instance()
        presence.processPresenceInfo(None)

        assert presence.old_info == { 'onlineStatus': None, 'titleId': None }

    @patch("playstationpresence.playstationpresence.PlaystationPresence.clearStatus")
    def test_processPresenceInfo_offlineAtStartup(self, mock_clearStatus):
        presence = self.get_presence_instance()
        presence.processPresenceInfo({'primaryPlatformInfo': {'onlineStatus': "offline"}})

        assert presence.old_info == { 'onlineStatus': "offline", 'titleId': None }
        mock_clearStatus.assert_called_once()

    @patch("playstationpresence.playstationpresence.PlaystationPresence.updateStatus")
    def test_processPresenceInfo_onlineAtStartup(self, mock_updateStatus):
        presence = self.get_presence_instance()
        presence.processPresenceInfo({'primaryPlatformInfo': {'onlineStatus': "online"}})

        assert presence.old_info == { 'onlineStatus': "online", 'titleId': None }
        mock_updateStatus.assert_called_once()
    
    @patch("playstationpresence.playstationpresence.PlaystationPresence.updateStatus")
    def test_processPresenceInfo_playingGameAtStartup(self, mock_updateStatus):
        presence = self.get_presence_instance()
        presence.processPresenceInfo({'primaryPlatformInfo': {'onlineStatus': "online"}, 'gameTitleInfoList': [ self.__test_title ]})

        assert presence.old_info == { 'onlineStatus': "online", 'titleId': "test-titleId" }
        mock_updateStatus.assert_called_once()

    @patch("playstationpresence.playstationpresence.PlaystationPresence.clearStatus")
    def test_processPresenceInfo_offlineThenOffline(self, mock_clearStatus):
        presence = self.get_presence_instance()
        presence.processPresenceInfo({'primaryPlatformInfo': {'onlineStatus': "offline"}})
        presence.processPresenceInfo({'primaryPlatformInfo': {'onlineStatus': "offline"}})

        assert presence.old_info == { 'onlineStatus': "offline", 'titleId': None }
        mock_clearStatus.assert_called_once()

    @patch("playstationpresence.playstationpresence.PlaystationPresence.clearStatus")
    @patch("playstationpresence.playstationpresence.PlaystationPresence.updateStatus")
    def test_processPresenceInfo_offlineThenOnline(self, mock_clearStatus, mock_updateStatus):
        presence = self.get_presence_instance()
        presence.processPresenceInfo({'primaryPlatformInfo': {'onlineStatus': "offline"}})
        presence.processPresenceInfo({'primaryPlatformInfo': {'onlineStatus': "online"}})

        assert presence.old_info == { 'onlineStatus': "online", 'titleId': None }
        mock_clearStatus.assert_called_once()
        mock_updateStatus.assert_called_once()
    
    @patch("playstationpresence.playstationpresence.PlaystationPresence.clearStatus")
    @patch("playstationpresence.playstationpresence.PlaystationPresence.updateStatus")
    def test_processPresenceInfo_offlineThenPlayingAGame(self, mock_clearStatus, mock_updateStatus):
        presence = self.get_presence_instance()
        presence.processPresenceInfo({'primaryPlatformInfo': {'onlineStatus': "offline"}})
        presence.processPresenceInfo({'primaryPlatformInfo': {'onlineStatus': "online"}, 'gameTitleInfoList': [ self.__test_title ]})

        assert presence.old_info == { 'onlineStatus': "online", 'titleId': "test-titleId" }
        mock_clearStatus.assert_called_once()
        mock_updateStatus.assert_called_once()

    @patch("playstationpresence.playstationpresence.PlaystationPresence.clearStatus")
    @patch("playstationpresence.playstationpresence.PlaystationPresence.updateStatus")
    def test_processPresenceInfo_onlineThenOffline(self, mock_clearStatus, mock_updateStatus):
        presence = self.get_presence_instance()
        presence.processPresenceInfo({'primaryPlatformInfo': {'onlineStatus': "online"}})
        presence.processPresenceInfo({'primaryPlatformInfo': {'onlineStatus': "offline"}})

        assert presence.old_info == { 'onlineStatus': "offline", 'titleId': None }
        mock_clearStatus.assert_called_once()
        mock_updateStatus.assert_called_once()

    @patch("playstationpresence.playstationpresence.PlaystationPresence.updateStatus")
    def test_processPresenceInfo_onlineThenOnline(self, mock_updateStatus):
        presence = self.get_presence_instance()
        presence.processPresenceInfo({'primaryPlatformInfo': {'onlineStatus': "online"}})
        presence.processPresenceInfo({'primaryPlatformInfo': {'onlineStatus': "online"}})

        assert presence.old_info == { 'onlineStatus': "online", 'titleId': None }
        mock_updateStatus.assert_called_once()
    
    @patch("playstationpresence.playstationpresence.PlaystationPresence.updateStatus")
    def test_processPresenceInfo_onlineThenPlayingAGame(self, mock_updateStatus):
        presence = self.get_presence_instance()
        presence.processPresenceInfo({'primaryPlatformInfo': {'onlineStatus': "online"}})
        presence.processPresenceInfo({'primaryPlatformInfo': {'onlineStatus': "online"}, 'gameTitleInfoList': [ self.__test_title ]})

        assert presence.old_info == { 'onlineStatus': "online", 'titleId': "test-titleId" }
        assert mock_updateStatus.call_count == 2
    
    @patch("playstationpresence.playstationpresence.PlaystationPresence.clearStatus")
    @patch("playstationpresence.playstationpresence.PlaystationPresence.updateStatus")
    def test_processPresenceInfo_playingAGameThenOffline(self, mock_clearStatus, mock_updateStatus):
        presence = self.get_presence_instance()
        presence.processPresenceInfo({'primaryPlatformInfo': {'onlineStatus': "online"}, 'gameTitleInfoList': [ self.__test_title ]})
        presence.processPresenceInfo({'primaryPlatformInfo': {'onlineStatus': "offline"}})

        assert presence.old_info == { 'onlineStatus': "offline", 'titleId': None }
        mock_clearStatus.assert_called_once()
        mock_updateStatus.assert_called_once()

    @patch("playstationpresence.playstationpresence.PlaystationPresence.updateStatus")
    def test_processPresenceInfo_playingAGameThenOnline(self, mock_updateStatus):
        presence = self.get_presence_instance()
        presence.processPresenceInfo({'primaryPlatformInfo': {'onlineStatus': "online"}, 'gameTitleInfoList': [ self.__test_title ]})
        presence.processPresenceInfo({'primaryPlatformInfo': {'onlineStatus': "online"}})

        assert presence.old_info == { 'onlineStatus': "online", 'titleId': None }
        assert mock_updateStatus.call_count == 2

    @patch("playstationpresence.playstationpresence.PlaystationPresence.updateStatus")
    def test_processPresenceInfo_playingAGameThenPlayingTheSameGame(self, mock_updateStatus):
        presence = self.get_presence_instance()
        presence.processPresenceInfo({'primaryPlatformInfo': {'onlineStatus': "online"}, 'gameTitleInfoList': [ self.__test_title ]})
        presence.processPresenceInfo({'primaryPlatformInfo': {'onlineStatus': "online"}, 'gameTitleInfoList': [ self.__test_title ]})

        assert presence.old_info == { 'onlineStatus': "online", 'titleId': "test-titleId" }
        mock_updateStatus.assert_called_once()
    
    @patch("playstationpresence.playstationpresence.PlaystationPresence.updateStatus")
    def test_processPresenceInfo_playingAGameThenPlayingAnotherGame(self, mock_updateStatus):
        presence = self.get_presence_instance()
        presence.processPresenceInfo({'primaryPlatformInfo': {'onlineStatus': "online"}, 'gameTitleInfoList': [ self.__test_title ]})
        presence.processPresenceInfo({'primaryPlatformInfo': {'onlineStatus': "online"}, 'gameTitleInfoList': [ self.__test_title2 ]})

        assert presence.old_info == { 'onlineStatus': "online", 'titleId': "test-titleId2" }
        assert mock_updateStatus.call_count == 2

if __name__ == '__main__':
    unittest.main()