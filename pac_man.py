from mazegenerator import MazeGenerator
from src.logic.core import GameEngine
import pygame as pg
from src.ui.menu import MenuScreen


if __name__ == "__main__":
    maze_width = 20
    maze_height = 20

    win_with = 1200
    win_heigh = 800

    mazeg = MazeGenerator(size=(maze_width, maze_height))
    pg.init()
    screen = pg.display.set_mode((800, 800))
    scores = [("Ann", 100), ("Bob", 50)]   # fake list until highscore.py exists
    choice = MenuScreen(screen, scores).run()
    if choice == "playing":
        engine.run()
    pg.quit()