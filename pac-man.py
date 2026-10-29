"""Pac-Man. Start with:  python3 pac-man.py config.json

Game loop: main menu > start game > win or lose > enter name > main menu.
"""

import sys

import pygame as pg

from src.logic.core import GameEngine
from src.logic.highscore import ScoringSystem
from src.logic.maze import MazeError
from src.ui.config import load_config
from src.ui.menu import MenuScreen

WINDOW_SIZE = (1200, 900)


def main() -> int:
    """Run the menu and the games until the player exits."""
    if len(sys.argv) != 2:
        print("Usage: python3 pac-man.py config.json")
        return 1

    config = load_config(sys.argv[1])
    scoring = ScoringSystem(config.highscore_filename)

    pg.init()
    pg.display.set_mode(WINDOW_SIZE, pg.RESIZABLE)
    pg.display.set_caption("Pac-Man")

    message = ""
    while True:
        surface = pg.display.get_surface()
        if surface is None:
            break
        menu = MenuScreen(surface, scoring.top(), message)
        message = ""
        if menu.run() != "playing":     # "quit": leave the program
            break

        try:
            engine = GameEngine(config, scoring, *WINDOW_SIZE)
        except MazeError as err:        # the maze generator failed
            print(f"Error: {err}")
            message = "Cannot generate the maze. See the terminal."
            continue

        if engine.run() == "quit":
            break

    pg.quit()
    print("Exiting Pac-Man.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pg.quit()
        print("\nExiting Pac-Man.")
        sys.exit(0)
    except Exception as error:          # last safety net: no traceback
        pg.quit()
        print(f"Unexpected error: {type(error).__name__}: {error}")
        sys.exit(1)
