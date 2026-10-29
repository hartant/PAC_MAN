"""Persistent top 10 highscores, stored in a JSON file.

File format (a list, best score first)::

    [{"name": "Ann", "score": 1200}, {"name": "Bob", "score": 800}]

Every problem with the file (missing, not JSON, wrong content, no right to
write...) is logged and the game goes on: it never crashes.
"""

import json
import logging
from typing import Any, List, Tuple

MAX_NAME_LENGTH = 10
TOP_SIZE = 10


def clean_name(name: object) -> str:
    """Return a safe name: ASCII letters, digits, spaces, 10 chars max."""
    if not isinstance(name, str):
        return ""
    kept = "".join(ch for ch in name
                   if ch.isascii() and (ch.isalnum() or ch == " "))
    return kept.strip()[:MAX_NAME_LENGTH].strip()


def is_valid_score(score: object) -> bool:
    """A score is a whole number, not negative (True/False are refused)."""
    return (isinstance(score, int) and not isinstance(score, bool)
            and score >= 0)


class ScoringSystem:
    """Load, keep and save the top 10 scores."""

    def __init__(self, filename: str = "highscores.json") -> None:
        """Create the system and load the file right now."""
        self.filename: str = filename
        self.scores: List[Tuple[str, int]] = []
        self.load()

    def load(self) -> None:
        """Read the file. A bad file gives an empty list (and a warning)."""
        self.scores = []
        try:
            with open(self.filename, "r", encoding="utf-8") as file:
                data: Any = json.load(file)
        except FileNotFoundError:
            return                      # first launch: nothing to load
        except (OSError, ValueError) as err:
            logging.warning("Highscores: cannot read '%s' (%s).",
                            self.filename, err)
            return

        if not isinstance(data, list):
            logging.warning("Highscores: '%s' must contain a list.",
                            self.filename)
            return

        for item in data:
            if not isinstance(item, dict):
                continue
            name = clean_name(item.get("name"))
            score = item.get("score")
            if name and isinstance(score, int) and is_valid_score(score):
                self.scores.append((name, score))
            else:
                logging.warning("Highscores: bad entry ignored: %r", item)
        self.scores.sort(key=lambda entry: entry[1], reverse=True)
        del self.scores[TOP_SIZE:]

    def add(self, name: str, score: int) -> bool:
        """Add a score, keep the top 10 and save the file.

        Returns:
            True if the score entered the top 10.
        """
        name = clean_name(name)
        if not name or not is_valid_score(score):
            logging.warning("Highscores: invalid score ignored (%r, %r).",
                            name, score)
            return False

        self.scores.append((name, score))
        self.scores.sort(key=lambda entry: entry[1], reverse=True)
        del self.scores[TOP_SIZE:]
        self.save()
        return (name, score) in self.scores

    def top(self) -> List[Tuple[str, int]]:
        """A copy of the list, best score first."""
        return list(self.scores)

    def save(self) -> None:
        """Write the file. A problem is only a warning."""
        data = [{"name": name, "score": score}
                for name, score in self.scores]
        try:
            with open(self.filename, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=2)
        except OSError as err:
            logging.warning("Highscores: cannot save '%s' (%s).",
                            self.filename, err)
