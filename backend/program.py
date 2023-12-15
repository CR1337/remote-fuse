from backend.command import Command
from backend.rl_exception import RlException
from backend.config import config
from backend.address import Address
import backend.time_util as tu
from machine import Timer
from backend.logger import logger


class Program:

    class InvalidProgram(RlException):
        pass

    _name: str
    _command_list: list[Command]

    _stop_flag: bool
    _pause_flag: bool
    _continue_flag: bool
    _paused: bool
    _running: bool

    _command_index: int | None

    _start_timestamp: int | None
    _pause_timestamp: int | None
    _milliseconds_paused: int | None
    _total_milliseconds_paused: int
    _last_current_timestamp_before_pause: int | None

    _callback: callable | None

    _timer: Timer

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
                int(float(event['timestamp']) * 1000),
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

        self._stop_flag = False
        self._pause_flag = False
        self._continue_flag = False
        self._paused = False
        self._running = False

        self._command_index = None

        self._start_timestamp = None
        self._pause_timestamp = None
        self._last_current_timestamp_before_pause = None
        self._milliseconds_paused = None
        self._total_milliseconds_paused = 0
        self._last_current_timestamp_before_pause = None

        self._callback = None

        self._timer = Timer()

    def add_command(self, command: Command):
        self._command_list.append(command)

    def run(self, callback: callable):
        self._start_timestamp = tu.timestamp_now()
        self._milliseconds_paused = 0
        self._command_index = 0
        self._running = True
        self._callback = callback

        self._timer.init(
            mode=Timer.ONE_SHOT,
            period=config.time_resolution,
            callback=self._timer_callback
        )

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

    def get_state(self) -> dict:
        return {
            'name': self._name,
            'command_list': [
                cmd.get_state()
                for cmd in self._command_list
            ],
            'time_paused': self._total_milliseconds_paused / 1000,
            'start_timestamp': (
                (self._start_timestamp / 1000)
                if self._start_timestamp
                else None
            ),
            'current_timestamp': (
                (self._current_timestamp() / 1000)
                if self._current_timestamp()
                else None
            ),
            'is_running': self._running
        }

    def _current_timestamp(self) -> int | None:
        if self._paused:
            return self._last_current_timestamp_before_pause
        if self._start_timestamp is None:
            return None
        return tu.timestamp_now() - self._start_timestamp

    @property
    def name(self) -> str:
        return self._name

    @property
    def running(self) -> bool:
        return self._running

    def _cleanup(self):
        self._timer.deinit()
        self._stop_flag = False
        self._callback()
        self._running = False

    def _timer_callback(self, _: Timer):
        if self._stop_flag or not self._command_list:
            self._cleanup()
        elif self._pause_flag:
            self._init_pause()
        elif self._paused:
            self._pause_handler()
        else:
            self._command_handler()
        if self._running:
            self._timer.init(
                mode=Timer.ONE_SHOT,
                period=config.time_resolution,
                callback=self._timer_callback
            )

    def _init_pause(self):
        self._pause_flag = False
        self._paused = True
        self._pause_timestamp = tu.timestamp_now()
        self._milliseconds_paused = 0
        self._last_current_timestamp_before_pause = (
            tu.timestamp_now() - self._start_timestamp
        )
        self._pause_handler()

    def _pause_handler(self):
        if self._continue_flag:
            self._continue_handler()

    def _continue_handler(self):
        self._continue_flag = False
        self._paused = False
        self._milliseconds_paused = tu.timestamp_now() - self._pause_timestamp
        self._total_milliseconds_paused += self._milliseconds_paused
        for command in self._command_list[self._command_index:]:
            command.increase_timestamp(self._milliseconds_paused)
        self._command_handler()

    def _command_handler(self):
        if self._command_index >= len(self._command_list):
            self._cleanup()
            return
        command = self._command_list[self._command_index]
        if command.milliseconds_left(self._start_timestamp) <= 0:
            try:
                logger.debug(f"Light {command}", __file__)
                command.light()
            except Exception as ex:
                logger.exception(
                    "Exception while fireing {command}", ex, __file__
                )
            self._command_index += 1
