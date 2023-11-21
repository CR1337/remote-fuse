from backend.config import config
from backend.address import Address
from backend.hardware import hardware
from machine import Timer
from backend import time_util as tu
from backend.logger import logger


class Command:

    _address: Address
    _timestamp: int
    _name: str
    _fired: bool
    _fireing: bool

    def __init__(self, address: Address, timestamp: int, name: str):
        self._address = address
        self._timestamp = timestamp
        self._name = name
        self._fired = False
        self._fireing = False

    def _timer_callback(self, timer: Timer):
        hardware.fuse_off(self._address.fuse_index)
        self._fireing = False
        self._fired = True
        timer.deinit()

    def light(self):
        logger.debug(f"Light {self}", __file__)
        hardware.fuse_on(self._address.fuse_index)
        self._fireing = True
        Timer().init(
            mode=Timer.ONE_SHOT,
            period=int(config.ignition_duration),
            callback=self._timer_callback,
        )

    def increase_timestamp(self, offset: int):
        self._timestamp += offset

    def get_state(self) -> dict:
        return {
            'address': str(self._address),
            'timestamp': self._timestamp / 1000,
            'name': self._name,
            'fired': self._fired,
            'fireing': self._fireing,
        }

    @property
    def address(self) -> Address:
        return self._address

    @property
    def timestamp(self) -> float:
        return self._timestamp

    def milliseconds_left(self, start_timestamp: int) -> int:
        return self._timestamp - (tu.timestamp_now() - start_timestamp)

    @property
    def name(self) -> str:
        return self._name

    @property
    def fired(self) -> bool:
        return self._fired

    @property
    def fireing(self) -> bool:
        return self._fireing

    def __str__(self):
        return f"{self._name}: {self.address} ({self._timestamp})"
