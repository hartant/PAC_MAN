from mazegenerator import MazeGenerator
from src.core import GameEngine
import pygame as pg


if __name__ == "__main__":
    maze_width = 20
    maze_height = 20

    win_with = 1200
    win_heigh = 800

    mazeg = MazeGenerator(size=(maze_width, maze_height))
    print(mazeg.maze)
    engine = GameEngine(
                    win_with,
                    win_heigh,
                    mazeg.maze
                )
    engine.run()
    pg.quit()
