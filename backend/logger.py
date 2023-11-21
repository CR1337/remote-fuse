import sys
import os
from backend import time_util as tu


class Logger:

    TRACEBACK_FILENAME: str = "logs/traceback.txt"
    START: str = ">>>"
    SEP: str = ":::"

    _filename: str

    def get_traceback(self, exception: Exception) -> str:
        with open(self.TRACEBACK_FILENAME, 'w') as file:
            sys.print_exception(exception, file)
        with open(self.TRACEBACK_FILENAME, 'r') as file:
            return file.read()

    def __init__(self):
        try:
            os.stat("/logs")
        except OSError:
            os.mkdir("/logs")
        self._set_filename()

    def _set_filename(self):
        taken_numbers = [
            int(filename.split(".")[0])
            for filename in os.listdir("/logs")
            if filename.endswith(".log")
        ] + [-1]
        number = max(taken_numbers) + 1
        self._filename = f"logs/{number}.log"

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
        try:
            with open(self._filename, 'a', encoding='utf-8') as file:
                file.write(f"{log_entry}\n")
        except OSError:
            with open(self._filename, 'w', encoding='utf-8') as file:
                file.write(f"{log_entry}\n")

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

    def get_log_files(self) -> list[str]:
        return [
            filename for filename
            in os.listdir("logs")
            if filename.endswith(".log")
        ]

    def get_log_file_content(self, name: str) -> str:
        with open(f"logs/{name}", 'r', encoding='utf-8') as file:
            return file.read()

    def get_log_structured_content(self, name: str) -> list[dict[str, str]]:
        content = self.get_log_file_content(name).replace("\n", "")
        structured_content = []
        for line in content.split(self.START)[1:]:
            time, level, thread, file, lineno, message = line.split(self.SEP)
            structured_content.append({
                'time': time,
                'level': level,
                'thread': thread,
                'file': file,
                'line': lineno,
                'message': message
            })
        return structured_content

    def logfile_exists(self, name: str) -> bool:
        try:
            with open(f"logs/{name}", 'r') as _:
                return True
        except OSError:
            return False

    def delete_all_logfiles(self):
        for filename in self.get_log_files():
            self.delete_logfile(filename)

    def delete_logfile(self, filename: str):
        os.remove(f"logs/{filename}")


logger = Logger()
