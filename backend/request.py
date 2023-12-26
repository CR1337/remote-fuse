import socket
import json


class Request:

    _content: str
    _socket: socket.socket
    _client_address: str
    _client_port: int

    _method: str
    _url: str
    _headers: dict[str, str]
    _payload: str
    _location: str
    _get_parameters: dict[str, str]
    _valid: bool

    url_parameters: dict[str, str]

    def __init__(
        self, content: str, socket: socket.socket,
        client_address: str, client_port: int
    ):
        self._content = content
        self._socket = socket
        self._client_address = client_address
        self._client_port = client_port
        self.url_parameters = {}
        self._valid = True
        self._parse_content()

    def _parse_content(self):
        lines = [
            line.strip() for line in
            self._content.split("\n")
        ]
        try:
            self._method, self._url, *_ = lines[0].split(" ")
        except ValueError:
            self._valid = False
            print("INVALID REQUEST: ", lines[0])
            return
        self._headers = {}
        for line in lines[1:]:
            if line == "":
                break
            colon_index = line.index(":")
            self._headers[line[0:colon_index].lower()] = (
                line[colon_index + 2:]
            )
        self._payload = "\n".join(lines[len(self._headers) + 2:])
        if "?" in self._url:
            self._location, parameter_string = self._url.split("?")
            self._get_parameters = {
                pair.split("=")[0]: pair.split("=")[1]
                for pair in parameter_string.split("&")
            }
        else:
            self._location = self._url
            self._get_parameters = {}

    @property
    def valid(self) -> bool:
        return self._valid

    @property
    def socket(self) -> socket.socket:
        return self._socket

    @property
    def method(self) -> str:
        return self._method.upper()

    @property
    def client_address(self) -> str:
        return self._client_address

    @property
    def client_port(self) -> str:
        return self._client_port

    @property
    def url(self) -> str:
        return self._url

    @property
    def headers(self) -> dict[str, str]:
        return self._headers

    @property
    def payload(self) -> str:
        return self._payload

    @property
    def location(self) -> str:
        return self._location

    @property
    def get_parameters(self) -> dict[str, str]:
        return self._get_parameters

    @property
    def json_payload(self) -> dict:
        try:
            return json.loads(self._payload)
        except json.JSONDecodeError:
            return {}

    @property
    def content(self) -> str:
        return self._content
