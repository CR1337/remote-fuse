from machine import Pin, WDT, deepsleep, Timer
from backend.logger import logger


class Hardware:

    DIP_PIN_IDS: list[int] = [8, 9, 10, 11, 12, 13, 14, 15]
    REMOTE_DEVICE_INDEX_BIT_INDICES: list[int] = [0, 1, 2, 3, 4, 5]
    FUSE_AMOUNT_BIT_INDICES: list[int] = [6, 7]

    FUSE_PIN_IDS: list[int] = [18, 19, 20, 21]

    LED_PIN_IDS: list[int | str] = [0, 'LED']

    _dip_pins: list[Pin]
    _fuse_pins: list[Pin]
    _led_pins: list[Pin]

    _remote_device_index: int
    _fuse_amount: int

    def __init__(self):
        self._dip_pins = [Pin(id_, Pin.IN) for id_ in self.DIP_PIN_IDS]
        self._fuse_pins = [Pin(id_, Pin.OUT) for id_ in self.FUSE_PIN_IDS]
        self._led_pins = [Pin(id_, Pin.OUT) for id_ in self.LED_PIN_IDS]
        for pin in self._fuse_pins:
            pin.value(0)
        for pin in self._led_pins:
            pin.value(0)
        self._remote_device_index = self._read_dip_pins(
            self.REMOTE_DEVICE_INDEX_BIT_INDICES
        )
        self._fuse_amount = self._read_dip_pins(
            self.FUSE_AMOUNT_BIT_INDICES
        ) + 1

    def _read_dip_pins(self, indices: list[int]) -> int:
        value = 0
        for i, index in enumerate(indices):
            value += self._dip_pins[index].value() << i
        return value

    def leds_on(self):
        for pin in self._led_pins:
            pin.value(1)

    def leds_off(self):
        for pin in self._led_pins:
            pin.value(0)

    def fuse_on(self, index: int):
        logger.debug(f"Fuse {index} on", __file__)
        self._fuse_pins[index].value(1)

    def fuse_off(self, index: int):
        logger.debug(f"Fuse {index} off", __file__)
        self._fuse_pins[index].value(0)

    @property
    def fuses_locked(self) -> bool:
        logger.debug("Check Lock Status", __file__)
        return self._fuses_locked

    @property
    def remote_device_index(self) -> int:
        return self._remote_device_index

    @property
    def fuse_amount(self) -> int:
        return self._fuse_amount

    def _secure(self):
        from backend.led import led
        from backend.event_stream import EventStream
        led.off()
        self.leds_off()
        EventStream.close_all()
        for fuse_index in range(self.fuse_amount):
            self.fuse_off(fuse_index)

    def panic(self, message: str):
        logger.error(f"Panic: {message}", __file__)
        from backend.led import led
        self._secure()
        led.on()
        raise RuntimeError(f"panic: {message}")

    def _shutdown(self):
        logger.info("Shutdown", __file__)
        self._secure()
        deepsleep()

    def shutdown(self):
        Timer().init(
            period=3000,
            mode=Timer.ONE_SHOT,
            callback=lambda _: self._shutdown()
        )

    def _reboot(self):
        logger.info("Reboot", __file__)
        self._secure()
        WDT(id=1, timeout=1000)
        while True:
            pass

    def reboot(self):
        Timer().init(
            period=3000,
            mode=Timer.ONE_SHOT,
            callback=lambda _: self._reboot()
        )

    def get_state(self) -> dict:
        return {
            "is_locked": False
        }


hardware = Hardware()
