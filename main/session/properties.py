from enum import Enum
from typing import Callable
from ..logic_helpers.property import DataWithCallback


class TIME_INTERVAL(Enum):
    H_12 = "12H",
    D_1 = "1D",
    D_2 = "1D",


class SessionProperties:
    def __init__(self) -> None:
        self._grid_width = DataWithCallback(None)
        self._interval = DataWithCallback(None)

    @property
    def grid_width(self) -> None:
        return self._grid_width.value

    @grid_width.setter
    def grid_width(self, value: int) -> None:
        self._grid_width.value = value

    def grid_width_register_callback(self, callback: Callable[[int], None]):
        self._grid_width.changed.register(callback)

    @property
    def interval(self) -> None:
        return self._interval.value

    @interval.setter
    def interval(self, value: TIME_INTERVAL) -> None:
        self._interval.value = value

    def interval_register_callback(self, callback: Callable[[TIME_INTERVAL], None]):
        self._interval.changed.register(callback)
