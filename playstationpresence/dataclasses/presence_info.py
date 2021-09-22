from dataclasses import dataclass, field

@dataclass
class PresenceInfo:
    onlineStatus: str = field(default=None)
    titleId: str = field(default=None)

    def updateStatus(self, onlineStatus, titleId):
        self.onlineStatus = onlineStatus
        self.titleId = titleId