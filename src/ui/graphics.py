"""Draws the maze, the dots, the player and the ghosts. No game rules here.

The game engine says what to draw, this file only knows how.
"""

import math
from typing import Dict, List, Tuple

import pygame as pg

from src.logic.father import EATEN, Ghost, Player
from src.logic.maze import Maze

Color = Tuple[int, int, int]

WALL_COLOR: Color = (50, 80, 255)
CELL_42_COLOR: Color = (25, 35, 130)
PACGUM_COLOR: Color = (255, 220, 170)
SUPER_COLOR: Color = (255, 255, 255)
PLAYER_COLOR: Color = (255, 255, 0)
EDIBLE_COLOR: Color = (40, 40, 255)
FLASH_COLOR: Color = (240, 240, 240)

# direction -> angle on the screen (degrees) where Pac-Man looks
ANGLES: Dict[int, int] = {
    Maze.RIGHT: 0, Maze.TOP: 90, Maze.LEFT: 180, Maze.BUTTOM: 270,
}


class Renderer():
    """Draws one level. A new Renderer is made for each maze."""

    def __init__(
            self,
            matrix: List[List[int]],
            screen: pg.Surface,
            offset_x: int,
            offset_y: int,
            cell_size: int,
            player: Player
            ) -> None:
        """Keep what we need to draw.

        Args:
            matrix: the maze (numbers 0 to 15, see maze.py).
            screen: the window.
            offset_x: x of the left of the maze, in pixels.
            offset_y: y of the top of the maze, in pixels.
            cell_size: size of one cell, in pixels.
            player: the player (we read its position).
        """
        self.matrix: List[List[int]] = matrix
        self.screen = screen
        self.offset_x: int = offset_x
        self.offset_y: int = offset_y
        self.cell_size: int = cell_size
        self.player = player
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
        """Draw the walls (and the "42" cells in a different color)."""
        size = self.cell_size
        for row, line in enumerate(self.matrix):
            for col, cell in enumerate(line):
                x = self.offset_x + col * size
                y = self.offset_y + row * size

                if cell == 15:
                    pg.draw.rect(self.screen, CELL_42_COLOR,
                                 (x, y, size, size))
                # one bit = one wall: 1 top, 2 right, 4 bottom, 8 left
                if cell & Maze.TOP:
                    self.draw_wall((x, y), (x + size, y))
                if cell & Maze.RIGHT:
                    self.draw_wall((x + size, y), (x + size, y + size))
                if cell & Maze.BUTTOM:
                    self.draw_wall((x, y + size), (x + size, y + size))
                if cell & Maze.LEFT:
                    self.draw_wall((x, y), (x, y + size))

    def draw_wall(self, start: Tuple[int, int], end: Tuple[int, int]) -> None:
        """One piece of wall."""
        pg.draw.line(self.screen, WALL_COLOR, start, end,
                     self.wall_thickness)

    def cell_center(self, col: float, row: float) -> Tuple[int, int]:
        """Pixel position of the center of a cell (can be between 2 cells).

        Example: col=3.5 is half way between column 3 and column 4.
        """
        x = self.offset_x + col * self.cell_size + self.cell_size / 2
        y = self.offset_y + row * self.cell_size + self.cell_size / 2
        return round(x), round(y)

    def draw_pacgums(self, positions: Dict[Tuple[int, int], bool]) -> None:
        """Small dots. positions = {(column, row): still_there}."""
        radius = max(2, self.cell_size // 10)
        for (col, row), exist in positions.items():
            if exist:
                pg.draw.circle(self.screen, PACGUM_COLOR,
                               self.cell_center(col, row), radius)

    def draw_super_pacgums(self,
                           positions: Dict[Tuple[int, int], bool]) -> None:
        """Big dots. They blink like in the real game."""
        if pg.time.get_ticks() // 250 % 2 == 1:
            return
        radius = max(4, self.cell_size // 4)
        for (col, row), exist in positions.items():
            if exist:
                pg.draw.circle(self.screen, SUPER_COLOR,
                               self.cell_center(col, row), radius)

    def draw_player(self) -> None:
        """Pac-Man: a yellow circle with a mouth that opens and closes."""
        player = self.player
        # slide from the previous cell to the real cell
        progress = player.progress
        move_x = player.pos_x - player.previous_x
        move_y = player.pos_y - player.previous_y
        cx, cy = self.cell_center(player.previous_x + move_x * progress,
                                  player.previous_y + move_y * progress)
        radius = self.cell_size // 3 + 1

        if player.moving:
            opening = 8 + 37 * abs(math.sin(pg.time.get_ticks() / 90))
        else:
            opening = 25
        facing = ANGLES.get(player.direction or player.next_direction, 0)

        points: List[Tuple[float, float]] = [(cx, cy)]
        angle = facing + opening
        while angle <= facing + 360 - opening:
            rad = math.radians(angle)
            points.append((cx + radius * math.cos(rad),
                           cy - radius * math.sin(rad)))
            angle += 10
        pg.draw.polygon(self.screen, PLAYER_COLOR, points)

    def draw_ghosts(self, ghosts: List[Ghost]) -> None:
        """Draw the 4 ghosts, sliding from cell to cell."""
        for ghost in ghosts:
            progress = ghost.progress
            move_x = ghost.pos_x - ghost.previous_x
            move_y = ghost.pos_y - ghost.previous_y
            x, y = self.cell_center(ghost.previous_x + move_x * progress,
                                    ghost.previous_y + move_y * progress)
            self.draw_ghost(ghost, x, y)

    def draw_ghost(self, ghost: Ghost, x: int, y: int) -> None:
        """One ghost: a colored circle with a square bottom and two eyes."""
        r = self.cell_size // 3 + 1

        if ghost.state == EATEN:            # only the eyes, in the corner
            self.draw_eyes(x, y, r)
            return

        if ghost.edible:                    # blue, white when it blinks
            blink = ghost.flash and pg.time.get_ticks() // 200 % 2 == 0
            color: Color = FLASH_COLOR if blink else EDIBLE_COLOR
        else:
            real = pg.Color(ghost.color)
            color = (real.r, real.g, real.b)

        pg.draw.circle(self.screen, color, (x, y), r)
        pg.draw.rect(self.screen, color, (x - r, y, 2 * r, r))
        self.draw_eyes(x, y, r)

    def draw_eyes(self, x: int, y: int, r: int) -> None:
        """Two white eyes."""
        for dx in (-r // 2, r // 2):
            pg.draw.circle(self.screen, "white", (x + dx, y - r // 4),
                           max(2, r // 3))
