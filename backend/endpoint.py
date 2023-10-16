import json

from hardware import hardware
from config import config


class Endpoint:

    OK_200: int = 200
    BAD_REQUEST_400: int = 400
    NOT_FOUND_404: int = 404
    METHOD_NOT_ALLOWED_405: int = 405
    NOT_IMPLEMENTED_501: int = 501

    CONTENT_HTML: str = "text/html"
    CONTENT_TEXT: str = "text/plain"
    CONTENT_JSON: str = "application/json"

    LOCATION: str
    METHODS: list[str]

    def _request_handler(
        self, method: str, path_parameter: str | None,
        get_parameters: dict[str, str], json_content: dict
    ) -> tuple[str, str, int]:
        raise NotImplementedError()

    def _extract_location_and_get_parameters(
        self, url: str
    ) -> tuple[str, dict[str, str]]:
        if "?" in url:
            location, parameter_string = url.split("?")
            get_parameters = {
                pair.split("=")[0]: pair.split("=")[1]
                for pair in parameter_string.split("&")
            }
        else:
            location = url
            get_parameters = {}
        return location, get_parameters

    def _extract_path_parameter(self, location: str) -> str | None:
        if "" not in self.LOCATION:
            return None
        return location.split("/")[-1]

    def handle_request(
        self,
        method: str,
        url: str,
        content: str
    ) -> tuple[str, str, int]:
        if method not in self.METHODS:
            return "{}", self.CONTENT_JSON, self.METHOD_NOT_ALLOWED_405
        location, get_parameters = self._extract_location_and_get_parameters(
            url
        )
        if location.endswith("/"):
            location = location[:-1]
        path_parameter = self._extract_path_parameter(location)
        json_content = json.loads(content)
        return self._request_handler(
            method, path_parameter, get_parameters, json_content
        )


class EndpointIndex(Endpoint):

    LOCATION_PREFIX: str = "/"
    METHODS: list[str] = ['GET']

    def _request_handler(
        self, method: str, path_parameter: str | None,
        get_parameters: dict[str, str], json_content: dict
    ):
        with open("frontend/device.html", 'r') as file:
            content = file.read()
        content.format(device_id=config.device_id)
        return content, self.CONTENT_HTML, self.OK_200


class EndpointFavicon(Endpoint):

    LOCATION_PREFIX: str = "/favicon.ico"
    METHODS: list[str] = ['GET']

    def _request_handler(
        self, method: str, path_parameter: str | None,
        get_parameters: dict[str, str], json_content: dict
    ):
        return "{}", self.CONTENT_JSON, self.NOT_FOUND_404  # TODO


class EndpointStatic(Endpoint):

    LOCATION_PREFIX: str = "/static/<path>"
    METHODS: list[str] = ['GET']

    def _request_handler(
        self, method: str, path_parameter: str,
        get_parameters: dict[str, str], json_content: dict
    ):
        try:
            with open("frontend/" + path_parameter, 'r') as file:
                content = file.read()
        except FileNotFoundError:
            return "{}", self.CONTENT_JSON, self.NOT_FOUND_404
        else:
            return content, self.CONTENT_TEXT, self.OK_200


class EndpointProgram(Endpoint):

    LOCATION_PREFIX: str = "/program"
    METHODS: list[str] = ['POST', 'DELETE']

    def _request_handler(
        self, method: str, path_parameter: str | None,
        get_parameters: dict[str, str], json_content: dict
    ):
        ...  # TODO


class EndpointProgramControl(Endpoint):

    LOCATION_PREFIX: str = "/program/control"
    METHODS: list[str] = ['POST']

    def _request_handler(
        self, method: str, path_parameter: str | None,
        get_parameters: dict[str, str], json_content: dict
    ):
        ...  # TODO


class EndpointFire(Endpoint):

    LOCATION_PREFIX: str = "/fire"
    METHODS: list[str] = ['POST']

    def _request_handler(
        self, method: str, path_parameter: str | None,
        get_parameters: dict[str, str], json_content: dict
    ):
        ...  # TODO


class EndpointTestloop(Endpoint):

    LOCATION_PREFIX: str = "/testloop"
    METHODS: list[str] = ['POST']

    def _request_handler(
        self, method: str, path_parameter: str | None,
        get_parameters: dict[str, str], json_content: dict
    ):
        ...  # TODO


class EndpointLock(Endpoint):

    LOCATION_PREFIX: str = "/lock"
    METHODS: list[str] = ['POST']

    def _request_handler(
        self, method: str, path_parameter: str | None,
        get_parameters: dict[str, str], json_content: dict
    ):
        is_locked = json_content.get("is_locked", None)
        if is_locked is None:
            return "{}", self.CONTENT_JSON, self.BAD_REQUEST_400
        if is_locked:
            hardware.lock_fuses()
        else:
            hardware.unlock_fuses()
        return "{}", self.CONTENT_JSON, self.OK_200


class EndpointSystemTime(Endpoint):

    LOCATION_PREFIX: str = "/system-time"
    METHODS: list[str] = ['GET']

    def _request_handler(
        self, method: str, path_parameter: str | None,
        get_parameters: dict[str, str], json_content: dict
    ):
        ...  # TODO


class EndpointEventStream(Endpoint):

    LOCATION_PREFIX: str = "/event-stream"
    METHODS: list[str] = ['GET']

    def _request_handler(
        self, method: str, path_parameter: str | None,
        get_parameters: dict[str, str], json_content: dict
    ):
        return "{}", self.CONTENT_JSON, self.NOT_IMPLEMENTED_501


class EndpointState(Endpoint):

    LOCATION_PREFIX: str = "/state"
    METHODS: list[str] = ['GET']

    def _request_handler(
        self, method: str, path_parameter: str | None,
        get_parameters: dict[str, str], json_content: dict
    ):
        ...  # TODO


class EndpointLogs(Endpoint):

    LOCATION_PREFIX: str = "/logs"
    METHODS: list[str] = ['GET']

    def _request_handler(
        self, method: str, path_parameter: str | None,
        get_parameters: dict[str, str], json_content: dict
    ):
        ...  # TODO


class EndpointLogsFilename(Endpoint):

    LOCATION_PREFIX: str = "/logs/<filename>"
    METHODS: list[str] = ['GET']

    def _request_handler(
        self, method: str, path_parameter: str | None,
        get_parameters: dict[str, str], json_content: dict
    ):
        ...  # TODO


class EndpointLogsStructuredFilename(Endpoint):

    LOCATION_PREFIX: str = "/logs/structured/<filename>"
    METHODS: list[str] = ['GET']

    def _request_handler(
        self, method: str, path_parameter: str | None,
        get_parameters: dict[str, str], json_content: dict
    ):
        ...  # TODO


class EndpointConfig(Endpoint):

    LOCATION_PREFIX: str = "/config"
    METHODS: list[str] = ['GET', 'POST']

    def _request_handler(
        self, method: str, path_parameter: str | None,
        get_parameters: dict[str, str], json_content: dict
    ):
        if method == 'GET':
            return json.dumps({
                "device_id": config.device_id,
                "fuse_amount": config.fuse_amount,
                "time_resolution": config.time_resolution,
                "ignition_duration": config.ignition_duration
            }), self.CONTENT_JSON, self.OK_200
        elif method == 'POST':
            return "{}", self.CONTENT_JSON, self.NOT_IMPLEMENTED_501


class EndpointUpdate(Endpoint):

    LOCATION_PREFIX: str = "/update"
    METHODS: list[str] = ['POST']

    def _request_handler(
        self, method: str, path_parameter: str | None,
        get_parameters: dict[str, str], json_content: dict
    ):
        return "{}", self.CONTENT_JSON, self.NOT_IMPLEMENTED_501


class EndpointDiscover(Endpoint):

    LOCATION_PREFIX: str = "/discover"
    METHODS: list[str] = ['GET']

    def _request_handler(
        self, method: str, path_parameter: str | None,
        get_parameters: dict[str, str], json_content: dict
    ):
        return json.dumps({
            "device_id": config.device_id,
            "is_remote": True
        }), self.CONTENT_JSON, self.OK_200


class EndpointShutdown(Endpoint):

    LOCATION_PREFIX: str = "/shutdown"
    METHODS: list[str] = ['POST']

    def _request_handler(
        self, method: str, path_parameter: str | None,
        get_parameters: dict[str, str], json_content: dict
    ):
        hardware.shutdown()
        return "{}", self.CONTENT_JSON, self.OK_200


class EndpointReboot(Endpoint):

    LOCATION_PREFIX: str = "/reboot"
    METHODS: list[str] = ['POST']

    def _request_handler(
        self, method: str, path_parameter: str | None,
        get_parameters: dict[str, str], json_content: dict
    ):
        hardware.reboot()
        return "{}", self.CONTENT_JSON, self.OK_200


class Router:

    _endpoints: dict[str, Endpoint]

    def __init__(self):
        self._endpoints = {}

    def register_endpoint(self, endpoint: Endpoint):
        location_prefix = endpoint.LOCATION
        if "<" in location_prefix:
            location_prefix = location_prefix.split("<")[0]
        self._endpoints[endpoint.LOCATION] = endpoint

    def handle_request(
        self,
        method: str,
        url: str,
        content: str
    ) -> tuple[str, str, int]:
        location_prefix = url.split("?")[0] if "?" in url else url
        location_prefix = (
            location_prefix.split("<")[0] if "<" in location_prefix
            else location_prefix
        )
        if location_prefix in self._endpoints:
            return self._endpoints[location_prefix].handle_request(
                method, url, content
            )
        else:
            return "{}", Endpoint.CONTENT_JSON, Endpoint.NOT_FOUND_404


router = Router()

router.register_endpoint(EndpointIndex())
router.register_endpoint(EndpointFavicon())
router.register_endpoint(EndpointStatic())
router.register_endpoint(EndpointProgramControl())
router.register_endpoint(EndpointFire())
router.register_endpoint(EndpointTestloop())
router.register_endpoint(EndpointLock())
router.register_endpoint(EndpointSystemTime())
router.register_endpoint(EndpointEventStream())
router.register_endpoint(EndpointState())
router.register_endpoint(EndpointLogs())
router.register_endpoint(EndpointLogsFilename())
router.register_endpoint(EndpointLogsStructuredFilename())
router.register_endpoint(EndpointConfig())
router.register_endpoint(EndpointUpdate())
router.register_endpoint(EndpointDiscover())
router.register_endpoint(EndpointShutdown())
router.register_endpoint(EndpointReboot())
