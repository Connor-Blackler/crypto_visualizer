import numpy as np
from shared_crypto_analysis.shared_python.shared_math.geometry import Vec2
from ...context_wrapper import ContextWrapper
from ...helpers import MOUSE_ACTION, Color
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
        self.scale_factor = max(0.3, self.scale_factor)
        return True

    def matrix(self) -> np.ndarray:
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
        self._shapes = []
        self._draggable = None
        self._selected = None

        # core scene classes
        self.transform = Transform()
        self.grid = Grid(self.transform)

        # Zoom
        self._scale_factor = 1.0
        self._matrix = np.identity(3)
        self._zoom_center = Vec2(0.0, 0.0)

        self._mouse_pos = Vec2(0.0, 0.0)
        self._pan_start_pos = Vec2(0.0, 0.0)

    def add_shape(self, shape):
        self._shapes.append(shape)

    def remove_shape(self, shape):
        self._shapes.remove(shape)

    def draw(self, context: ContextWrapper):
        context.save()
        context.concat(self.transform.matrix())

        self.grid.draw(context)

        for shape in self._shapes:
            shape.draw(context)

        context.restore()

    def mouse_scroll(self, xoffset, yoffset) -> bool:
        return self.transform.mouse_scroll(xoffset, yoffset)

    def mouse_action(self, action: MOUSE_ACTION, pos: Vec2) -> bool:
        # Apply inverse transformation to the mouse position
        inverse_matrix = np.linalg.inv(self.transform.matrix())
        transformed_pos = np.dot(inverse_matrix, [pos.x, pos.y, 1.0])
        transformed_pos = Vec2(transformed_pos[0], transformed_pos[1])

        match action:
            case MOUSE_ACTION.LEFT_CLICK_DOWN:
                if self._selected is None:
                    for this_shape in self._shapes:
                        if this_shape.contains(transformed_pos):
                            self._selected = this_shape
                            return True

                 # Store the initial position for panning
                self._pan_start_pos = pos

            case MOUSE_ACTION.LEFT_CLICK_DRAG:
                if self._selected is None:
                    pan_offset = pos - self._pan_start_pos
                    self.transform.apply_pan(pan_offset)
                    # Update the start position for continuous panning
                    self._pan_start_pos = pos

                    return True

                if self._draggable is None:
                    self._draggable = draggable(
                        transformed_pos, self._selected)
                else:
                    self._draggable.work(transformed_pos)

            case MOUSE_ACTION.LEFT_CLICK_UP:
                self._draggable = None
                self._selected = None

            case MOUSE_ACTION.RIGHT_CLICK_DOWN:
                pass

            case MOUSE_ACTION.RIGHT_CLICK_UP:
                self.add_shape(
                    Shape.construct_polygon(transformed_pos + Vec2(60, 60), 40, 6, Color(50, 50, 50)))

                self.add_shape(
                    Shape.construct_circle(transformed_pos, 40, Color(50, 50, 50)))
