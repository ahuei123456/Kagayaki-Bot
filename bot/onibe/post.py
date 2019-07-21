from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class Message:
    text: str
    link: str
    media: list


class Postable(ABC):
    @abstractmethod
    def post(self, message: Message):
        ...
