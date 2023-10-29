import json

from backend.hardware import hardware
from backend.config import config
from backend.event_stream import EventStream
from backend.request import Request
from backend.response import Response
from backend.controller import controller
from backend.logger import logger
from backend.rl_exception import RlException


class Endpoint:

    _function: callable
    _methods: list[str]
    _url_parameter_names: dict[int, str]
    _location: str

    def __init__(
        self,
        function: callable,
        methods: list[str],
        url_parameter_names: dict[int, str],
        location: str
    ):
        self._function = function
        self._methods = methods
        self._url_parameter_names = url_parameter_names
        self._location = location

    @property
    def function(self) -> callable:
        return self._function

    @property
    def methods(self) -> list[str]:
        return self._methods

    @property
    def url_parameter_names(self) -> dict[int, str]:
        return self._url_parameter_names

    @property
    def location(self) -> str:
        return self._location

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        methods = str(self.methods).replace("'", "")
        url_parameter_names = str(self.url_parameter_names).replace("'", "")
        return (
            f"\"Endpoint(methods={methods}, "
            + f"url_parameter_names={url_parameter_names}, "
            + f"location={self.location})\""
        )


class Router:

    URL_PARAMETER_PREFIX: str = "<"
    URL_PARAMETER_SUFFIX: str = ">"
    URL_PAREMETER_KEY: str = r"{URL_PARAM}"
    ROOT_SYMBOL: str = r"{ROOT}"

    _endpoints: dict

    def __init__(self):
        self._endpoints = self._new_node()

    def _new_node(self) -> dict:
        return {
            'endpoint': None,
            'nodes': {}
        }

    def _split_location(self, location: str) -> list[str]:
        directories = [self.ROOT_SYMBOL] + location.split("/")[1:]
        if directories[-1] == "":
            directories = directories[:-1]
        return directories

    def _register_endpoint(
        self, location: str, methods: list[str], func: callable
    ):
        directories = self._split_location(location)

        last_index = len(directories) - 1
        node = self._endpoints
        url_parameter_names = {}

        for idx, directory in enumerate(directories):

            key = directory
            if (
                directory[0] == self.URL_PARAMETER_PREFIX
                and directory[-1] == self.URL_PARAMETER_SUFFIX
            ):
                url_parameter_name = directory[1:-1]
                if url_parameter_name in url_parameter_names:
                    hardware.panic(
                        "duplicate path parameter name: ",
                        + url_parameter_name
                    )
                url_parameter_names[idx] = url_parameter_name
                key = self.URL_PAREMETER_KEY

            if key not in node['nodes']:
                node['nodes'][key] = self._new_node()
            node = node['nodes'][key]

            if idx == last_index and node['endpoint'] is not None:
                hardware.panic(f"duplicate endpoint: {location}")

        node['endpoint'] = Endpoint(
            func, methods, url_parameter_names, location
        )

    def route(self, location: str, methods: list[str]):
        def decorator(func):
            self._register_endpoint(location, methods, func)

            def wrapper(request: Request) -> Response:
                return func(request)

            return wrapper
        return decorator

    def _build_exception_response(
        self, exception: Exception, clients_fault: bool
    ) -> Response:
        content = json.dumps({
            'exception_type': str(type(exception)),
            'exception_args': "NOT_IMPLEMEMTED",  # TODO
            'traceback': logger.get_traceback(exception)
        })
        return Response(
            status_code=400 if clients_fault else 500,
            body=content
        )

    def handle_request(self, request: Request) -> Response:
        directories = self._split_location(request.location)
        last_index = len(directories) - 1
        node = self._endpoints
        url_parameter_values = {}

        for idx, directory in enumerate(directories):

            key = directory
            if directory not in node['nodes']:
                url_parameter_values[idx] = directory
                key = self.URL_PAREMETER_KEY

            node = node['nodes'].get(key, None)
            if node is None:
                return Response(status_code=404)

            if idx == last_index and node['endpoint'] is None:
                return Response(status_code=404)

        endpoint = node['endpoint']

        if len(endpoint.url_parameter_names) != len(url_parameter_values):
            return Response(status_code=404)
        for value_idx, value in url_parameter_values.items():
            name = endpoint.url_parameter_names.get(value_idx, None)
            if name is None:
                return Response(status_code=404)
            request.url_parameters[name] = value

        if request.method not in endpoint.methods:
            return Response(status_code=405)

        try:
            return endpoint.function(request)
        except RlException as ex:
            return self._build_exception_response(ex, True)
        except Exception as ex:
            return self._build_exception_response(ex, False)


router = Router()


@router.route("/", ['GET'])
def endpoint_index(request: Request) -> Response:
    with open("frontend/device.html", 'r') as file:
        content = file.read()
    content = content.format(device_id=config.device_id)
    return Response(body=content, content_type=Response.CONTENT_TYPE_HTML)


@router.route("/favicon.ico", ['GET'])
def endpoint_favicon(request: Request) -> Response:
    if config.master_ip is None or config.master_port is None:
        return Response(status_code=404)
    response = Response(status_code=301)
    response.add_header(
        "Location",
        f"http://{config.master_ip}:{config.master_port}/favicon.ico"
    )
    return response


@router.route("/static/<path>", ['GET'])
def endpoint_static(request: Request) -> Response:
    # FIXME: doesnt work
    filename = request.url_parameters['path']
    try:
        with open("frontend/" + filename, 'r') as file:
            content = file.read()
    except FileNotFoundError:
        return Response(status_code=404)
    else:
        return Response(body=content, content_type=Response.CONTENT_TYPE_PLAIN)


@router.route("/program", ['POST', 'DELETE'])
def endpoint_program(request: Request) -> Response:
    if request.method == 'POST':
        json_data = request.json_payload
        controller.load_program(json_data['name'], json_data['event_list'])
    elif request.method == 'GET':
        controller.unload_program()

    return Response()


@router.route("/program/control", ['POST'])
def endpoint_program_control(request: Request) -> Response:
    action = request.json_payload['action']
    if action == 'run':
        controller.run_program()
    elif action == 'pause':
        controller.pause_program()
    elif action == 'continue':
        controller.continue_program()
    elif action == 'stop':
        controller.stop_program()
    elif action == 'schedule':
        time = request.json_payload['time']
        controller.schedule_program(time)
    elif action == 'unschedule':
        controller.unschedule_program()

    return Response()


@router.route("/fire", ['POST'])
def endpoint_fire(request: Request) -> Response:
    letter = request.json_payload['letter']
    number = request.json_payload['number']
    controller.fire(letter, number)
    return Response()


@router.route("/testloop", ['POST'])
def endpoint_testloop(request: Request) -> Response:
    controller.run_testloop()
    return Response()


@router.route("/lock", ['POST'])
def endpoint_lock(request: Request) -> Response:
    is_locked = request.json_payload.get("is_locked", None)
    if is_locked is None:
        return Response(status_code=400)
    if is_locked:
        hardware.lock_fuses()
    else:
        hardware.unlock_fuses()
    return Response()


@router.route("/system-time", ['GET'])
def endpoint_system_time(request: Request) -> Response:
    content = {'system-time': controller.get_system_time()}
    return Response(body=json.dumps(content))


@router.route("/event-stream", ['GET'])
def endpoint_event_stream(request: Request) -> Response:
    event_stream = EventStream(request.socket)
    event_stream.run()
    return Response(keep_alive=True)


@router.route("/state", ['GET'])
def endpoint_state(request: Request) -> Response:
    return Response(body=json.dumps(controller.get_state()))


@router.route("/logs", ['GET'])
def endpoint_logs(request: Request) -> Response:
    return Response(body=json.dumps(logger.get_log_files()))


@router.route("/logs/<filename>", ['GET'])
def endpoint_logs_filename(request: Request) -> Response:
    # FIXME: doesnt work
    filename = request.url_parameters['filename']
    if logger.logfile_exists(filename):
        return Response(
            body=logger.get_log_file_content(filename),
            content_type=Response.CONTENT_TYPE_PLAIN
        )
    else:
        return Response(status_code=404)


@router.route("/logs/structured/<filename>", ['GET'])
def endpoint_logs_structured_filename(request: Request) -> Response:
    # FIXME: doesnt work
    filename = request.url_parameters['filename']
    if logger.logfile_exists(filename):
        structured_log = logger.get_log_structured_content(filename)
        return Response(body=json.dumps(structured_log))
    else:
        return Response(status_code=404)


@router.route("/config", ['GET', 'POST'])
def endpoint_config(request: Request) -> Response:
    if request.method == 'GET':
        content = json.dumps({
            "device_id": config.device_id,
            "fuse_amount": config.fuse_amount,
            "time_resolution": config.time_resolution,
            "ignition_duration": config.ignition_duration
        })
        return Response(body=content)
    elif request.method == 'POST':
        return Response(status_code=501)


@router.route("/update", ['POST'])
def endpoint_update(request: Request) -> Response:
    return Response(status_code=501)


@router.route("/discover", ['GET'])
def endpoint_discover(request: Request) -> Response:
    config.master_ip = request.client_address
    config.master_port = request.client_port
    content = json.dumps({
        "device_id": config.device_id,
        "is_remote": True
    })
    return Response(body=content)


@router.route("/shutdown", ['POST'])
def endpoint_shutdown(request: Request) -> Response:
    hardware.shutdown()
    return Response()


@router.route("/reboot", ['POST'])
def endpoint_reboot(request: Request) -> Response:
    hardware.reboot()
    return Response()
