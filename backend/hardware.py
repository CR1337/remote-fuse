from machine import Pin, WDT, deepsleep


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
    _fuses_locked: bool

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
        self._fuses_locked = True

    def _read_dip_pins(self, indices: list[int]) -> int:
        value = 0
        for index in indices:
            value += self._dip_pins[index].value() << index
        return value

    def leds_on(self):
        for pin in self._led_pins:
            pin.value(1)

    def leds_off(self):
        for pin in self._led_pins:
            pin.value(0)

    def fuse_on(self, index: int):
        if not self._fuses_locked:
            self._fuse_pins[index].value(1)

    def fuse_off(self, index: int):
        self._fuse_pins[index].value(0)

    def lock_fuses(self):
        self._fuses_locked = True

    def unlock_fuses(self):
        self._fuses_locked = False

    @property
    def remote_device_index(self) -> int:
        return self._remote_device_index

    @property
    def fuse_amount(self) -> int:
        return self._fuse_amount

    def _secure(self):
        from backend.led import led
        led.off()
        self.leds_off()
        for fuse_index in range(self.fuse_amount):
            self.fuse_off(fuse_index)

    def panic(self, message: str):
        from backend.led import led
        self._secure()
        led.on()
        raise RuntimeError(f"panic: {message}")

    def shutdown(self):
        self._secure()
        deepsleep()

    def reboot(self):
        self._secure()
        WDT(id=1, timeout=1000)
        while True:
            pass


hardware = Hardware()
