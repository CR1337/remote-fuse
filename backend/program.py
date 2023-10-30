from backend import time_util as tu
from backend.address import Address
from backend.config import config
from backend.hardware import hardware
from backend.command import Command
from backend.rl_exception import RlException
from backend.logger import logger
import _thread


class Program:

    class InvalidProgram(RlException):
        pass

    _name: str
    _command_list: list[Command]

    _start_timestamp: int
    _callback: callable
    _command_idx: int

    _paused: bool
    _milliseconds_paused: int
    _last_current_timestamp_before_pause: int

    _pause_flag: bool
    _continue_flag: bool
    _stop_flag: bool

    _running: bool

    @classmethod
    def from_json(cls, name: str, json_data: list) -> 'Program':
        program = cls(name)
        for event in json_data:
            address = Address(
                event['device_id'],
                event['letter'],
                event['number']
            )
            if address.device_id != config.device_id:
                continue
            command = Command(
                address,
                event['timestamp'] * 1000,
                event['name']
            )
            program.add_command(command)
        return program

    @classmethod
    def testloop_program(cls) -> 'Program':
        testloop = cls("Testloop")
        for idx, address in enumerate(Address.all_addresses()):
            command = Command(address, idx / 4 * 1000, str(address))
            testloop.add_command(command)
        return testloop

    def __init__(self, name: str):
        self._name = name
        self._command_list = []

        self._start_timestamp = None
        self._callback = None
        self._command_idx = 0

        self._paused = False
        self._milliseconds_paused = 0
        self._last_current_timestamp_before_pause = None

        self._pause_flag = False
        self._continue_flag = False
        self._stop_flag = False

        self._running = False

    def add_command(self, command: Command):
        self._command_list.append(command)

    def run(self, callback: callable):
        self._command_list.sort(key=lambda c: c.timestamp)
        self._callback = callback
        _thread.start_new_thread(self._thread_handler, ())

    def pause(self):
        self._pause_flag = True

    def continue_(self):
        self._continue_flag = True

    def stop(self):
        self._stop_flag = True
        self.join()

    def join(self):
        while self._running:
            tu.sleep(config.time_resolution / 1000)

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def name(self) -> str:
        return self._name

    def get_state(self) -> dict:
        return {
            'name': self._name,
            'command_list': [
                cmd.get_state()
                for cmd in self._command_list
            ],
            'time_paused': self._milliseconds_paused / 1000,
            'start_timestamp': self._start_timestamp / 1000,
            'current_timestamp': self._current_timestamp / 1000,
            'is_running': self.is_running
        }

    @property
    def _current_timestamp(self) -> float:
        if self._paused:
            return self._last_current_timestamp_before_pause
        if self._start_timestamp is None:
            return None
        return tu.timestamp_now() - self._start_timestamp

    def _thread_handler(self):
        self._milliseconds_paused = 0.0
        self._command_idx = 0
        self._start_timestamp = tu.timestamp_now()
        self._running = True

        hardware_was_locked = hardware.fuses_locked
        if hardware_was_locked:
            hardware.unlock_fuses()
        try:
            self._program_mainloop()
        finally:
            if hardware_was_locked:
                tu.sleep(config.ignition_duration / 1000 * 2)
                hardware.lock_fuses()

        self._callback()
        self._running = False

    def _program_mainloop(self):
        while not self._stop_flag and self._command_list:

            if self._pause_flag:
                self._milliseconds_paused += self._pause_handler()
                for command in self._command_list:
                    command.increase_timestamp(self._milliseconds_paused)
                if self._stop_flag:
                    break

            tu.sleep(config.time_resolution / 1000)

            command = self._command_list[self._command_idx]

            print("MAINLOOP STEP")
            print("COMMAND:", command)
            print("COMMAND TIMESTAMP:", command.timestamp)
            print("CURRENT TIMESTAMP:", self._current_timestamp)
            print("TIMESTAMP NOW:", tu.timestamp_now())

            if command.timestamp <= self._current_timestamp:
                try:
                    logger.debug(f"Light {command}", __file__)
                    command.light()
                except Exception as ex:
                    logger.exception(
                        "Exception while fireing {command}", ex, __file__
                    )
                self._command_idx += 1
                if self._command_idx >= len(self._command_list):
                    break

    def _pause_handler(self) -> float:
        self._last_current_timestamp_before_pause = self._current_timestamp
        self._paused = True
        pause_started_timestamp = tu.timestamp_now()
        while not self._continue_flag:
            if self._stop_flag:
                pause_ended_timestamp = tu.timestamp_now()
                return pause_ended_timestamp - pause_started_timestamp
            tu.sleep(config.time_resolution / 1000)
        self._pause_flag = False
        self._continue_flag = False
        pause_ended_timestamp = tu.timestamp_now()
        self._paused = False
        return pause_ended_timestamp - pause_started_timestamp
