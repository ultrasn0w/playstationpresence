from dataclasses import dataclass, field
from typing import List

from playstationpresence.dataclasses.game import Game
from playstationpresence.dataclasses.platform_info import PlatformInfo

@dataclass
class UserPresence:
    primaryPlatformInfo: PlatformInfo
    gameTitleInfoList: List[Game] = field(default=None)