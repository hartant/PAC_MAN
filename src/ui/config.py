"""Read config.json and give the game safe values.

Rules:
- Lines starting with '#' are comments and are ignored
  (C '/* */' and C++ '//' comments are accepted too).
- A missing key        -> default value (silent).
- A wrong value        -> warning + default value (the game goes on).
- A broken file        -> warning + all default values (the game goes on).
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Any

MIN_MAZE_SIZE = 5
MAX_MAZE_SIZE = 30
# default maze sizes of the 10 levels (a bigger maze needs more time)
DEFAULT_SIZES = (15, 15, 15, 17, 17, 17, 17, 19, 19, 19)


def strip_comments(text: str) -> str:
    """Remove the comments from a JSON text.

    - Lines starting with '#' (spaces before are allowed).
    - C++ comments: '//' until the end of the line.
    - C comments: '/* ... */', on one or more lines.
    Text inside "strings" is never touched.
    """
    out: list[str] = []
    i = 0
    in_string = False
    at_line_start = True
    while i < len(text):
        ch = text[i]
        if in_string:
            out.append(ch)
            if ch == "\\" and i + 1 < len(text):
                out.append(text[i + 1])
                i += 1
            elif ch == '"':
                in_string = False
            i += 1
            continue
        if at_line_start and ch == "#":
            end = text.find("\n", i)
            i = len(text) if end == -1 else end
            continue
        if text.startswith("//", i):
            end = text.find("\n", i)
            i = len(text) if end == -1 else end
            continue
        if text.startswith("/*", i):
            end = text.find("*/", i + 2)
            if end == -1:
                raise ValueError("comment '/*' is never closed")
            # keep the new lines so JSON errors give the right line number
            out.append("\n" * text.count("\n", i, end))
            i = end + 2
            continue
        if ch == '"':
            in_string = True
        if ch == "\n":
            at_line_start = True
        elif not ch.isspace():
            at_line_start = False
        out.append(ch)
        i += 1
    return "".join(out)


@dataclass
class LevelConfig:
    """Size of the maze of one level."""

    width: int = 15
    height: int = 15

    @staticmethod
    def default_levels() -> list["LevelConfig"]:
        """10 levels, the maze grows a little as we go (15 -> 19)."""
        return [LevelConfig(size, size) for size in DEFAULT_SIZES]


class ConfigParser:
    """Checks one key of the JSON data. A wrong value gives the default."""

    @staticmethod
    def read_int(data: dict[str, Any], key: str, default: int,
                 minimum: int, maximum: int) -> int:
        """Return data[key] if it is a whole number in [minimum, maximum].

        Otherwise log a warning and return the default.
        A missing key gives the default without any warning.
        """
        if key not in data:
            return default
        value: int = data[key]
        # bool is a kind of int in Python, so True would pass: refuse it.
        if isinstance(value, bool) or not isinstance(value, int):
            logging.warning("Config: '%s' must be a whole number (got %r). "
                            "Using default: %d", key, value, default)
            return default
        if not minimum <= value <= maximum:
            logging.warning("Config: '%s' must be between %d and %d "
                            "(got %d). Using default: %d", key, minimum,
                            maximum, value, default)
            return default
        return value

    @staticmethod
    def read_bool(data: dict[str, Any], key: str, default: bool) -> bool:
        """Return data[key] if it is true or false, else the default."""
        if key not in data:
            return default
        value = data[key]
        if not isinstance(value, bool):
            logging.warning("Config: '%s' must be true or false (got %r). "
                            "Using default: %s", key, value, default)
            return default
        return value

    @staticmethod
    def read_filename(data: dict[str, Any], default: str) -> str:
        """Return 'highscore_filename' if it is a non-empty text."""
        if "highscore_filename" not in data:
            return default
        value = data["highscore_filename"]
        if not isinstance(value, str) or not value.strip():
            logging.warning("Config: 'highscore_filename' must be a "
                            "non-empty text (got %r). Using default: %s",
                            value, default)
            return default
        return value.strip()

    @staticmethod
    def read_levels(data: dict[str, Any]) -> list[LevelConfig]:
        """Return the valid levels. Bad levels are skipped with a warning."""
        if "levels" not in data:
            return LevelConfig.default_levels()
        raw = data["levels"]
        if not isinstance(raw, list):
            logging.warning("Config: 'levels' must be a list (got %r). "
                            "Using default levels.", raw)
            return LevelConfig.default_levels()

        levels: list[LevelConfig] = []
        for index, item in enumerate(raw, start=1):
            if not isinstance(item, dict):
                logging.warning("Config: level %d must be an object with "
                                "'width' and 'height'. Level skipped.",
                                index)
                continue
            width = ConfigParser.read_int(item, "width", 0,
                                          MIN_MAZE_SIZE, MAX_MAZE_SIZE)
            height = ConfigParser.read_int(item, "height", 0,
                                           MIN_MAZE_SIZE, MAX_MAZE_SIZE)
            if width == 0 or height == 0:
                logging.warning("Config: level %d needs a valid 'width' and "
                                "'height' (%d to %d). Level skipped.",
                                index, MIN_MAZE_SIZE, MAX_MAZE_SIZE)
                continue
            levels.append(LevelConfig(width, height))

        if not levels:
            logging.warning("Config: no valid level found. "
                            "Using default levels.")
            return LevelConfig.default_levels()
        return levels


@dataclass
class GameConfig:
    """All game settings. Names are the same as the keys in config.json."""

    highscore_filename: str = "highscores.json"
    lives: int = 3
    pacgum: int = 1000
    points_per_pacgum: int = 10
    points_per_super_pacgum: int = 50
    points_per_ghost: int = 200
    seed: int = 42
    level_max_time: int = 90
    cheat_mode: bool = False
    levels: list[LevelConfig] = field(
        default_factory=LevelConfig.default_levels)

    @classmethod
    def from_file(cls, filepath: str) -> "GameConfig":
        """Load the configuration file. Never raises: errors give defaults."""
        config = cls()

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
            data = json.loads(strip_comments(text))
        except FileNotFoundError:
            logging.error("Config file '%s' not found. Using default "
                          "settings.", filepath)
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

        read = ConfigParser
        config.highscore_filename = read.read_filename(
            data, config.highscore_filename)
        config.lives = read.read_int(data, "lives", config.lives, 1, 99)
        config.pacgum = read.read_int(data, "pacgum", config.pacgum,
                                      1, 10000)
        config.points_per_pacgum = read.read_int(
            data, "points_per_pacgum", config.points_per_pacgum, 0, 100000)
        config.points_per_super_pacgum = read.read_int(
            data, "points_per_super_pacgum", config.points_per_super_pacgum,
            0, 100000)
        config.points_per_ghost = read.read_int(
            data, "points_per_ghost", config.points_per_ghost, 0, 100000)
        # seed > 0 only: 0 or less would give a random first level
        config.seed = read.read_int(data, "seed", config.seed,
                                    1, 2**31 - 1)
        config.level_max_time = read.read_int(
            data, "level_max_time", config.level_max_time, 10, 3600)
        config.cheat_mode = read.read_bool(data, "cheat_mode",
                                           config.cheat_mode)
        config.levels = read.read_levels(data)
        return config
