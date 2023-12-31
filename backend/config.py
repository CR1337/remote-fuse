from backend.hardware import hardware
from backend.logger import logger


class Config:

    DIP_PIN_IDS: list[int] = [8, 9, 10, 11, 12, 13, 14, 15]
    ADDRESS_BIT_INDICES: list[int] = [0, 1, 2, 3, 4, 5]
    FUSE_AMOUNT_BIT_INDICES: list[int] = [6, 7]

    TIME_RESOLUTION: int = 100
    IGNITION_DURATION: int = 100
    EVENT_STREAM_PERIOD: int = 2000
    EVENT_STREAM_RETRY_PERIOD: int = 5000

    _device_id: str
    _fuse_amount: int
    _master_ip: str
    _master_port: int

    def __init__(self):
        self._device_id = f"remote{hardware.remote_device_index}"
        logger.info(f"Detected device id: {self._device_id}", __file__)
        self._fuse_amount = hardware.fuse_amount
        logger.info(f"Detected fuse amount: {self._fuse_amount}", __file__)
        self._master_ip = None
        self._master_port = None

    @property
    def device_id(self) -> str:
        return self._device_id

    @property
    def fuse_amount(self) -> int:
        return self._fuse_amount

    @property
    def time_resolution(self) -> int:
        return self.TIME_RESOLUTION

    @property
    def ignition_duration(self) -> float:
        return self.IGNITION_DURATION

    @property
    def event_stream_period(self) -> int:
        return self.EVENT_STREAM_PERIOD

    @property
    def event_stream_retry_period(self) -> int:
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

    def get_state(self) -> dict:
        return {
            "config": {
                "device_id": self.device_id,
                "chip_amount": 1,
                "fuse_amounts": [self.fuse_amount],
                "debug": False,
                "master_ip": self.master_ip,
                "master_port": self.master_port
            },
            "constants": {
                "time_resolution": self.time_resolution / 1000,
                "ignition_duration": self.ignition_duration,
                "event_stream_period": self.event_stream_period,
                "event_stream_retry_period": self.event_stream_retry_period
            }
        }


config = Config()
