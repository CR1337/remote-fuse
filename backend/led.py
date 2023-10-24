from machine import Pin, Timer
from backend.hardware import hardware
from backend.logger import logger


class Led:

    STATIC_PERIODS: list[int] = [100, 100]
    SHORT_BLINK_PERIODS: list[int] = [100, 900]
    LONG_BLINK_PERIODS: list[int] = [500, 500]

    _status_pin: Pin
    _onboard_pin: Pin
    _is_on: bool
    _mode: str
    _timer: Timer

    def __init__(self):
        self._turn_off()
        self._mode = 'blink_long'
        self._timer = Timer()
        self._schedule_timer(100)

    def __del__(self):
        self._timer.deinit()

    def _turn_on(self):
        hardware.leds_on()
        self._is_on = True

    def _turn_off(self):
        hardware.leds_off()
        self._is_on = False

    def _toggle(self):
        if self._is_on:
            self._turn_off()
        else:
            self._turn_on()

    def _schedule_timer(self, period: int):
        self._timer.init(
            mode=Timer.ONE_SHOT,
            period=period,
            callback=self._timer_callback
        )

    def _timer_callback(self, _: Timer):
        if self._mode == 'on':
            self._turn_on()
            periods = self.STATIC_PERIODS
        elif self._mode == 'off':
            self._turn_off()
            periods = self.STATIC_PERIODS
        elif self._mode == 'blink_short':
            self._toggle()
            periods = self.SHORT_BLINK_PERIODS
        elif self._mode == 'blink_long':
            self._toggle()
            periods = self.LONG_BLINK_PERIODS
        else:
            periods = self.STATIC_PERIODS
        self._schedule_timer(periods[0 if self._is_on else 1])

    def on(self):
        logger.info("LED on", __file__)
        self._mode = 'on'
        self._mode_change_flag = True

    def off(self):
        logger.info("LED off", __file__)
        self._mode = 'off'
        self._mode_change_flag = True

    def blink_short(self):
        logger.info("LED blink short", __file__)
        self._mode = 'blink_short'
        self._mode_change_flag = True

    def blink_long(self):
        logger.info("LED blink long", __file__)
        self._mode = 'blink_long'
        self._mode_change_flag = True


led = Led()
