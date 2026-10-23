import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame as pg  # noqa: E402

from src.ui.menu import MainMenu, MenuScreen  # noqa: E402


def test_down_then_enter() -> None:
    menu = MainMenu()
    assert menu.handle_key("down") == "menu"
    assert menu.handle_key("enter") == "highscores"


def test_wrap_around() -> None:
    menu = MainMenu()
    menu.handle_key("up")
    assert menu.handle_key("enter") == "quit"


def test_space_starts_game() -> None:
    assert MainMenu().handle_key("space") == "playing"


def test_unknown_key_ignored() -> None:
    menu = MainMenu()
    assert menu.handle_key("banana") == "menu"
    assert menu.selected == 0


def _screen() -> MenuScreen:
    pg.init()
    surface = pg.display.set_mode((800, 800))
    return MenuScreen(surface, [("Ann", 100), ("Bob", 50)])


def _key(key: int) -> pg.event.Event:
    return pg.event.Event(pg.KEYDOWN, key=key)


def test_open_and_close_instructions() -> None:
    ms = _screen()
    ms.handle_event(_key(pg.K_DOWN))
    ms.handle_event(_key(pg.K_DOWN))
    assert ms.handle_event(_key(pg.K_RETURN)) is None
    assert ms.current == "instructions"
    ms.handle_event(_key(pg.K_a))
    assert ms.current == "menu"


def test_start_and_quit_results() -> None:
    ms = _screen()
    assert ms.handle_event(_key(pg.K_SPACE)) == "playing"
    assert ms.handle_event(pg.event.Event(pg.QUIT)) == "quit"


def test_drawing_does_not_crash_with_empty_scores() -> None:
    pg.init()
    ms = MenuScreen(pg.display.set_mode((800, 800)), [])
    ms.draw_menu()
    ms.draw_highscores()
    ms.draw_instructions()