"""Pac-Man. Start with:  python3 pac-man.py config.json

Game loop: main menu > start game > win or lose > enter name > main menu.
"""

import os
import sys

import pygame as pg
from src.logic.core import GameEngine
from src.logic.highscore import ScoringSystem
from src.logic.maze import MazeError
from src.ui.config import GameConfig
from src.ui.menu import MenuScreen


WINDOW_SIZE = (1200, 900)


class Application:
    """The whole program: config, window, menu and games."""

    def __init__(self, config_path: str) -> None:
        """Read the config and the highscores (the window comes later)."""
        self.config: GameConfig = GameConfig.from_file(config_path)
        self.scoring: ScoringSystem = ScoringSystem(
            self.config.highscore_filename)
        self.message: str = ""      # error shown in red in the menu

    def run(self) -> int:
        """Run the menu and the games until the player exits."""
        pg.init()
        pg.display.set_mode(WINDOW_SIZE, pg.RESIZABLE)
        pg.display.set_caption("Pac-Man")

        while True:
            surface = pg.display.get_surface()
            if surface is None:
                break
            menu = MenuScreen(surface, self.scoring.top(), self.message)
            self.message = ""
            if menu.run() != "playing":     # "quit": leave the program
                break
            if not self.play():
                break

        pg.quit()
        print("Exiting Pac-Man.")
        return 0

    def play(self) -> bool:
        """Play one game. Returns False if the player wants to quit."""
        try:
            engine = GameEngine(self.config, self.scoring, *WINDOW_SIZE)
        except MazeError as err:        # the maze generator failed
            print(f"Error: {err}")
            self.message = "Cannot generate the maze. See the terminal."
            return True
        return engine.run() != "quit"


def config_from_args(argv: list[str]) -> str | None:
    """Return the config path given on the command line, or None.

    The packaged game (PyInstaller, Itch.io) is started by a double click,
    without any argument: it then uses the config.json next to the game.
    """
    if len(argv) == 2:
        return argv[1]
    if getattr(sys, "frozen", False) and len(argv) == 1:
        game_dir = os.path.dirname(os.path.abspath(sys.executable))
        os.chdir(game_dir)          # highscores.json is saved here too
        return os.path.join(game_dir, "config.json")
    return None


if __name__ == "__main__":
    config_path = config_from_args(sys.argv)
    if config_path is None:
        print("Usage: python3 pac-man.py config.json")
        sys.exit(1)
    try:
        sys.exit(Application(config_path).run())
    except KeyboardInterrupt:
        pg.quit()
        print("\nExiting Pac-Man.")
        sys.exit(0)
    except Exception as error:          # last safety net: no traceback
        pg.quit()
        print(f"Unexpected error: {type(error).__name__}: {error}")
        sys.exit(1)
