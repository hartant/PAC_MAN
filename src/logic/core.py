import pygame as pg
from src.ui.graphics import Renderer
from src.logic.father import Player
from typing import List


class GameEngine():
    def __init__(self, wx, wy, matrix):
        pg.init()
        self.matrix: List[List[int]] = matrix

        # reuse the menu window; create it only if it does not exist
        screen = pg.display.get_surface()
        if screen is None:
            screen = pg.display.set_mode((wx, wy), pg.RESIZABLE)
        self.screen = screen
        self.window_width, self.window_height = screen.get_size()

        self.offset_x: int = 0
        self.offset_y: int = 0
        self.cell_size: int = 0

        self.calculate_layout(margin=20)
        self.runing: bool = True
        self.clock = pg.time.Clock()

        self.graphic = Renderer(self.matrix,
                                self.screen,
                                self.offset_x,
                                self.offset_y,
                                self.cell_size
                                )
        self.graphic.set_layout(self.screen, self.offset_x,
                                self.offset_y, self.cell_size)

        self.player = Player((2, 2), "Ahmed")

    def refresh_layout(self) -> None:
        """If the window size changed, recompute the maze layout."""
        screen = pg.display.get_surface()
        if screen is None:
            return
        self.screen = screen
        size = screen.get_size()
        if size != (self.window_width, self.window_height):
            self.window_width, self.window_height = size
            self.calculate_layout(margin=20)
        self.graphic.set_layout(self.screen, self.offset_x,
                                self.offset_y, self.cell_size)

    def calculate_layout(self, margin: int = 40) -> None:
        rows: int = len(self.matrix)
        cols: int = len(self.matrix[0])

        # Mssaha dyal l-HUD f l-t7t wla l-foq
        space: int = 60 

        u_width = self.window_width - (margin * 2)
        u_height = (self.window_height - space) - (margin * 2)

        cell_size = min(
            u_width // cols,
            u_height // rows
        )

        # Check ila kan l-size sghir bzzaf (t-la3 mesg f terminal)
        if cell_size < 15:
            print("WARNING: Window size is too small! Maze tiles will be too tiny to display properly.")

        self.cell_size = max(10, cell_size)  # Safe minimum size

        maze_width = cols * self.cell_size
        maze_height = rows * self.cell_size

        # Hisab offsets bash l-maze y-ji m-sawwi f l-wast dyal l-fnatra
        self.offset_x = (self.window_width - maze_width) // 2
        self.offset_y = margin + ((self.window_height - space - (margin * 2)) - maze_height) // 2

    def run(self):
        while self.runing:
            self.refresh_layout()
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
        self.graphic.draw_player(self.player.position)
