import sys


class Logger:

    TRACEBACK_FILENAME: str = "logs/traceback.txt"

    def get_traceback(self, exception: Exception) -> str:
        with open(self.TRACEBACK_FILENAME, 'w') as file:
            sys.print_exception(exception, file)
        with open(self.TRACEBACK_FILENAME, 'r') as file:
            return file.read()


logger = Logger()
