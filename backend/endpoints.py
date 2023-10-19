import json

from backend.hardware import hardware
from backend.config import config
from backend.event_stream import EventStream
from backend.request import Request
from backend.response import Response
from backend.controller import controller
from backend.logger import logger
from backend.rl_exception import RlException


class Router:

    _endpoints: dict

    def __init__(self):
        self._endpoints = {}

    def route(self, location: str, methods: list[str]):
        def decorator(func):
            self._endpoints[location] = (func, methods)

            def wrapper(request: Request) -> Response:
                return func(request)

            return wrapper
        return decorator

    def _build_exception_response(
        self, exception: Exception, clients_fault: bool
    ) -> Response:
        content = json.dumps({
            'exception_type': str(type(exception)),
            'exception_args': vars(exception),
            'traceback': logger.get_traceback(exception)
        })
        return Response(
            status_code=400 if clients_fault else 500,
            body=content
        )

    def handle_request(self, request: Request) -> Response:
        func, methods = self._endpoints.get(request.location, (None, [None]))
        if func is None:
            func, methods = self._endpoints.get(
                request.location.split("/")[0], (None, [None])
            )
            if func is not None:
                if (
                    "<" not in request.location
                    or ">" not in request.location
                ):
                    return Response(status_code=404)
        if func is None:
            return Response(status_code=404)
        if request.method not in methods:
            return Response(status_code=405)
        try:
            return func(request)
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
    filename = request.path_parameter if request.path_parameter else ""
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
    ...


@router.route("/logs/<filename>", ['GET'])
def endpoint_logs_filename(request: Request) -> Response:
    ...


@router.route("/logs/structured/<filename>", ['GET'])
def endpoint_logs_structured_filename(request: Request) -> Response:
    ...


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
        "is_remote": False
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
