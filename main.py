from backend.network_ import Network
from backend.led import led
from backend.webserver import webserver
from backend import time_util as tu


def entrypoint():
    led.blink_long()
    Network.connect_wlan()
    tu.set_ntp_time()
    webserver.run()


entrypoint()
while True:
    pass
