from typing import List


class Maze:
    TOP = 1
    RIGHT = 2
    BUTTOM = 4
    LEFT = 8

    def __init__(self, matrix: List[List[int]]) -> None:
        self.matrix: List[List[int]] = matrix

    def can_move(
        self,
        row: int,
        col: int,
        direction: int,
    ) -> bool:
        rows = len(self.matrix)
        cols = len(self.matrix[0])

        if not (0 <= row < rows and 0 <= col < cols):
            return False

        movements = {
            self.TOP: (-1, 0, self.BUTTOM),
            self.RIGHT: (0, 1, self.LEFT),
            self.BUTTOM: (1, 0, self.TOP),
            self.LEFT: (0, -1, self.RIGHT),
        }

        if direction not in movements:
            return False

        dr, dc, opposite = movements[direction]

        new_row = row + dr
        new_col = col + dc

        if not (0 <= new_row < rows and 0 <= new_col < cols):
            return False

        # Check wall in current cell
        if self.matrix[row][col] & direction:
            return False

        # Check opposite wall in destination cell
        if self.matrix[new_row][new_col] & opposite:
            return False

        return True
