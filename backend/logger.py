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
        self._filename = f"logs/remote-{str(tu.get_system_time())}.log"

    def _log(self, level: str, message: str):
        time_string = tu.get_system_time.split(".")[0]
        time_string = time_string.replace("T", " ").replace(":", ".")
        log_entry = (
            f"{self.START}{time_string}{self.SEP}{level}"
            f"{self.SEP}main_thread"
            f"{self.SEP}NO_FILENAME{self.SEP}NO_LINE{self.SEP}{message}"  # TODO
        )
        print(log_entry)
        with open(self._filename, 'a', encoding='utf-8') as file:
            file.write(f"{log_entry}\n")

    def debug(self, message: str):
        self._log('debug', message)

    def info(self, message: str):
        self._log('info', message)

    def warning(self, message: str):
        self._log('warning', message)

    def error(self, message: str):
        self._log('error', message)

    def exception(self, message: str):
        self._log('exception', message)  # TODO

    def get_log_files() -> list[str]:
        return [
            filename for filename
            in os.listdir("logs")
            if filename.endswith(".log")
        ]

    def get_log_file_content(name: str) -> str:
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

    def logfile_exists(name: str) -> bool:
        try:
            with open(f"logs/{name}", 'r') as _:
                return True
        except OSError:
            return False


logger = Logger()
