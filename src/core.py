import pygame as pg
from src.graphics import Renderer
from src.father import Player
from typing import List


class GameEngine():
    def __init__(self, wx, wy, matrix):
        pg.init()
        self.window_width: int = wx
        self.window_height: int = wy
        self.matrix: List[List[int]] = matrix

        self.offset_x: int = 0
        self.offset_y: int = 0
        self.cell_size: int = 0

        self.calculate_layout(margin=20)
        self.runing: bool = True

        self.screen = pg.display.set_mode(
                                (self.window_width, self.window_height))
        # self.window_width, self.window_height = self.screen.get_size()
        self.clock = pg.time.Clock()

        # can add this in the main and remove it
        self.graphic = Renderer(self.matrix,
                                self.screen,
                                self.offset_x,
                                self.offset_y,
                                self.cell_size
                                )

        self.player = Player((2, 2), "Ahmed")

    def calculate_layout(self, margin: int = 20) -> None:
        rows: int = len(self.matrix)
        cols: int = len(self.matrix[0])

        space: int = self.window_height // 100 * 6

        u_wigth = self.window_width - margin
        u_height = (self.window_height - space) - margin

        cell_size = min(
            u_wigth // cols,
            u_height // rows
        )
        self.cell_size = cell_size
        print(f" tile siez: {self.cell_size}")

        maze_width = cols * self.cell_size
        maze_height = rows * self.cell_size

        self.offset_x = (self.window_width - maze_width) // 2
        self.offset_y = ((self.window_height - space) - maze_height) // 2

    def run(self):
        while self.runing:
            self.screen.fill("black")
            self.handle_event()

            self.draw()
            pg.display.flip()
            self.clock.tick(60)

    def draw(self):
        self.screen.fill("black")
        self.graphic.draw_maze()
        self.player_control()

    def handle_event(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.runing = False

        keys = pg.key.get_pressed()

        if keys[pg.K_q]:
            self.runing = False

    def update(self):
        pass

    def player_control(self):
        print("draw player")
        self.graphic.draw_player(self.player.position)
