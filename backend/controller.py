import time_util as tu
from backend.program import Program
from backend.address import Address
from backend.command import Command
from backend.config import config


class Controller:

    STATE_NOT_LOADED: str = 'not_loaded'
    STATE_LOADED: str = 'loaded'
    STATE_SCHEDULED: str = 'scheduled'
    STATE_RUNNING: str = 'running'
    STATE_PAUSED: str = 'paused'

    _program: Program
    _program_state: str

    def __init__(self):
        self._program = None

    def load_program(self, name: str, json_data: list):
        if self._program_state not in (self.STATE_NOT_LOADED,):
            raise RuntimeError()
        self._program = Program.from_json(name, json_data)

    def unload_program(self):
        if self._program_state not in (self.STATE_LOADED,):
            raise RuntimeError()
        self._program = None

    def schedule_program(self, time: str):
        if self._program_state not in (self.STATE_LOADED,):
            raise RuntimeError()
        ...

    def unschedule_program(self):
        if self._program_state not in (self.STATE_SCHEDULED,):
            raise RuntimeError()
        ...

    def run_program(self):
        if self._program_state not in (self.STATE_LOADED,):
            raise RuntimeError()
        self._program.run(self._program_finisher_callback)

    def pause_program(self):
        if self._program_state not in (self.STATE_RUNNING,):
            raise RuntimeError()
        self._program.pause()

    def continue_program(self):
        if self._program_state not in (self.STATE_PAUSED,):
            raise RuntimeError()
        self._program.continue_()

    def stop_program(self):
        if self._program_state not in (self.STATE_RUNNING, self.STATE_PAUSED):
            raise RuntimeError()
        self._program.stop()

    def run_testloop(self):
        if self._program_state not in (self.STATE_NOT_LOADED,):
            raise RuntimeError()
        self._program = Program.testloop_program()
        self._program.run(self._program_finisher_callback)

    def _program_finisher_callback(self):
        ...

    def fire(self, letter: str, number: int):
        if self._program_state not in (self.STATE_NOT_LOADED,):
            raise RuntimeError()
        address = Address(config.device_id, letter, number)
        command = Command(address, 0, f"manual_fire_command_{address}")
        command.light()

    def get_system_time(self) -> str:
        return tu.get_system_time()

    def get_state(self) -> dict:
        ...


controller = Controller()
