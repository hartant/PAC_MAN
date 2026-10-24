import pygame as pg
from typing import List, Tuple

# red, pink, cyan, orange (like the original game)
GHOST_COLORS = [(255, 0, 0), (255, 184, 255), (0, 255, 255), (255, 184, 82)]
EDIBLE_COLOR = (40, 40, 255)


class Renderer():
    def __init__(
            self,
            matrix: List[List[int]],
            screen: pg.Surface,
            offset_x: int,
            offset_y: int,
            cell_size: int
            ) -> None:
        self.matrix: List[List[int]] = matrix
        self.screen = screen
        self.offset_x: int = offset_x
        self.offset_y: int = offset_y
        self.cell_size: int = cell_size
        self.wall_thickness: int = 2

    def set_layout(self, screen: pg.Surface, offset_x: int,
                   offset_y: int, cell_size: int) -> None:
        """Called when the window size changes."""
        self.screen = screen
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.cell_size = cell_size
        self.wall_thickness = max(2, cell_size // 12)

    def draw_maze(self) -> None:
        colored_cells = self.get_42_cells()
        rows = len(self.matrix)
        cols = len(self.matrix[0])
        for row in range(rows):
            for col in range(cols):
                cell = self.matrix[row][col]

                x = self.offset_x + col * self.cell_size
                y = self.offset_y + row * self.cell_size

                if (row, col) in colored_cells:
                    pg.draw.rect(
                        self.screen,
                        (40, 100, 255),
                        (x, y, self.cell_size, self.cell_size)
                    )

                if cell & 1:
                    pg.draw.line(
                            self.screen,
                            "white",
                            (x, y),
                            (x + self.cell_size, y),
                            self.wall_thickness
                        )

                if cell & 2:
                    pg.draw.line(
                            self.screen,
                            "white",
                            (x + self.cell_size, y),
                            (x + self.cell_size, y + self.cell_size),
                            self.wall_thickness
                        )

                if cell & 4:
                    pg.draw.line(
                            self.screen,
                            "white",
                            (x, y + self.cell_size),
                            (x + self.cell_size, y + self.cell_size),
                            self.wall_thickness
                        )

                if cell & 8:
                    pg.draw.line(
                            self.screen,
                            "white",
                            (x, y),
                            (x, y + self.cell_size),
                            self.wall_thickness
                        )

    def get_42_cells(self) -> set:
        """The '42' cells are the ones closed on all 4 sides (value 15)."""
        colored_cells: set = set()
        for row, line in enumerate(self.matrix):
            for col, cell in enumerate(line):
                if cell == 15:
                    colored_cells.add((row, col))
        return colored_cells

    def draw_player(self, pos_x: int, pos_y: int) -> None:
        """position = (column, row) of the player in the maze (cells)."""
        x = self.offset_x + pos_x * self.cell_size + self.cell_size // 2
        y = self.offset_y + pos_y * self.cell_size + self.cell_size // 2
        pg.draw.circle(self.screen, "yellow", (x, y), self.cell_size // 3)
    
    def cell_center(self, col: int, row: int) -> tuple[int, int]:
        """Pixel position of the center of a cell."""
        x = self.offset_x + col * self.cell_size + self.cell_size // 2
        y = self.offset_y + row * self.cell_size + self.cell_size // 2
        return x, y

    def draw_pacgums(self, positions: set[tuple[int, int]]) -> None:
        """Small dots. positions = set of (column, row) cells."""
        radius = max(2, self.cell_size // 10)
        for col, row in positions:
            pg.draw.circle(self.screen, (255, 220, 170),
                           self.cell_center(col, row), radius)

    def draw_super_pacgums(self, positions: set[tuple[int, int]]) -> None:
        """Big dots. positions = set of (column, row) cells."""
        radius = max(4, self.cell_size // 4)
        for col, row in positions:
            pg.draw.circle(self.screen, "white",
                           self.cell_center(col, row), radius)
    
    def draw_ghosts(self, ghosts: list[tuple[int, int, bool]]) -> None:
        """ghosts = list of (column, row, edible)."""
        r = self.cell_size // 3
        for i, (col, row, edible) in enumerate(ghosts):
            x, y = self.cell_center(col, row)
            color = EDIBLE_COLOR if edible else GHOST_COLORS[i % 4]
            pg.draw.circle(self.screen, color, (x, y), r)           # head
            pg.draw.rect(self.screen, color, (x - r, y, 2 * r, r))  # body
            for dx in (-r // 2, r // 2):                            # eyes
                pg.draw.circle(self.screen, "white",
                               (x + dx, y - r // 4), max(2, r // 3))
                pg.draw.circle(self.screen, "black",
                               (x + dx, y - r // 4), max(1, r // 6))

                               
