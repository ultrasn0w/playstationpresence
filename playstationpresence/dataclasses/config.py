from dataclasses import dataclass, field
from marshmallow_dataclass import Optional

@dataclass
class Config:
    discordClientId: str
    discordToken: str
    npsso: str
    psnid: str
    refresh_token: Optional[str]
    refresh_token_expiration: Optional[float]