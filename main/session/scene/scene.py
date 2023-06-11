import numpy as np
from shared_crypto_analysis.shared_python.shared_math.geometry import Vec2
from ...context_wrapper import ContextWrapper
from ...helpers import MOUSE_ACTION
from .shapes.shapes import Shape
from .grid.scene_grid import Grid


class draggable():
    def __init__(self, start_pos: Vec2, dragging_shape: Shape) -> None:
        self.current_pos = start_pos
        self.shape = dragging_shape

    def work(self, pos: Vec2):
        distance = pos - self.current_pos
        self.current_pos = pos
        self.shape.translate(distance)


class Transform:
    def __init__(self):
        self._width = 0.0
        self._height = 0.0

        self.scale_factor = 1.0
        self.pan_offset = Vec2(0.0, 0.0)
        self.zoom_center = Vec2(0.0, 0.0)

    @property
    def width(self) -> int:
        return self._width

    @width.setter
    def width(self, s: float) -> None:
        self._width = s

    @property
    def height(self) -> int:
        return self._height

    @height.setter
    def height(self, s: float) -> None:
        self._height = s

    def mouse_scroll(self, xoffset, yoffset) -> bool:
        self.scale_factor += yoffset / 10.0
        return True

    def matrix(self):
        pan_center = Vec2(self.width / 2, self.height / 2)
        zoomed_pan_offset = self.pan_offset

        translation_to_center = np.array([
            [1, 0, pan_center.x],
            [0, 1, pan_center.y],
            [0, 0, 1]
        ])

        scaling = np.array([
            [self.scale_factor, 0, 0],
            [0, self.scale_factor, 0],
            [0, 0, 1]
        ])

        translation_to_offset = np.array([
            [1, 0, zoomed_pan_offset.x],
            [0, 1, zoomed_pan_offset.y],
            [0, 0, 1]
        ])

        cache_matrix = translation_to_center @ scaling @ translation_to_offset

        return cache_matrix

    def apply_pan(self, pan_offset):
        scaled_pan_offset = pan_offset / self.scale_factor
        self.pan_offset += scaled_pan_offset


class Scene:
    def __init__(self):
        self.shapes = []
        self.draggable = None
        self.selected = None
        self.transform = Transform()

        # Zoom
        self.scale_factor = 1.0
        self.matrix = np.identity(3)
        self.zoom_center = Vec2(0.0, 0.0)

        self.mouse_pos = Vec2(0.0, 0.0)
        self.pan_start_pos = Vec2(0.0, 0.0)

        self.grid = Grid()

    def add_shape(self, shape):
        self.shapes.append(shape)

    def remove_shape(self, shape):
        self.shapes.remove(shape)

    def draw(self, context: ContextWrapper):
        context.save()
        context.concat(self.transform.matrix())

        self.grid.draw(context)

        for shape in self.shapes:
            shape.draw(context)

        context.restore()

    def mouse_scroll(self, xoffset, yoffset) -> bool:
        return self.transform.mouse_scroll(xoffset, yoffset)

    def mouse_action(self, action: MOUSE_ACTION, pos: Vec2) -> bool:
        match action:
            case MOUSE_ACTION.LEFT_CLICK_DOWN:
                if self.selected is None:
                    for this_shape in self.shapes:
                        if this_shape.contains(pos):
                            self.selected = this_shape
                            return True

                 # Store the initial position for panning
                self.pan_start_pos = pos

            case MOUSE_ACTION.LEFT_CLICK_DRAG:
                if self.selected is None:
                    pan_offset = pos - self.pan_start_pos
                    self.transform.apply_pan(pan_offset)
                    self.pan_start_pos = pos  # Update the start position for continuous panning

                    return True

                if self.draggable is None:
                    self.draggable = draggable(pos, self.selected)
                else:
                    self.draggable.work(pos)

            case MOUSE_ACTION.LEFT_CLICK_UP:
                self.draggable = None
                self.selected = None
