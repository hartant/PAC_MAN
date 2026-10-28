from src.logic.father import Player, Ghost
from typing import List, Dict
import time


class Pacgum():
    def __init__(self,
                 matrix: List[List[int]],
                 player: Player,
                 ghosts: List[Ghost],
                 cheat_mode: List[bool]) -> None:
        self.matrix: List[List[int]] = matrix
        self.player: Player = player
        self.cheat_mode: List[bool] = cheat_mode

        self.pacgums_point: int = 5
        self.super_pacgums_point: int = 10
        self.pacgums_state: Dict = {}
        self.super_pacgums_state: Dict = {}
        self.supermode_time: int = 10
        self.supermode: bool = False
        self.start: float = 0
        self.activate()

    def activate(self) -> None:
        self.pacgum_state()
        self.super_pacgum_state()

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
        # eat pacgum
        if self.pacgums_state.get((self.player.pos_x, self.player.pos_y)):
            self.pacgums_state.update(
                {(self.player.pos_x, self.player.pos_y): False}
            )
            self.player.update_score(self.pacgums_point)
            print(f"=========== update_score: {self.player.score}")

        # eat super pacgum
        if self.super_pacgums_state.get((self.player.pos_x, self.player.pos_y)):
            print("== eat spacgum")
            self.super_pacgums_state.update(
                {(self.player.pos_x, self.player.pos_y): False}
                )
            self.player.update_score(self.super_pacgums_point)
            # activate superpacgum
            self.start = time.monotonic()
            self.cheat_mode[0] = True
            self.supermode = True

        elapsed = time.monotonic() - self.start
        if elapsed >= self.supermode_time:
            self.supermode = False
            self.cheat_mode[0] = False

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
        """put large dots in the corridors. :)"""
        rows = len(self.matrix)
        cols = len(self.matrix[0])
        self.super_pacgums_state: Dict = {
            (0, 0): True,
            (cols - 1, 0): True,
            (0, rows - 1): True,
            (cols - 1, rows - 1): True
        }

    def super_effect(self, start: float) -> None:   # can integreat cheatmode for save time !!
        self.cheat_mode[0] = True
        self.supermode = True

        elapsed = time.monotonic() - start
        print(f"mode: {elapsed} - {start} // ")
        if elapsed >= self.supermode_time:
            self.supermode = False
            self.cheat_mode[0] = False
            elapsed = 0
            print("mode_: 0")

    # def super_effect(self, start: float) -> None:   # can integreat cheatmode for save time !!
    #     self.cheat_mode[0] = True
    #     self.supermode = True
    #     # start = time.monotonic()

    #     elapsed = time.monotonic() - start
    #     print(f"mode: {elapsed} - {start} // ")
    #     if elapsed >= self.supermode_time:
    #         self.supermode = False
    #         self.cheat_mode[0] = False
    #         elapsed = 0
    #         print("mode_: 0")

# import time

# start = time.monotonic()

# elapsed = time.monotonic() - start

# print(elapsed)

# if time.monotonic() - super_start >= super_duration:
#     self.player.super_mode = False
