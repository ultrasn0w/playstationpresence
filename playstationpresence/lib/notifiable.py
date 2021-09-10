from typing import Protocol

class Notifiable(Protocol):
    title: str
    visible: bool

    def stop(self) -> None:
        ...
    
    def notify(self, message: str, title: str = None) -> None:
        ...