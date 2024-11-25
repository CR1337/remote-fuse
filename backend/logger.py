import sys
from backend import time_util as tu


class Logger:

    TRACEBACK_FILENAME: str = "traceback.txt"
    START: str = ">>>"
    SEP: str = ":::"

    def get_traceback(self, exception: Exception) -> str:
        with open(self.TRACEBACK_FILENAME, 'w') as file:
            sys.print_exception(exception, file)
        with open(self.TRACEBACK_FILENAME, 'r') as file:
            return file.read()

    def _log(self, level: str, message: str, filename: str):
        time_string = tu.get_system_time().split(".")[0]
        time_string = time_string.replace("T", " ").replace(":", ".")
        if filename is None:
            filename = "NO_FILENAME"
        log_entry = (
            f"{self.START}{time_string}{self.SEP}{level}"
            + f"{self.SEP}main_thread"
            + f"{self.SEP}{filename}{self.SEP}NO_LINE{self.SEP}{message}"
        )
        print(log_entry)

    def debug(
        self,
        message: str,
        filename: str = None
    ):
        self._log('debug', message, filename)

    def info(
        self,
        message: str,
        filename: str = None
    ):
        self._log('info', message, filename)

    def warning(
        self,
        message: str,
        filename: str = None
    ):
        self._log('warning', message, filename)

    def error(
        self,
        message: str,
        filename: str = None
    ):
        self._log('error', message, filename)

    def exception(
        self,
        message: str,
        exception: Exception,
        filename: str = None
    ):
        traceback = self.get_traceback(exception)
        self._log(
            'exception',
            "\n".join([message, traceback]),
            filename
        )


logger = Logger()
