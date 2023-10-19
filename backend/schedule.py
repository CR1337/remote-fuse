from backend import time_util as tu
from backend.config import config
from machine import Timer


class Schedule:

    _scheduled_time: str
    _callback: callable
    _timestamp: float
    _cancel_flag: bool
    _done: bool
    _faulty: bool
    _timer: Timer

    def __init__(self, time: str, callback: callable):
        self._scheduled_time = time
        self._timestamp = tu.string_to_timestamp(time)
        self._callback = callback
        self._cancel_flag = False
        self._done = False
        self._faulty = False
        self._timer = Timer()

    def start(self):
        self._timer.init(
            mode=Timer.PERIODIC,
            period=config.time_reolution * 1000,
            callback=self._timer_callback
        )

    def cancel(self):
        self._cancel_flag = True
        self.join()

    def join(self):
        while not self._done:
            pass

    def _timer_callback(self, timer: Timer):
        if not self._cancel_flag:
            if tu.time_reached(self._timestamp):
                try:
                    self._callback()
                except Exception:
                    self._faulty = True
                self._cancel_flag = True
        else:
            timer.deinit()
            self._done = True

    @property
    def timestamp(self) -> float:
        return self._timestamp

    @property
    def seconds_left(self) -> float:
        return self._timestamp - tu.timestamp_now()

    def get_state(self) -> dict:
        return {
            'timestamp': self._timestamp,
            'seconds_left': self.seconds_left,
            'faulty': self._faulty,
            'scheduled_time': self._scheduled_time
        }
