"""Tests of the config file reader (src/ui/config.py)."""

import os
import tempfile

from src.ui.config import GameConfig, load_config


def read(text: str) -> GameConfig:
    """Write a config file, load it, give the result."""
    path = os.path.join(tempfile.mkdtemp(), "config.json")
    with open(path, "w", encoding="utf-8") as file:
        file.write(text)
    return load_config(path)


def test_comments_are_ignored() -> None:
    config = read('# a comment\n{\n  # other\n  "lives": 5, "seed": 7\n}')
    assert config.lives == 5
    assert config.seed == 7


def test_missing_key_gives_default() -> None:
    assert read("{}").lives == GameConfig().lives


def test_wrong_values_give_defaults() -> None:
    default = GameConfig()
    for bad in ("-4", "0", "3.9", "true", '"abc"', "null", "[1]", "1000"):
        assert read('{"lives": %s}' % bad).lives == default.lives, bad


def test_limits_of_the_time() -> None:
    assert read('{"level_max_time": 99999}').level_max_time == 90
    assert read('{"level_max_time": 5}').level_max_time == 90
    assert read('{"level_max_time": 30}').level_max_time == 30


def test_broken_files_give_all_defaults() -> None:
    default = GameConfig()
    for text in ('{"lives": 5,}', "[1, 2]", "", "not json", "42"):
        assert read(text) == default, text


def test_missing_file_gives_defaults() -> None:
    assert load_config("this_file_does_not_exist.json") == GameConfig()


def test_unknown_keys_are_ignored() -> None:
    assert read('{"foo": 1, "lives": 2}').lives == 2


def test_levels_are_read_and_bad_ones_skipped() -> None:
    config = read('{"levels": [{"width": 15, "height": 15}, 5, '
                  '{"width": 99, "height": 9}, {"width": 21, "height": 17}]}')
    assert [(lvl.width, lvl.height) for lvl in config.levels] == [
        (15, 15), (21, 17)]


def test_no_valid_level_gives_the_default_levels() -> None:
    assert len(read('{"levels": [1, 2]}').levels) == 10
    assert len(read("{}").levels) == 10


def test_cheat_mode_must_be_a_boolean() -> None:
    assert read('{"cheat_mode": true}').cheat_mode is True
    assert read('{"cheat_mode": 1}').cheat_mode is False


def test_real_config_file_is_valid() -> None:
    config = load_config("config.json")
    assert config.lives == 3
    assert len(config.levels) >= 10
