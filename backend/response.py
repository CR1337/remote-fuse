class Response:

    STATUS_CODES: dict[int, str] = {
        200: "OK",
        204: "No Content",
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

    _content_type: str
    _status_code: int
    _headers: dict[str, str]
    _keep_alive: bool

    @classmethod
    def preflight_response(cls):
        return cls(
            status_code=204,
            body="",
            content_type=None,
            keep_alive=True,
            is_preflight=True
        )

    def __init__(
        self,
        status_code: int = 200,
        body: str = "{}",
        content_type: str = CONTENT_TYPE_JSON,
        keep_alive: bool = False,
        is_preflight=False
    ):
        self._content_type = content_type
        self._status_code = status_code
        self._body = (
            body if content_type != self.CONTENT_TYPE_EVENT_STREAM else ""
        )
        if is_preflight:
            self._headers = {
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, GET, DELETE",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Max-Age": "86400"
            }
        elif content_type == self.CONTENT_TYPE_EVENT_STREAM:
            self._headers = {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, GET, DELETE",
                "Access-Control-Allow-Headers": "Content-Type",
                "Content-Type": content_type,
                "Cache-Control": "no-cache"
            }
        else:
            self._headers = {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, GET, DELETE",
                "Access-Control-Allow-Headers": "Content-Type",
                "Content-Type": content_type,
                "Content-Length": str(len(body))
            }
        self._keep_alive = keep_alive

    def add_header(self, key: str, value: str):
        self._headers[key] = value

    @property
    def content_type(self) -> str:
        return self._content_type

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
    def header_string(self) -> str:
        return "\n".join(
            f"{key}: {value}"
            for key, value in self._headers.items()
        )

    def iter_content(self, block_size: int):
        yield self.status_line + "\n" + self.header_string + "\n\n"
        if self._content_type != self.CONTENT_TYPE_EVENT_STREAM:
            for i in range(0, len(self._body), block_size):
                yield self._body[i:i + block_size]
