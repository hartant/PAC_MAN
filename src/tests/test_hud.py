import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame as pg  # noqa: E402

from src.ui.fake_state import make_fake_state  # noqa: E402
from src.ui.hud import Hud  # noqa: E402


def test_hud_draws_in_any_window_size() -> None:
    pg.init()
    hud = Hud()
    for size in [(1200, 900), (500, 400), (1600, 700)]:
        screen = pg.display.set_mode(size)
        hud.draw(screen, make_fake_state())


def test_hud_with_low_time_and_zero_lives() -> None:
    pg.init()
    screen = pg.display.set_mode((800, 600))
    state = make_fake_state()
    state.time_left = 5
    state.lives = 0
    Hud().draw(screen, state)


if __name__ == "__main__":
    test_hud_draws_in_any_window_size()
    test_hud_with_low_time_and_zero_lives()
    print("HUD tests: OK")