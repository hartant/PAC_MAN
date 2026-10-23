from dataclasses import dataclass, field


@dataclass
class LevelConfig:
    """Settings for one level."""
    width: int = 15
    height: int = 15


@dataclass
class GameConfig:
    """All game settings, with safe default values."""
    highscore_filename: str = "highscores.json"
    lives: int = 3
    points_per_pacgum: int = 10
    points_per_super_pacgum: int = 50
    points_per_ghost: int = 200
    seed: int = 42
    level_max_time: int = 90
    levels: list[LevelConfig] = field(default_factory=list)