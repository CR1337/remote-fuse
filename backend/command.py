from backend.config import config
from backend.address import Address
from backend.hardware import hardware
from machine import Timer
from backend import time_util as tu
from backend.logger import logger


class Command:

    _address: Address
    _timestamp: float
    _name: str
    _fired: bool
    _fireing: bool

    def __init__(self, address: Address, timestamp: float, name: str):
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
            period=int(config.ignition_duration * 1000),
            callback=self._timer_callback,
        )

    def increae_timestamp(self, offset: float):
        self._timestamp += offset

    def get_state(self) -> dict:
        return {
            'address': str(self._address),
            'timestamp': self._timestamp,
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

    @property
    def seconds_left(self) -> float:
        return self._timestamp - tu.timestamp_now()

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
