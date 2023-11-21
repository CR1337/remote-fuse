from backend.network_ import Network
from backend.led import led
from backend.webserver import webserver
from backend import time_util as tu
from backend.hardware import hardware
from backend.logger import logger


def entrypoint():
    logger.info("Running app...", "main.py")
    led.blink_long()
    Network.connect_wlan()
    tu.set_ntp_time()
    webserver.run()


# entrypoint()


try:
    entrypoint()
except Exception as ex:
    logger.exception("Exception running app!", ex, "main.py")
except (KeyboardInterrupt, SystemExit):
    logger.info(
        "Termination due to KeyboardInterrupt or SystemExit.", "main.py"
    )
finally:
    # pass
    hardware.shutdown()
