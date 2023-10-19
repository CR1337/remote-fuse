from backend import time_util as tu
from backend.address import Address
from backend.config import config
from backend.hardware import hardware
from backend.command import Command
from backend.led import led


class Program:

    _name: str
    _command_list: list[Command]

    @classmethod
    def from_json(cls, name: str, json_data: list) -> 'Program':
        ...

    @classmethod
    def testloop_program(cls) -> 'Program':
        ...

    def __init__(self, name: str):
        ...

    def add_command(self, command: Command):
        ...

    def run(self, callback: callable):
        ...

    def pause(self):
        ...

    def continue_(self):
        ...

    def stop(self):
        ...

    def join(self):
        ...

    @property
    def is_running(self) -> bool:
        ...

    @property
    def name(self) -> str:
        return self._name

    def get_state(self) -> dict:
        ...
