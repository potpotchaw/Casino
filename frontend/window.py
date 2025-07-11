from __future__ import annotations

__all__ = ("MainWindow",)

import logging
import typing

import arcade
from arcade import View

import frontend.constants as c
from frontend.internal.net_client import NetClient
from frontend.net.rest_client import RestClient
from frontend.views import MainMenu
from frontend.views import PauseMenu
from frontend.views import TitleView
from frontend.views.game_view import GameView
from frontend.views.lobbys_view import LobbysView
from frontend.views.login_view import LoginMenu

if typing.TYPE_CHECKING:
    import pathlib

    from pyglet.event import EVENT_HANDLE_STATE

    from frontend.views.base import BaseView

logger = logging.getLogger(__name__)


class MainWindow(arcade.Window):
    def __init__(self, root_path: pathlib.Path) -> None:
        logger.debug("Initializing Main Window")
        logger.debug("Screen size: %sx%s", c.SCREEN_WIDTH, c.SCREEN_HEIGHT)
        logger.debug("Center: %s,%s", c.CENTER_X, c.CENTER_Y)
        super().__init__(title=c.WINDOW_NAME, fullscreen=c.FULL_SCREEN, width=c.SCREEN_WIDTH, height=c.SCREEN_HEIGHT)
        arcade.set_background_color(arcade.color.BLACK)
        self.set_update_rate(1 / c.UPDATES_PER_SECOND)
        self.set_fps(c.DEFAULT_FPS)

        self.shader_path = root_path / "shaders"
        self.net_client = NetClient[RestClient](RestClient, "127.0.0.1:8000")

        self._title_view = TitleView(window=self)
        self._main_menu = MainMenu(window=self)
        self._pause_menu = PauseMenu(window=self)
        self._login_menu = LoginMenu(window=self)

        self._blackjack_lobby_view = LobbysView(window=self, game_mode=c.GameModes.BLACKJACK)

        self._current_selected_view: BaseView = self._title_view
        self._show_view(self._title_view)

    def set_fps(self, fps: int) -> None:
        if fps > c.UPDATES_PER_SECOND:
            logger.debug(
                "Tried setting fps to %s, faster then the update rate of %s, capping fps to %s",
                fps,
                c.UPDATES_PER_SECOND,
                c.UPDATES_PER_SECOND,
            )
            fps = c.UPDATES_PER_SECOND
        self.set_draw_rate(1 / fps)

    def get_shader_path(self, shader_name: str) -> pathlib.Path:
        return self.shader_path / f"{shader_name}.glsl"

    @typing.override
    def show_view(self, new_view: View) -> None:
        logger.debug("Showing view %s", new_view)
        super().show_view(new_view)

    def _show_view(self, view: BaseView) -> None:
        if self.current_view == view:
            return
        self._current_selected_view.deactivate()
        self.show_view(view)
        self._current_selected_view = view
        self._current_selected_view.activate()

    def show_main_menu(self) -> None:
        if self.net_client.authorized:
            self._show_view(self._main_menu)
        else:
            self._show_view(self._login_menu)

    def show_game(self, game_mode: c.GameModes, lobby_id: str) -> None:
        game_view = GameView(window=self, game_mode=game_mode, lobby_id=lobby_id)
        self._show_view(view=game_view)

    def show_lobbys(self, game_mode: c.GameModes) -> None:
        match game_mode:
            case c.GameModes.BLACKJACK:
                self._show_view(self._blackjack_lobby_view)
            case _:
                raise TypeError(f"No lobbys view for game mode: {game_mode}")

    def toggle_pause_menu(self) -> None:
        if self._pause_menu.shown:
            self.show_view(self._current_selected_view)
            self._pause_menu.shown = False
        else:
            self.show_view(self._pause_menu)
            self._pause_menu.shown = True

    @typing.override
    def on_key_press(self, symbol: int, modifiers: int) -> EVENT_HANDLE_STATE:
        if symbol == arcade.key.ESCAPE and self._current_selected_view.can_pause:
            self.toggle_pause_menu()

    @property
    def current_selected_view(self) -> BaseView:
        return self._current_selected_view

    @typing.override
    def on_update(self, delta_time: float) -> bool | None:
        if not self.net_client.authorized and self.current_selected_view != self._title_view:
            self._show_view(self._login_menu)
