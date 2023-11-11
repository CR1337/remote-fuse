import socket

from backend.request import Request
from backend.endpoints import router
from backend.network_ import Network
from backend.hardware import hardware
from backend.led import led


class Webserver:

    PORT: int = 5000

    _connection: socket.socket
    _has_current_client: bool
    _current_client: socket.socket
    _shutdown: bool

    def __init__(self):
        self._has_current_client = False
        self._shutdown = False

    def run(self):
        self._open_connection()
        led.blink_short()
        while not self._shutdown:
            self._mainloop()  # TODO
            # try:
            #     self._mainloop()
            # except Exception as ex:
            #     if self._has_current_client:
            #         self._current_client.close()
            #     hardware.panic(str(ex))

    def _open_connection(self):
        host = socket.getaddrinfo('0.0.0.0', self.PORT)[0][-1]
        self._connection = socket.socket()
        self._connection.bind(host)
        self._connection.listen()
        print(f"Listening on {Network.ip()}:{self.PORT}")

    def _mainloop(self):
        self._current_client, (client_address, client_port) = (
            self._connection.accept()
        )
        raw_request = self._current_client.recv(1024).decode('ascii')
        content_length_idx = raw_request.find('Content-Length: ')
        if content_length_idx != -1:
            next_line_idx = raw_request.find('\r\n', content_length_idx)
            content_length = int(
                raw_request[content_length_idx + 16:next_line_idx].strip()
            )
            emptyline_idx = raw_request.find('\r\n\r\n')
            header_length = emptyline_idx + 4
            body_length = len(raw_request) - header_length
            print("START LOOP")
            while body_length < content_length:
                chunk = self._current_client.recv(1024).decode('ascii')
                raw_request += chunk
                body_length += len(chunk)
            print("END LOOP")
        request = Request(
            raw_request,
            self._current_client,
            client_address,
            client_port
        )
        response = router.handle_request(request)
        self._current_client.send(response.content)
        if not response.keep_alive:
            self._current_client.close()
        print(
            f"{client_address} > {request.method} "
            + f"{request.url} ({response.status_code})"
        )


webserver = Webserver()
