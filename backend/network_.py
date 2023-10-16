import network
import json
from backend import time_util as tu
from backend.hardware import hardware


class Network:

    CONNECTION_WAIT_TIME: float = 2.0  # seconds

    _wlan: network.WLAN = network.WLAN(network.STA_IF)

    @classmethod
    def connect_wlan(cls):
        cls._wlan.active(True)
        with open('wlan.txt') as file:
            credentials = json.load(file)
        cls._wlan.connect(credentials['ssid'], credentials['password'])

        while cls._wlan.status() == network.STAT_CONNECTING:
            print("waiting for connection...")
            tu.sleep(cls.CONNECTION_WAIT_TIME)

        if cls._wlan.status() == network.STAT_GOT_IP:
            print("connected to wlan")
            return

        if cls._wlan.status() == network.STAT_WRONG_PASSWORD:
            hardware.panic("wrong wlan password")
        elif cls._wlan.status() == network.STAT_NO_AP_FOUND:
            hardware.panic("no wlan access point found")
        elif cls._wlan.status() == network.STAT_CONNECT_FAIL:
            hardware.panic("wlan connection failed")
        else:
            hardware.panic("unknown wlan error")

    @classmethod
    def disconnect_wlan(cls):
        cls._wlan.disconnect()
        cls._wlan.active(False)
