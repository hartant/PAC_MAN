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
                 name: str):
        self.position = position
        self.name: str = name
        self.speed: int
        self.score: int


class Ghost(Father):
    def __init__(self, position, direction, speed):
        super().__init__(position, direction, speed)
