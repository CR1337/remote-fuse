import network
import json
from backend import time_util as tu
from backend.hardware import hardware


class Network:

    CONNECTION_WAIT_TIME: float = 2.0  # seconds
    STAT_CONNECTED: int = 2

    _wlan: network.WLAN
    _ip: str = ""

    @classmethod
    def connect_wlan(cls):
        cls._wlan = network.WLAN(network.STA_IF)
        cls._wlan.active(True)
        with open('wlan.json') as file:
            credentials = json.load(file)
        cls._wlan.connect(
            ssid=credentials['ssid'],
            key=credentials['password']
        )

        while cls._wlan.status() == network.STAT_CONNECTING:
            print("waiting for connection...")
            tu.sleep(cls.CONNECTION_WAIT_TIME)

        if cls._wlan.isconnected() or cls._wlan.status() == cls.STAT_CONNECTED:
            print("connected to wlan")
            cls._ip = cls._wlan.ifconfig()[0]
            return

        if cls._wlan.status() == network.STAT_WRONG_PASSWORD:
            hardware.panic("wrong wlan password")
        elif cls._wlan.status() == network.STAT_NO_AP_FOUND:
            hardware.panic("no wlan access point found")
        elif cls._wlan.status() == network.STAT_CONNECT_FAIL:
            hardware.panic("wlan connection failed")
        elif cls._wlan.status() == network.STAT_IDLE:
            hardware.panic("wlan connection idle")
        else:
            hardware.panic(f"unknown wlan error: {cls._wlan.status()}")

    @classmethod
    def disconnect_wlan(cls):
        cls._wlan.disconnect()
        cls._wlan.active(False)

    @classmethod
    def ip(cls) -> str:
        return cls._ip
