"""The numbers shown by the HUD. The game engine fills them each frame."""

from dataclasses import dataclass


@dataclass
class GameState:
    """What the player needs to see during the game."""

    score: int = 0
    lives: int = 3
    level: int = 1
    level_count: int = 10
    time_left: int = 90
    power_left: int = 0         # seconds of super mode left (0 = no power)
    cheat_text: str = ""        # empty when the cheat mode is off
