from src.logic.father import Player
from typing import List, Dict


class Pacgum():
    def __init__(self, matrix: List[List[int]], player: Player) -> None:
        self.matrix: List[List[int]] = matrix
        self.player = player

        self.pacgums_point: int = 5
        self.super_pacgums_point: int = 10
        self.pacgums_state: Dict = {}
        self.activate()

    def activate(self) -> None:
        self.pacgum_state()

    def pacgum_state(self) -> None:
        """put dots in the corridors."""
        rows = len(self.matrix)
        cols = len(self.matrix[0])
        corners = {(0, 0), (cols - 1, 0), (0, rows - 1), (cols - 1, rows - 1)}

        self.pacgums_state: Dict = {}
        for row in range(rows):
            for col in range(cols):
                closed = self.matrix[row][col] == 15       # the "42" cells
                if not closed and (col, row) not in corners:
                    self.pacgums_state.update({(col, row): True})

    def eat_pacgum(self) -> None:
        if self.pacgums_state.get((self.player.pos_x, self.player.pos_y)):
            self.pacgums_state.update({(self.player.pos_x, self.player.pos_y): False})
            self.player.update_score(self.pacgums_point)
            print(f"=========== update_score: {self.player.score}")

    def reset(self) -> None:
        # we !!!!!!!!!!!!!!!111
        rows = len(self.matrix)
        cols = len(self.matrix[0])
        corners = {(0, 0), (cols - 1, 0), (0, rows - 1), (cols - 1, rows - 1)}

        for row in range(rows):
            for col in range(cols):
                closed = self.matrix[row][col] == 15       # the "42" cells
                if not closed and (col, row) not in corners:
                    self.pacgums_state.update({(col, row): True})

    def super_pacgum_state(self) -> None:
        pass
