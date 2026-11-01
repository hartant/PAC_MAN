"""Maze rules (where can we walk?) and the loader of the A-Maze-ing package.

Each cell of the matrix is a number from 0 to 15. Each bit is a wall:
TOP = 1, RIGHT = 2, BUTTOM = 4, LEFT = 8. A cell worth 15 is closed on the
four sides: it is a part of the "42" drawing in the middle of the maze.
"""

import importlib
import random
import sys
from collections import deque
from typing import Any, Deque, Dict, List, Optional, Tuple

GENERATE_TRIES = 5

Cell = Tuple[int, int]          # (row, col)


class MazeError(Exception):
    """The maze could not be generated."""


class Maze:
    """Knows the walls of one level. Used by the player and the ghosts."""

    TOP = 1
    RIGHT = 2
    BUTTOM = 4
    LEFT = 8

    # direction -> (row change, column change)
    OFFSETS: Dict[int, Cell] = {
        TOP: (-1, 0),
        RIGHT: (0, 1),
        BUTTOM: (1, 0),
        LEFT: (0, -1),
    }
    OPPOSITE: Dict[int, int] = {
        TOP: BUTTOM,
        RIGHT: LEFT,
        BUTTOM: TOP,
        LEFT: RIGHT,
    }

    def __init__(self, matrix: List[List[int]]) -> None:
        """Keep the matrix (a list of rows) of the level."""
        self.matrix: List[List[int]] = matrix
        self.rows: int = len(matrix)
        self.cols: int = len(matrix[0])
        self._distance_cache: Dict[Cell, Dict[Cell, int]] = {}

    def can_move(self, row: int, col: int, direction: int) -> bool:
        """Say if we can leave cell (row, col) in this direction."""
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return False
        if direction not in self.OFFSETS:
            return False

        d_row, d_col = self.OFFSETS[direction]
        new_row = row + d_row
        new_col = col + d_col
        if not (0 <= new_row < self.rows and 0 <= new_col < self.cols):
            return False

        # wall in the current cell
        if self.matrix[row][col] & direction:
            return False
        # wall in the cell we want to enter
        if self.matrix[new_row][new_col] & self.OPPOSITE[direction]:
            return False
        return True

    def is_closed(self, row: int, col: int) -> bool:
        """True for the closed cells of the "42" drawing."""
        return self.matrix[row][col] == 15

    def free_cells(self) -> List[Cell]:
        """All the cells where somebody can stand (not the "42" ones)."""
        return [(row, col)
                for row in range(self.rows)
                for col in range(self.cols)
                if not self.is_closed(row, col)]

    def start_cell(self) -> Cell:
        """The cell of the player: the middle, or the nearest free cell.

        With some sizes the middle cell is a part of the "42" drawing.
        """
        mid_row = self.rows // 2
        mid_col = self.cols // 2
        return min(self.free_cells(),
                   key=lambda cell: (abs(cell[0] - mid_row)
                                     + abs(cell[1] - mid_col), cell))

    def corners(self) -> List[Cell]:
        """The 4 corners as (row, col)."""
        last_row = self.rows - 1
        last_col = self.cols - 1
        return [(0, 0), (last_row, 0), (0, last_col), (last_row, last_col)]

    def distances(self, row: int, col: int) -> Dict[Cell, int]:
        """Walking distance from (row, col) to every reachable cell (BFS).

        The result is kept in a cache: the maze never changes in a level.
        """
        start = (row, col)
        if start in self._distance_cache:
            return self._distance_cache[start]

        result: Dict[Cell, int] = {start: 0}
        queue: Deque[Cell] = deque([start])
        while queue:
            cur_row, cur_col = queue.popleft()
            for direction, (d_row, d_col) in self.OFFSETS.items():
                if not self.can_move(cur_row, cur_col, direction):
                    continue
                nxt = (cur_row + d_row, cur_col + d_col)
                if nxt not in result:
                    result[nxt] = result[(cur_row, cur_col)] + 1
                    queue.append(nxt)
        self._distance_cache[start] = result
        return result

    def cell_ahead(self, row: int, col: int, direction: int,
                   steps: int) -> Cell:
        """Walk `steps` cells in a direction. Stop in front of a wall."""
        for _ in range(steps):
            if not self.can_move(row, col, direction):
                break
            d_row, d_col = self.OFFSETS[direction]
            row += d_row
            col += d_col
        return (row, col)

    @staticmethod
    def load_generator() -> Any:
        """Return the MazeGenerator class of the A-Maze-ing package.

        Raises:
            MazeError: if the package is not installed (no traceback).
        """
        try:
            package = importlib.import_module("mazegenerator")
            return getattr(package, "MazeGenerator")
        except (ImportError, AttributeError) as err:
            raise MazeError("the 'mazegenerator' package is not installed "
                            f"(run: make install) - {err}") from err

    @staticmethod
    def generate(width: int, height: int,
                 seed: Optional[int] = None) -> List[List[int]]:
        """Ask the A-Maze-ing package for a maze (it is used as it is).

        Args:
            width: number of columns.
            height: number of rows.
            seed: a seed > 0 always gives the same maze.
                None gives a random one.

        Returns:
            The matrix of the maze (list of rows of numbers 0 to 15).

        Raises:
            MazeError: if the package is missing or fails 5 times.
        """
        maze_generator = Maze.load_generator()
        last_error = "unusable maze"
        # the package builds the maze with a recursive function
        old_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(max(old_limit, width * height * 4 + 1000))
        try:
            for attempt in range(GENERATE_TRIES):
                try_seed = seed or 0
                if attempt > 0:         # the asked seed failed: random one
                    try_seed = random.randint(1, 2**31 - 1)
                try:
                    generator = maze_generator(size=(width, height),
                                               perfect=False, seed=try_seed)
                    matrix = [list(row) for row in generator.maze]
                except Exception as err:    # not our package: catch all
                    last_error = f"{type(err).__name__}: {err}"
                    continue
                if Maze.is_usable(matrix, width, height):
                    return matrix
        finally:
            sys.setrecursionlimit(old_limit)
        raise MazeError(f"Cannot generate a {width}x{height} maze "
                        f"({last_error})")

    @staticmethod
    def is_usable(matrix: Any, width: int, height: int) -> bool:
        """Check the result of the package: size, values, all cells linked."""
        if not isinstance(matrix, list) or len(matrix) != height:
            return False
        for row in matrix:
            if not isinstance(row, list) or len(row) != width:
                return False
            for value in row:
                if not isinstance(value, int) or not 0 <= value <= 15:
                    return False
        maze = Maze(matrix)
        free = maze.free_cells()
        if not free:
            return False
        reachable = maze.distances(*maze.start_cell())
        return len(reachable) == len(free)
