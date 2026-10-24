from src.logic.maze import Maze
from typing import List, Tuple


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
        self.ui_x: int = pos_x
        self.ui_y: int = pos_y

    def move(self, maze: Maze, direction: int) -> None:
        if not maze.can_move(self.pos_y, self.pos_x, direction):
            return

        if direction == Maze.TOP:
            self.pos_y -= 1

        elif direction == Maze.BUTTOM:
            self.pos_y += 1

        elif direction == Maze.LEFT:
            self.pos_x -= 1

        elif direction == Maze.RIGHT:
            self.pos_x += 1

    def return_enter(self):
        """default position"""
        # we need to check the
        self.pos_x = self.position[0]
        self.pos_y = self.position[1]


class Ghost(Father):
    def __init__(self, position, direction, speed):
        super().__init__(position, direction, speed)
