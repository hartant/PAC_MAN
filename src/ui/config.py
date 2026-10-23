import json
import logging
from dataclasses import dataclass

@dataclass
class GameConfig:
    """Safe game configuration with default values."""
    highscore_filename: str = "highscores.json"
    lives: int = 3
    pacgum_points: int = 10
    super_pacgum_points: int = 50
    ghost_points: int = 200
    seed: int = 42
    level_max_time: int = 90
    levels_count: int = 10

def load_config(filepath: str) -> GameConfig:
    """Load configuration from a JSON file, ignoring '#' comments 
    and falling back to safe defaults on errors.
    """
    config = GameConfig()
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # Filter out lines starting with '#' (ignoring leading whitespace)
        clean_lines = [line for line in lines if not line.strip().startswith("#")]
        raw_data = json.loads("".join(clean_lines))
        
        if not isinstance(raw_data, dict):
            logging.warning("Config root must be a JSON object. Using defaults.")
            return config

        # Safely parse expected keys, ignoring unknown ones
        if "highscore_filename" in raw_data and isinstance(raw_data["highscore_filename"], str):
            config.highscore_filename = raw_data["highscore_filename"]
            
        if "lives" in raw_data:
            try:
                config.lives = max(1, int(raw_data["lives"])) # Clamp minimum lives to 1
            except (ValueError, TypeError):
                logging.warning("Invalid 'lives' value. Using default: %d", config.lives)

        if "seed" in raw_data:
            try:
                config.seed = int(raw_data["seed"])
            except (ValueError, TypeError):
                logging.warning("Invalid 'seed' value. Using default: %d", config.seed)

        if "level_max_time" in raw_data:
            try:
                config.level_max_time = max(10, int(raw_data["level_max_time"]))
            except (ValueError, TypeError):
                logging.warning("Invalid 'level_max_time'. Using default: %d", config.level_max_time)

        # Repeat safely for other optional keys (points, etc.)

    except FileNotFoundError:
        logging.error("Configuration file '%s' not found. Using default settings.", filepath)
    except json.JSONDecodeError as e:
        logging.error("Malformed JSON in config file: %s. Using default settings.", e)
    except Exception as e:
        logging.error("Unexpected error loading config: %s. Using default settings.", e)

    return config