import time
import ntptime


MACHINE_TIME_ORIGIN = 946684800  # 2000-01-01T00:00:00.000


def set_ntp_time():
    ntptime.settime()


def get_system_time() -> str:
    y, mo, d, h, mi, s, *_ = time.localtime()
    return f"{y}-{mo:02d}-{d:02d}T{h:02d}:{mi:02d}:{s:02d}.{000}"


def timestamp_now() -> float:
    return float(time.mktime(time.localtime()) + MACHINE_TIME_ORIGIN)


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
    ) + int(millisecond) / 1000


def time_reached(timestamp: float) -> bool:
    return timestamp_now() >= timestamp


def sleep(seconds: float):
    time.sleep(seconds)
