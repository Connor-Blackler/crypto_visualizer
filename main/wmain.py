from __future__ import annotations
import contextlib
import glfw
from OpenGL import GL
import skia
from skia import *
from shared_crypto_analysis.shared_python.shared_math.geometry import Vec2
from .context_wrapper import ContextWrapperSkia, ContextWrapper
from .ui_classes.button import Button
from .ui_classes.toolbar import Toolbar
from .helpers import MOUSE_ACTION, Color
from .session.session import Session


class _DrawArea:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.session = Session()
        self.toolbar = Toolbar(
            Vec2(0, 0), self.width, 32,
            [Button("select", 32, 32, Color(255, 0, 0)),
             Button("delete", 32, 32, Color(0, 255, 0))])

        self.mouse_pos = Vec2(0.0, 0.0)

    def add_shape(self, shape):
        self.session.add_shape(shape)

    def remove_shape(self, shape):
        self.session.remove_shape(shape)

    def draw(self, context: ContextWrapper):
        # Render contents of the draw area
        context.save()
        self.session.draw(context)
        context.restore()

        # Render UI
        self.toolbar.draw(context)

    def mouse_button_callback(self, window, button, action, mods):
        x, y = glfw.get_cursor_pos(window)
        pos = Vec2(x, y)

        if button == glfw.MOUSE_BUTTON_LEFT:
            if action == glfw.PRESS:
                clicked_button = self.toolbar.hit_test(pos)
                if clicked_button:
                    clicked_button.click()
                else:
                    self.session.mouse_action(
                        MOUSE_ACTION.LEFT_CLICK_DOWN, pos)

            elif action == glfw.RELEASE:
                self.session.mouse_action(MOUSE_ACTION.LEFT_CLICK_UP, pos)

        if button == glfw.MOUSE_BUTTON_RIGHT:
            if action == glfw.PRESS:
                self.session.mouse_action(
                    MOUSE_ACTION.RIGHT_CLICK_DOWN, pos)

            if action == glfw.RELEASE:
                self.session.mouse_action(
                    MOUSE_ACTION.RIGHT_CLICK_UP, pos)

    def scroll_callback(self, window, xoffset, yoffset):
        self.session.mouse_scroll(xoffset, yoffset)

    def cursor_pos_callback(self, window, xpos, ypos):
        self.mouse_pos.x = xpos
        self.mouse_pos.y = ypos

        if glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_LEFT) == glfw.PRESS:
            pos = Vec2(xpos, ypos)
            self.session.mouse_action(MOUSE_ACTION.LEFT_CLICK_DRAG, pos)

    def window_size_callback(self, window, width, height):
        self.width = width
        self.height = height
        self.session.scene.transform.width = width
        self.session.scene.transform.height = height


class Wmain:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.draw_area = _DrawArea(width, height)

    def run(self):
        with self.glfw_window(self.width, self.height) as window:
            glfw.set_mouse_button_callback(
                window, self.draw_area.mouse_button_callback)
            glfw.set_cursor_pos_callback(
                window, self.draw_area.cursor_pos_callback)
            glfw.set_scroll_callback(
                window, self.draw_area.scroll_callback)
            glfw.set_window_size_callback(
                window, self.draw_area.window_size_callback)

            width, height = glfw.get_window_size(window)
            self.draw_area.window_size_callback(window, width, height)

            while not glfw.window_should_close(window):
                GL.glClear(GL.GL_COLOR_BUFFER_BIT)

                with self.skia_surface(window) as surface:
                    with surface as canvas:
                        self.draw_area.draw(ContextWrapperSkia(canvas))

                    surface.flushAndSubmit()
                    glfw.swap_buffers(window)

                glfw.poll_events()

    @staticmethod
    @contextlib.contextmanager
    def skia_surface(window):
        context = GrDirectContext.MakeGL()
        (fb_width, fb_height) = glfw.get_framebuffer_size(window)
        backend_render_target = GrBackendRenderTarget(
            fb_width,
            fb_height,
            0,  # sampleCnt
            0,  # stencilBits
            GrGLFramebufferInfo(0, GL.GL_RGBA8))
        surface = skia.Surface.MakeFromBackendRenderTarget(
            context, backend_render_target, kBottomLeft_GrSurfaceOrigin,
            kRGBA_8888_ColorType, ColorSpace.MakeSRGB())
        assert surface is not None
        yield surface
        context.abandonContext()

    @staticmethod
    @contextlib.contextmanager
    def glfw_window(width, height):
        if not glfw.init():
            raise RuntimeError('glfw.init() failed')
        glfw.window_hint(glfw.STENCIL_BITS, 8)
        window = glfw.create_window(width, height, '', None, None)
        glfw.make_context_current(window)
        yield window
        glfw.terminate()
