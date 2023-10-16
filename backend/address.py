from backend.config import config


class Address:

    ASCII_LOWERCASE: str = 'abcdefghijklmnopqrstuvwxyz'
    NUMBERS_PER_LETTER: int = 16
    LETTER: str = 'a'

    @classmethod
    def all_addresses(cls) -> list['Address']:
        return [
            cls(config.device_id, cls.LETTER, number)
            for number in range(config.fuse_amount)
        ]

    _device_id: str
    _letter: str
    _number: int

    def __init__(self, device_id: str, letter: str, number: int):
        self._device_id = device_id.lower()
        self._letter = letter.lower()
        self._number = number

    def _raise_on_letter(self):
        if len(self._letter) != 1:
            raise ValueError(f"letter has to be of length 1: {self._letter}")
        if self._letter not in self.ASCII_LOWERCASE:
            raise ValueError(
                f"letter has to be an ascii letter: {self._letter}"
            )

    def _raise_on_number(self):
        if self._number < 0 or self._number >= self.NUMBERS_PER_LETTER:
            raise ValueError(
                f"number has to be a positive integer in "
                f"[0,{self.NUMBERS_PER_LETTER - 1}]: {self._number}"
            )

    @property
    def device_id(self) -> str:
        return self._device_id

    @property
    def letter(self) -> str:
        return self._letter

    @property
    def number(self) -> int:
        return self._number

    @property
    def fuse_index(self) -> int:
        if self._letter != self.LETTER:
            raise RuntimeError()
        if self._number >= config.fuse_amount:
            raise RuntimeError()
        return self._number

    def __str__(self) -> str:
        return f"{self._device_id}::{self._letter}{self._number}"

    def __repr__(self) -> str:
        return f"Address({str(self)})"

    def __eq__(self, other: 'Address') -> bool:
        return (
            self._device_id == other.device_id
            and self._letter == other.letter
            and self._number == other.number
        )
