import pygame as pg
from typing import List, Tuple


class Renderer():     # (.... w_with,w_height)
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

    def draw_maze(self):
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
        pattern = [
            "100 111",
            "100 001",
            "111 111",
            "001 100",
            "001 111",
        ]
        rows = len(self.matrix)
        cols = len(self.matrix[0])

        start_row = (rows - len(pattern)) // 2
        start_col = (cols - len(pattern[0])) // 2

        colored_cells: set = set()

        for r, line in enumerate(pattern):
            for c, value in enumerate(line):
                if value == "1":
                    colored_cells.add(
                        (start_row + r, start_col + c)
                        )
        return colored_cells

    def draw_player(self, position: Tuple[int]):
        x = position[0] + self.offset_x + self.cell_size // 2
        y = position[1] + self.offset_y + self.cell_size // 2
        print(x, y)
        pg.draw.circle(self.screen, "yellow", (x, y), self.cell_size // 3)
