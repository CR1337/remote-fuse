class RlException(Exception):

    def __init__(self, message: str = None):
        self.message = message if message else ""
        super().__init__(self.message)
