"""Pacgums (small dots) and super-pacgums (big dots in the 4 corners).

A dot is stored as {(column, row): True}. True = still there, False = eaten.
"""

from typing import Dict, List, Tuple

from src.logic.father import Player
from src.logic.maze import Maze

Position = Tuple[int, int]      # (column, row)

NOTHING = ""
PACGUM = "pacgum"
SUPER = "super"


class Pacgum:
    """All the dots of one level and the power (super mode) timer."""

    def __init__(self,
                 maze: Maze,
                 player: Player,
                 pacgums_point: int = 10,
                 pacgums: int = 42,
                 super_pacgums_point: int = 50,
                 supermode_time: float = 8.0) -> None:
        """Put the dots in the maze.

        Args:
            maze: the maze of the level.
            player: the player (it gets the points).
            pacgums_point: points for a pacgum.
            super_pacgums_point: points for a super-pacgum.
            supermode_time: seconds the ghosts stay edible.
        """
        self.maze: Maze = maze
        self.player: Player = player
        self.pacgums_point: int = pacgums_point
        self.pacgums: int = pacgums
        self.super_pacgums_point: int = super_pacgums_point
        self.supermode_time: float = supermode_time

        self.pacgums_state: Dict[Position, bool] = {}
        self.super_pacgums_state: Dict[Position, bool] = {}
        self.supermode: bool = False
        self.supermode_left: float = 0.0
        self.activate()

    def activate(self) -> None:
        """Put all the dots back (new level)."""
        self.pacgum_state()
        self.super_pacgum_state()
        self.supermode = False
        self.supermode_left = 0.0

    def pacgum_state(self) -> None:
        """Put the small dots in the corridors, spread over the whole maze.

        Not in the "42" cells, not in the corners (big dots there) and not
        in the cell where the player starts. `pacgums` (config key
        "pacgum") is the maximum number of dots: if the maze has more free
        cells, the dots are taken at regular steps so they cover the whole
        maze, not only its top rows.
        """
        corners = {(col, row) for row, col in self.maze.corners()}
        start = (self.player.spawn_x, self.player.spawn_y)
        free: List[Position] = [
            (col, row)
            for row, col in self.maze.free_cells()
            if (col, row) not in corners and (col, row) != start
        ]
        count = min(self.pacgums, len(free))
        chosen: List[Position] = []
        if count == len(free):
            chosen = free
        elif count > 0:
            step = len(free) / count
            chosen = [free[int(i * step)] for i in range(count)]
        self.pacgums_state = {cell: True for cell in chosen}

    def super_pacgum_state(self) -> None:
        """Put a big dot in each corner."""
        self.super_pacgums_state = {
            (col, row): True for row, col in self.maze.corners()
        }

    def eat_pacgum(self) -> str:
        """Eat what is under the player.

        Returns:
            "pacgum", "super" or "" (nothing here).
        """
        here = (self.player.pos_x, self.player.pos_y)
        if self.pacgums_state.get(here):
            self.pacgums_state[here] = False
            self.player.update_score(self.pacgums_point)
            return PACGUM
        if self.super_pacgums_state.get(here):
            self.super_pacgums_state[here] = False
            self.player.update_score(self.super_pacgums_point)
            self.start_supermode()
            return SUPER
        return NOTHING

    def start_supermode(self) -> None:
        """The ghosts can be eaten for `supermode_time` seconds."""
        self.supermode = True
        self.supermode_left = self.supermode_time

    def update(self, dt: float) -> None:
        """Count the super mode time down (not called while paused)."""
        if not self.supermode:
            return
        self.supermode_left -= dt
        if self.supermode_left <= 0:
            self.supermode = False
            self.supermode_left = 0.0

    def remaining(self) -> int:
        """Number of dots (small and big) still to eat."""
        small = sum(1 for left in self.pacgums_state.values() if left)
        big = sum(1 for left in self.super_pacgums_state.values() if left)
        return small + big

    def all_eaten(self) -> bool:
        """True when the level is won."""
        return self.remaining() == 0
