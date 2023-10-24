from hardware import hardware
from backend.logger import logger


class Config:

    DIP_PIN_IDS: list[int] = [8, 9, 10, 11, 12, 13, 14, 15]
    ADDRESS_BIT_INDICES: list[int] = [0, 1, 2, 3, 4, 5]
    FUSE_AMOUNT_BIT_INDICES: list[int] = [6, 7]

    TIME_RESOLUTION: float = 0.1
    IGNITION_DURATION: float = 0.1
    EVENT_STREAM_PERIOD: float = 2.0
    EVENT_STREAM_RETRY_PERIOD: float = 5.0

    _device_id: str
    _fuse_amount: int
    _master_ip: str
    _master_port: int

    def __init__(self):
        self._device_id = f"remote{hardware.remote_device_index}"
        self._fuse_amount = hardware.fuse_amount
        self._master_ip = None
        self._master_port = None

    @property
    def device_id(self) -> str:
        return self._device_id

    @property
    def fuse_amount(self) -> int:
        return self._fuse_amount

    @property
    def time_reolution(self) -> float:
        return self.TIME_RESOLUTION

    @property
    def ignition_duration(self) -> float:
        return self.IGNITION_DURATION

    @property
    def event_stream_period(self) -> float:
        return self.EVENT_STREAM_PERIOD

    @property
    def event_stream_retry_period(self) -> float:
        return self.EVENT_STREAM_RETRY_PERIOD

    @property
    def master_ip(self) -> str:
        return self._master_ip

    @master_ip.setter
    def master_ip(self, value: str):
        logger.info(f"Set master ip to {value}")
        self._master_ip = value

    @property
    def master_port(self) -> int:
        return self._master_port

    @master_port.setter
    def master_port(self, value: int):
        logger.info(f"Set master port to {value}")
        self._master_port = value


config = Config()
