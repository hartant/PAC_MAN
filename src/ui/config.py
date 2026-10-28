"""Read config.json and give the game safe values.

Rules:
- Lines starting with '#' are comments and are ignored.
- A missing key        -> default value (silent).
- A wrong value        -> warning + default value (the game goes on).
- A broken file        -> warning + all default values (the game goes on).
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Any

MIN_MAZE_SIZE = 5
MAX_MAZE_SIZE = 50


@dataclass
class LevelConfig:
    """Size of the maze of one level."""

    width: int = 15
    height: int = 15


def _default_levels() -> list[LevelConfig]:
    return [LevelConfig(15, 15)]


@dataclass
class GameConfig:
    """All game settings. Names are the same as the keys in config.json."""

    highscore_filename: str = "highscores.json"
    lives: int = 3
    pacgum: int = 42
    points_per_pacgum: int = 10
    points_per_super_pacgum: int = 50
    points_per_ghost: int = 200
    seed: int = 42
    level_max_time: int = 90
    levels: list[LevelConfig] = field(default_factory=_default_levels)


def _read_int(data: dict[str, Any], key: str, default: int,
              minimum: int, maximum: int) -> int:
    """Return data[key] if it is a whole number in [minimum, maximum].

    Otherwise log a warning and return the default.
    A missing key gives the default without any warning.
    """
    if key not in data:
        return default
    value = data[key]
    # bool is a kind of int in Python, so True would pass: refuse it.
    if isinstance(value, bool) or not isinstance(value, int):
        logging.warning("Config: '%s' must be a whole number (got %r). "
                        "Using default: %d", key, value, default)
        return default
    if not minimum <= value <= maximum:
        logging.warning("Config: '%s' must be between %d and %d (got %d). "
                        "Using default: %d", key, minimum, maximum,
                        value, default)
        return default
    return value


def _read_filename(data: dict[str, Any], default: str) -> str:
    """Return 'highscore_filename' if it is a non-empty text."""
    if "highscore_filename" not in data:
        return default
    value = data["highscore_filename"]
    if not isinstance(value, str) or not value.strip():
        logging.warning("Config: 'highscore_filename' must be a non-empty "
                        "text (got %r). Using default: %s", value, default)
        return default
    return value.strip()


def _read_levels(data: dict[str, Any]) -> list[LevelConfig]:
    """Return the valid levels. Bad levels are skipped with a warning."""
    if "levels" not in data:
        return _default_levels()
    raw = data["levels"]
    if not isinstance(raw, list):
        logging.warning("Config: 'levels' must be a list (got %r). "
                        "Using default levels.", raw)
        return _default_levels()

    levels: list[LevelConfig] = []
    for index, item in enumerate(raw, start=1):
        if not isinstance(item, dict):
            logging.warning("Config: level %d must be an object with "
                            "'width' and 'height'. Level skipped.", index)
            continue
        width = _read_int(item, "width", 0, MIN_MAZE_SIZE, MAX_MAZE_SIZE)
        height = _read_int(item, "height", 0, MIN_MAZE_SIZE, MAX_MAZE_SIZE)
        if width == 0 or height == 0:
            logging.warning("Config: level %d needs a valid 'width' and "
                            "'height' (%d to %d). Level skipped.",
                            index, MIN_MAZE_SIZE, MAX_MAZE_SIZE)
            continue
        levels.append(LevelConfig(width, height))

    if not levels:
        logging.warning("Config: no valid level found. "
                        "Using default levels.")
        return _default_levels()
    return levels


def load_config(filepath: str) -> GameConfig:
    """Load the configuration file. Never raises: errors give defaults."""
    config = GameConfig()

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
        # Drop comment lines (a '#' after some spaces counts too).
        clean = [ln for ln in lines if not ln.strip().startswith("#")]
        data = json.loads("".join(clean))
    except FileNotFoundError:
        logging.error("Config file '%s' not found. Using default settings.",
                      filepath)
        return config
    except json.JSONDecodeError as err:
        logging.error("Config file is not valid JSON (%s). "
                      "Using default settings.", err)
        return config
    except (OSError, ValueError) as err:
        logging.error("Cannot read config file (%s). "
                      "Using default settings.", err)
        return config

    if not isinstance(data, dict):
        logging.error("Config file must contain a JSON object { ... }. "
                      "Using default settings.")
        return config

    known = set(vars(config))
    for key in data:
        if key not in known:
            logging.warning("Config: unknown key '%s' ignored.", key)

    config.highscore_filename = _read_filename(
        data, config.highscore_filename)
    config.lives = _read_int(data, "lives", config.lives, 1, 99)
    config.pacgum = _read_int(data, "pacgum", config.pacgum, 1, 10000)
    config.points_per_pacgum = _read_int(
        data, "points_per_pacgum", config.points_per_pacgum, 0, 100000)
    config.points_per_super_pacgum = _read_int(
        data, "points_per_super_pacgum", config.points_per_super_pacgum,
        0, 100000)
    config.points_per_ghost = _read_int(
        data, "points_per_ghost", config.points_per_ghost, 0, 100000)
    config.seed = _read_int(data, "seed", config.seed, -2**31, 2**31 - 1)
    config.level_max_time = _read_int(
        data, "level_max_time", config.level_max_time, 10, 3600)
    config.levels = _read_levels(data)
    return config