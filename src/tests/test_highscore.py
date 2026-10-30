"""Tests of the highscore system (src/logic/highscore.py)."""

import json
import os
import tempfile

from src.logic.highscore import ScoringSystem


def new_path() -> str:
    return os.path.join(tempfile.mkdtemp(), "scores.json")


def test_names_are_cleaned() -> None:
    assert ScoringSystem.clean_name("  Ann  ") == "Ann"
    assert ScoringSystem.clean_name("A!n@n#") == "Ann"
    assert ScoringSystem.clean_name("abcdefghijklmnop") == "abcdefghij"
    assert ScoringSystem.clean_name("Zoë") == "Zo"
    assert ScoringSystem.clean_name("   ") == ""
    assert ScoringSystem.clean_name(42) == ""


def test_scores_are_sorted_and_saved() -> None:
    path = new_path()
    system = ScoringSystem(path)
    system.add("Bob", 50)
    system.add("Ann", 300)
    system.add("Cid", 120)
    assert system.top() == [("Ann", 300), ("Cid", 120), ("Bob", 50)]
    assert ScoringSystem(path).top() == system.top()      # reload


def test_only_the_top_10_are_kept() -> None:
    system = ScoringSystem(new_path())
    for score in range(15):
        system.add(f"P{score}", score * 10)
    assert len(system.top()) == 10
    assert system.top()[0] == ("P14", 140)
    assert system.top()[-1] == ("P5", 50)
    assert system.add("Low", 1) is False        # does not enter the top 10


def test_invalid_scores_are_refused() -> None:
    system = ScoringSystem(new_path())
    assert system.add("Ann", -5) is False
    assert system.add("Ann", True) is False
    assert system.add("Ann", 1.5) is False  # type: ignore[arg-type]
    assert system.add("!!!", 10) is False
    assert system.top() == []


def test_zero_is_a_valid_score() -> None:
    system = ScoringSystem(new_path())
    assert system.add("Ann", 0) is True


def test_bad_files_give_an_empty_list() -> None:
    for text in ("not json", "{}", "42", "[1, 2]", ""):
        path = new_path()
        with open(path, "w", encoding="utf-8") as file:
            file.write(text)
        assert ScoringSystem(path).top() == [], text


def test_bad_entries_are_skipped_good_ones_kept() -> None:
    path = new_path()
    data = [{"name": "Ann", "score": 10}, {"name": "", "score": 5},
            {"name": "Bob", "score": -1}, {"name": "Cid", "score": "x"},
            {"score": 3}, "text", {"name": "Dan", "score": 20}]
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file)
    assert ScoringSystem(path).top() == [("Dan", 20), ("Ann", 10)]


def test_missing_file_is_fine() -> None:
    assert ScoringSystem(new_path()).top() == []


def test_cannot_write_does_not_crash() -> None:
    system = ScoringSystem("/proc/not_allowed/scores.json")
    system.add("Ann", 10)       # only a warning in the terminal
    assert system.top() == [("Ann", 10)]
