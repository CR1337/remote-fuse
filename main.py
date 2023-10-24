from backend.network_ import Network
from backend.led import led
from backend.webserver import webserver
from backend import time_util as tu
from backend.hardware import hardware
from backend.logger import logger


def entrypoint():
    logger.info("Running app...", __file__)
    led.blink_long()
    Network.connect_wlan()
    tu.set_ntp_time()
    webserver.run()


try:
    entrypoint()
except Exception as ex:
    logger.exception("Exception running app!", ex, __file__)
except (KeyboardInterrupt, SystemExit):
    logger.info(
        "Termination due to KeyboardInterrupt or SystemExit.", __file__
    )
finally:
    hardware.shutdown()
