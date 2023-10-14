from hardware import hardware


class Config:

    DIP_PIN_IDS: list[int] = [8, 9, 10, 11, 12, 13, 14, 15]
    ADDRESS_BIT_INDICES: list[int] = [0, 1, 2, 3, 4, 5]
    FUSE_AMOUNT_BIT_INDICES: list[int] = [6, 7]

    TIME_RESOLUTION: float = 0.1
    IGNITION_DURATION: float = 0.1

    _device_id: str
    _fuse_amount: int

    def __init__(self):
        self._device_id = f"remote{hardware.remote_device_index}"
        self._fuse_amount = hardware.fuse_amount

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


config = Config()
