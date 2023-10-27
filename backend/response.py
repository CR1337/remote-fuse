class Response:

    STATUS_CODES: dict[int, str] = {
        200: "OK",
        301: "Moved Permanently",
        400: "Bad Request",
        404: "Not Found",
        405: "Method Not Allowed",
        500: "Internal Server Error",
        501: "Not Implemented"
    }

    CONTENT_TYPE_HTML: str = "text/html"
    CONTENT_TYPE_JSON: str = "application/json"
    CONTENT_TYPE_PLAIN: str = "text/plain"
    CONTENT_TYPE_EVENT_STREAM: str = "text/event-stream"

    _status_code: int
    _headers: dict[str, str]
    _keep_alive: bool

    def __init__(
        self,
        status_code: int = 200,
        body: str = "{}",
        content_type: str = CONTENT_TYPE_JSON,
        keep_alive: bool = False
    ):
        self._status_code = status_code
        self._body = body
        self._headers = {
            "Access-Control-Allow-Origin": "*",
            "Content-Type": content_type,
            "Content-Length": str(len(body))
        }
        self._keep_alive = keep_alive

    def add_header(self, key: str, value: str):
        self._headers[key] = value

    @property
    def keep_alive(self) -> bool:
        return self._keep_alive

    @property
    def status_code(self) -> int:
        return self._status_code

    @property
    def status_line(self) -> str:
        return (
            f"HTTP/1.1 {self._status_code} "
            + f"{self.STATUS_CODES[self._status_code]}"
        )

    @property
    def content(self) -> str:
        return (
            self.status_line + "\n"
            + "\n".join(
                f"{key}: {value}"
                for key, value in self._headers.items()
            )
            + "\n\n"
            + self._body
        )
