from __future__ import annotations
import uuid
from copy import deepcopy
from ....context_wrapper import ContextWrapper, path_provider
from ....helpers import Color
from shared_crypto_analysis.shared_python.shared_math.geometry import Vec2, BezierPathA, BezierPath, BezierContour, BezierPoint
from ...properties import TIME_INTERVAL


class Grid:
    def __init__(self) -> None:
        self.id = uuid.uuid4()
        self.regenerate = True

        # initialize session property vars
        self._grid_width = None
        self._interval = None

        # Grid specific variables
        self._path = None
        self.stroke_thickness = 0.03
        self.context_path = path_provider()(
            None, Color(255, 255, 255), None, self.stroke_thickness)

    @property
    def grid_width(self) -> int:
        return self._grid_width

    @grid_width.setter
    def grid_width(self, grid_width: int) -> None:
        # Should only be called by session properties as a callback
        self._grid_width = grid_width

    @property
    def interval(self) -> TIME_INTERVAL:
        return self._interval

    @interval.setter
    def interval(self, interval: TIME_INTERVAL) -> None:
        # Should only be called by session properties as a callback
        self._interval = interval
        self.regenerate = True

    def regenerate_path(self):
        self._path = BezierPathA()

        start = BezierPath()
        start_c = BezierContour(False)
        start_c.add_point(BezierPoint(Vec2(-99999, -99999)))
        start_c.add_point(BezierPoint(Vec2(-99999, 99999)))
        start.add_contour(start_c)

        start_y = BezierPath()
        start_y_c = BezierContour(False)
        start_y_c.add_point(BezierPoint(Vec2(-99999, -99999)))
        start_y_c.add_point(BezierPoint(Vec2(99999, -99999)))
        start_y.add_contour(start_y_c)

        for x in range(0, 5000):
            self._path.paths.append(start)
            start = deepcopy(start)
            start.translate(Vec2(108.0, 0.0))

            self._path.paths.append(start_y)
            start_y = deepcopy(start_y)
            start_y.translate(Vec2(0.0, 108.0))

        self.context_path.set_path(self._path)

    def draw(self, context: ContextWrapper) -> None:
        if self.regenerate:
            self.regenerate_path()
            self.regenerate = False

        context.draw_path(self.context_path)
