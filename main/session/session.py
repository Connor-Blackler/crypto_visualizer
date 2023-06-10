from .scene.scene import Scene
from ..context_wrapper import ContextWrapper
from ..helpers import MOUSE_ACTION
from shared_crypto_analysis.shared_python.shared_math.geometry import Vec2
from .properties import SessionProperties, TIME_INTERVAL


class Session:
    def __init__(self) -> None:
        self.scene = Scene()
        self.properties = SessionProperties()

        self.properties.grid_width_register_callback(
            self.scene.grid.__class__.grid_width.fset.__get__(self.scene.grid))
        self.properties.grid_width = 10

        self.properties.interval_register_callback(
            self.scene.grid.__class__.interval.fset.__get__(self.scene.grid))
        self.properties.interval = TIME_INTERVAL.D_1

    def add_shape(self, shape):
        self.scene.add_shape(shape)

    def remove_shape(self, shape):
        self.scene.remove_shape(shape)

    def draw(self, context: ContextWrapper):
        self.scene.draw(context)

    def mouse_action(self, action: MOUSE_ACTION, pos: Vec2) -> bool:
        return self.scene.mouse_action(action, pos)
