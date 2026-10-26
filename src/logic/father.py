from src.logic.maze import Maze
from typing import List, Tuple
from collections import deque
import random


class Father:
    def __init__(self, maze: List[List[int]]) -> None:
        self.maze: List[List[int]] = maze
        self.position: Tuple[int]
        self.direction: int
        self.speed: int

    def set_position(self):
        pass


# class Player(Father):
#     def __init__(self, position: Tuple[int],
#                  direction,
#                  speed: int,
#                  name: str):
#         super().__init__(position, direction, speed)
#         self.name: str = name
#         self.score: int


class Player():
    def __init__(self,
                 position: Tuple[int],
                 pos_x: int,
                 pos_y: int,
                 name: str) -> None:
        self.position: Tuple[int] = position
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.name: str = name
        self.speed: int = 5
        self.score: int = 0
        self.direction: int
        self.next_direction: int = 0
        self.lives: int = 3

    def move(self, maze: Maze) -> None:
        if not maze.can_move(self.pos_y, self.pos_x, self.next_direction):
            return

        if self.next_direction == Maze.TOP:
            self.pos_y -= 1

        elif self.next_direction == Maze.BUTTOM:
            self.pos_y += 1

        elif self.next_direction == Maze.LEFT:
            self.pos_x -= 1

        elif self.next_direction == Maze.RIGHT:
            self.pos_x += 1

    def set_direction(self, direction: int) -> None:
        if direction in (
            Maze.TOP,
            Maze.BUTTOM,
            Maze.LEFT,
            Maze.RIGHT
        ):
            self.next_direction = direction

    def return_enter(self):
        """default position"""
        # we need to check the
        self.pos_x = self.position[0]
        self.pos_y = self.position[1]


class Ghost():
    DIRECTIONS = (
            Maze.TOP,
            Maze.RIGHT,
            Maze.BUTTOM,
            Maze.LEFT,
        )

    OFFSETS = {
            Maze.TOP: (-1, 0),
            Maze.RIGHT: (0, 1),
            Maze.BUTTOM: (1, 0),
            Maze.LEFT: (0, -1),
        }

    def __init__(self,
                 pos_x: int,
                 pos_y: int,
                 color: str,
                 maze: Maze) -> None:
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.color = color
        self.maze = maze
        self.direction = 0

        self.spawn_x = pos_x
        self.spawn_y = pos_y

        self.previous_x = pos_x
        self.previous_y = pos_y

    def move(self, player_row: int, player_col: int) -> None:
        direction = self.find_direction(
            self.pos_y,
            self.pos_x,
            player_row,
            player_col
        )

        if direction == 0:
            return

        if not self.maze.can_move(
            self.pos_y,
            self.pos_x,
            direction
        ):
            return
        self.previous_x = self.pos_x
        self.previous_y = self.pos_y

        dr, dc = self.OFFSETS[direction]

        self.pos_y += dr
        self.pos_x += dc

        self.direction = direction

    def find_direction(
        self,
        ghost_row: int,
        ghost_col: int,
        player_row: int,
        player_col: int,
    ) -> int:
        """Return first direction of the shortest path."""
        # this more efficent than return all path for every time

        start = (ghost_row, ghost_col)
        target = (player_row, player_col)

        # random crazy !!
        k = [1, 0, 0]
        directions = [1, 2, 4, 8]
        if random.choice(k) == 1:
            return random.choice(directions)

        if start == target:
            return 0

        queue = deque([(start, 0)])
        visited = {start}

        while queue:
            (row, col), first_direction = queue.popleft()

            for direction in self.DIRECTIONS:
                if not self.maze.can_move(row, col, direction):
                    continue

                dr, dc = self.OFFSETS[direction]
                next_pos = (row + dr, col + dc)

                if next_pos in visited:
                    continue

                next_direction = (
                    first_direction
                    if first_direction != 0
                    else direction
                )

                if next_pos == target:
                    return next_direction

                visited.add(next_pos)
                queue.append((next_pos, next_direction))
        return 0
