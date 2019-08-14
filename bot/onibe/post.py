from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class Message:
    message_id: int
    channel_id: int
    text: str
    link: str
    media: str


class Postable(ABC):
    @abstractmethod
    def post(self, message: Message):
        ...

    @abstractmethod
    def newest(self):
        ...
