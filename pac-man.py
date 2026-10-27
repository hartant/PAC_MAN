import sys
import logging
import pygame as pg
from src.ui.config import load_config  # Or wherever your config loader is
from src.ui.menu import MenuScreen
from src.logic.core import GameEngine
from mazegenerator import MazeGenerator


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 pac-man.py config.json")
        sys.exit(1)

    config_path = sys.argv[1]

    config = load_config(config_path)

    pg.init()
    screen_width = 1200
    screen_height = 900
    pg.display.set_mode((screen_width, screen_height), pg.RESIZABLE)
    pg.display.set_caption("Pac-Man")

    dummy_highscores = [
        ("Sannaka", 1110),
        ("foliole", 20),
        ("Marmelade", 20),
        ("goldfish", 20)
    ]

    while True:
        menu_screen = MenuScreen(pg.display.get_surface(), dummy_highscores)
        action = menu_screen.run()
        if action != "playing":      # "quit": leave the program
            break

        maze = MazeGenerator(size=(15, 15), perfect=False,
                             seed=config.seed).maze
        engine = GameEngine(1200, 900, maze, cheat_mode=False)
        if engine.run() == "quit":
            break

    print("Exiting Pac-Man.")
    pg.quit()
    sys.exit(0)
