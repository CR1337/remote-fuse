import time
import ntptime
# from backend.logger import logger
# from backend.hardware import harware


MACHINE_TIME_ORIGIN: int = 946684800  # 2000-01-01T00:00:00.000
TIMEZONE_OFFSET: int = 3600  # 1 hour
NTP_RETIRES: int = 4


def _current_seconds() -> int:
    return (
        time.mktime(time.localtime())
        + MACHINE_TIME_ORIGIN
        + TIMEZONE_OFFSET
    )


def set_ntp_time():
    for i in range(NTP_RETIRES + 1):
        try:
            # logger.info("setting time from ntp server", __file__)
            ntptime.settime()
            break
        except Exception as ex:
            # logger.exception(
            #     "could not set time from ntp server. "
            #     + f"retry {i + 1}/{NTP_RETIRES}",
            #     ex, __file__
            # )
            pass
    else:
        # logger.error("could not set time from ntp server", __file__)
        # panic("could not set time from ntp server")
        pass

def get_system_time() -> str:
    y, mo, d, h, mi, s, *_ = time.localtime(_current_seconds() - MACHINE_TIME_ORIGIN)
    return f"{y}-{mo:02d}-{d:02d}T{h:02d}:{mi:02d}:{s:02d}.{000}"


def timestamp_now() -> int:
    return _current_seconds() * 1000


def string_to_timestamp(string: str) -> float:
    date_part, time_part = string.split("T")
    year, month, day = date_part.split("-")
    hour, minute, second = time_part.split(":")
    second, millisecond = second.split(".")
    return time.mktime(
        (
            int(year),
            int(month),
            int(day),
            int(hour),
            int(minute),
            int(second),
            0,
            0,
            0,
        )
    ) * 1000 + int(millisecond)


def time_reached(timestamp: float) -> bool:
    return timestamp_now() >= timestamp


def sleep(seconds: float):
    time.sleep(seconds)
