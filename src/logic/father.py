"""The characters that move in the maze: the Player and the Ghosts.

Positions are in cells: pos_x is the column, pos_y is the row.
A character goes to a new cell every `step_time` seconds. The previous cell
is kept, so the screen can slide the character between the two cells.
"""

import random
from typing import List

from src.logic.maze import Cell, Maze

NORMAL = "normal"       # chases the player
EDIBLE = "edible"       # blue, runs away, can be eaten
EATEN = "eaten"         # waits in its corner before coming back


class Player:
    """Pac-Man: goes straight, and turns when the player asked for it."""

    def __init__(self, pos_x: int, pos_y: int, lives: int = 3) -> None:
        """Put the player in a cell (pos_x = column, pos_y = row)."""
        self.spawn_x: int = pos_x
        self.spawn_y: int = pos_y
        self.pos_x: int = pos_x
        self.pos_y: int = pos_y
        self.previous_x: int = pos_x
        self.previous_y: int = pos_y

        self.direction: int = 0         # direction we are really going
        self.next_direction: int = 0    # direction asked with the keyboard
        self.moving: bool = False

        self.lives: int = lives
        self.score: int = 0

        self.timer: float = 0.0
        self.step_time: float = 0.12

    @property
    def progress(self) -> float:
        """From 0 to 1: how far we are between the 2 cells (for drawing)."""
        if not self.moving:
            return 1.0
        return min(1.0, self.timer / self.step_time)

    def set_direction(self, direction: int) -> None:
        """Remember the direction asked by the player (key pressed)."""
        if direction in Maze.OFFSETS:
            self.next_direction = direction

    def update(self, dt: float, maze: Maze, step_time: float) -> bool:
        """Add the time that passed. Returns True if we changed of cell."""
        self.step_time = step_time
        self.timer += dt
        if self.timer < step_time:
            return False
        self.timer = 0.0
        self.moving = self.step(maze)
        return self.moving

    def step(self, maze: Maze) -> bool:
        """Go to the next cell: the asked direction first, else straight."""
        self.previous_x = self.pos_x
        self.previous_y = self.pos_y
        for direction in (self.next_direction, self.direction):
            if direction and maze.can_move(self.pos_y, self.pos_x, direction):
                d_row, d_col = Maze.OFFSETS[direction]
                self.pos_y += d_row
                self.pos_x += d_col
                self.direction = direction
                return True
        return False

    def reset_position(self) -> None:
        """Back to the start cell (after a lost life or a new level)."""
        self.pos_x = self.previous_x = self.spawn_x
        self.pos_y = self.previous_y = self.spawn_y
        self.direction = 0
        self.next_direction = 0
        self.moving = False
        self.timer = 0.0

    def new_level(self, pos_x: int, pos_y: int) -> None:
        """Change the start cell for a new maze. Score and lives stay."""
        self.spawn_x = pos_x
        self.spawn_y = pos_y
        self.reset_position()

    def update_score(self, value: int) -> None:
        """Add points (the score never goes down)."""
        if value > 0:
            self.score += value


class Ghost:
    """A ghost. Each ghost has its own way to chase the player.

    - "chase" (red): goes straight to the player.
    - "ambush" (pink): goes 4 cells in front of the player.
    - "random" (cyan): goes to a random place, changed every 20 steps.
    - "shy" (orange): chases from far, runs to its corner when too close.

    A ghost never turns back by itself (like in the real game). When it is
    edible (blue) it runs away from the player.
    """

    def __init__(self, pos_x: int, pos_y: int, color: str, maze: Maze,
                 personality: str = "chase") -> None:
        """Create a ghost in its corner.

        Args:
            pos_x: column of the corner.
            pos_y: row of the corner.
            color: pygame color name ("red", "pink", ...).
            maze: the maze of the level.
            personality: "chase", "ambush", "random" or "shy".
        """
        self.spawn_x: int = pos_x
        self.spawn_y: int = pos_y
        self.pos_x: int = pos_x
        self.pos_y: int = pos_y
        self.previous_x: int = pos_x
        self.previous_y: int = pos_y
        self.color: str = color
        self.maze: Maze = maze
        self.personality: str = personality
        self.rng: random.Random = random.Random()

        self.direction: int = 0
        self.state: str = NORMAL
        self.flash: bool = False        # blinks at the end of the power
        self.respawn_left: float = 0.0
        self.timer: float = 0.0
        self.step_time: float = 0.2

        self.random_target: Cell = (pos_y, pos_x)   # for "random"
        self.steps_left: int = 0

    @property
    def edible(self) -> bool:
        """True while the player can eat this ghost."""
        return self.state == EDIBLE

    @property
    def progress(self) -> float:
        """From 0 to 1: how far we are between the 2 cells (for drawing)."""
        if self.state == EATEN:
            return 1.0
        return min(1.0, self.timer / self.step_time)

    def reset(self) -> None:
        """Back to the corner, normal."""
        self.pos_x = self.previous_x = self.spawn_x
        self.pos_y = self.previous_y = self.spawn_y
        self.direction = 0
        self.state = NORMAL
        self.flash = False
        self.respawn_left = 0.0
        self.timer = 0.0

    def set_edible(self, value: bool) -> None:
        """Start or stop the edible mode (an eaten ghost is not changed)."""
        if self.state == EATEN:
            return
        self.state = EDIBLE if value else NORMAL
        self.flash = False

    def eat(self, respawn_time: float) -> None:
        """The player ate us: back to the corner, wait, then come back."""
        self.reset()
        self.state = EATEN
        self.respawn_left = respawn_time

    def update(self, dt: float, player: Player, step_time: float) -> None:
        """Add the time that passed and move if it is time."""
        if self.state == EATEN:
            self.respawn_left -= dt
            if self.respawn_left <= 0:
                self.state = NORMAL
            return

        self.step_time = step_time
        self.timer += dt
        if self.timer >= step_time:
            self.timer = 0.0
            self.step(player)

    def step(self, player: Player) -> None:
        """Choose a direction and go to the next cell."""
        self.previous_x = self.pos_x
        self.previous_y = self.pos_y
        direction = self.choose_direction(player)
        if direction == 0:
            return
        d_row, d_col = Maze.OFFSETS[direction]
        self.pos_y += d_row
        self.pos_x += d_col
        self.direction = direction

    def next_cell(self, direction: int) -> Cell:
        """The cell we reach if we go in this direction."""
        d_row, d_col = Maze.OFFSETS[direction]
        return (self.pos_y + d_row, self.pos_x + d_col)

    def choose_direction(self, player: Player) -> int:
        """Pick the best direction (0 if we are stuck).

        Maze.distances gives the walking distance from the target to every
        cell. We take the neighbour cell that is the closest to the target
        (or the farthest from the player when we are edible).
        """
        options = [d for d in Maze.OFFSETS
                   if self.maze.can_move(self.pos_y, self.pos_x, d)]
        if not options:
            return 0

        # do not turn back, except in a dead end
        back = Maze.OPPOSITE.get(self.direction, 0)
        if len(options) > 1 and back in options:
            options.remove(back)

        if self.state == EDIBLE:
            dist = self.maze.distances(player.pos_y, player.pos_x)
            scores = {d: dist.get(self.next_cell(d), 0) for d in options}
            best = max(scores.values())
        else:
            target = self.get_target(player)
            dist = self.maze.distances(target[0], target[1])
            scores = {d: dist.get(self.next_cell(d), 9999) for d in options}
            best = min(scores.values())
        return self.rng.choice([d for d in options if scores[d] == best])

    def get_target(self, player: Player) -> Cell:
        """The cell (row, col) this ghost wants to reach."""
        if self.personality == "ambush":
            return self.maze.cell_ahead(player.pos_y, player.pos_x,
                                        player.direction, 4)

        if self.personality == "random":
            if self.steps_left <= 0:
                self.random_target = self.rng.choice(self.maze.free_cells())
                self.steps_left = 20
            self.steps_left -= 1
            return self.random_target

        if self.personality == "shy":
            dist = self.maze.distances(player.pos_y, player.pos_x)
            if dist.get((self.pos_y, self.pos_x), 0) <= 6:
                return (self.spawn_y, self.spawn_x)     # too close: go home

        return (player.pos_y, player.pos_x)             # "chase"


def make_ghosts(maze: Maze) -> List[Ghost]:
    """The 4 ghosts, one in each corner."""
    styles = [("red", "chase"), ("pink", "ambush"),
              ("cyan", "random"), ("orange", "shy")]
    ghosts = []
    for (row, col), (color, personality) in zip(maze.corners(), styles):
        ghosts.append(Ghost(col, row, color, maze, personality))
    return ghosts
