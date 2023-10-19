import socket
from machine import Timer
import json
from config import config


event_streams: list['EventStream'] = []


class EventStream:

    _socket: socket.socket
    _counter: int
    _closed: bool

    @classmethod
    def close_all(cls):
        for event_stream in event_streams[:]:
            event_stream.close()

    def __init__(self, socket: socket.socket):
        self._socket = socket
        self._counter = 0
        self._closed = False

    def run(self):
        event_streams.append(self)
        self._set_timer()

    def close(self):
        self._closed = True
        event_streams.remove(self)
        self._socket.close()

    def _set_timer(self):
        Timer().init(
            mode=Timer.ONE_SHOT,
            period=int(config.event_stream_period * 1000),
            callback=self._timer_callback
        )

    def _timer_callback(self, timer: Timer):
        try:
            self._socket.send(self._event_content())
            self._counter += 1
        except OSError:
            self.close()
        else:
            if not self._closed:
                self._set_timer()

    def _event_content(self) -> str:
        data = {}  # TODO
        content = f"retry: {config.event_stream_retry_period * 1000}\n"
        content += f"id: {self._counter}\n"
        content += f"data: {json.dumps(data)}\n\n"
        return content