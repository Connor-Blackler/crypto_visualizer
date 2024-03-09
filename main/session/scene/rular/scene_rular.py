from __future__ import annotations
import uuid
from typing import Protocol
from copy import deepcopy
import numpy as np
from ....context_wrapper import ContextWrapper, path_provider
from ....helpers import Color
from shared_crypto_analysis.shared_python.shared_math.geometry import Vec2, BezierPathA, BezierPath, BezierContour, BezierPoint
from ...properties import TIME_INTERVAL


class TransformProvider(Protocol):
    def width(self) -> float:
        ...

    def height(self) -> float:
        ...

    def matrix(self) -> np.ndarray:
        ...


class Rular:
    def __init__(self, transform_provider: TransformProvider) -> None:
        self.id = uuid.uuid4()
        self._transform = transform_provider
        self._regenerate = True

        # initialize session property vars
        self._grid_width = None
        self._interval = None

        # rular specific variables
        self._context_path = path_provider()()

    def _regenerate_path(self):
        self._path = BezierPathA()

        self._context_path.set_path(self._path)

    def draw(self, context: ContextWrapper) -> None:
        if self._regenerate:
            self._regenerate_path()
            self._regenerate = False

        context.draw_path(self._context_path)
