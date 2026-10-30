# Project analysis and choices

## Subject → requirements

| Requirement | Where it is done |
|---|---|
| `python3 pac-man.py config.json`, exactly one argument, no traceback | `pac-man.py` |
| JSON with `#` comments, robust defaults, faulty config handling | `src/ui/config.py` |
| A-Maze-ing package as is, `perfect=False`, errors handled | `src/logic/maze.py` (`Maze.generate`) |
| Highscore: top 10, names ≤ 10 (alnum + spaces), scores ≥ 0, load/save, menu | `src/logic/highscore.py`, `src/ui/menu.py` |
| Level 1 fixed seed, other levels random, ≥ 10 levels, time limit | `GameEngine.load_level` |
| Pacgums, 4 super-pacgums, 4 ghosts, player in the middle | `packgum.py`, `father.py` |
| Chase / run away / respawn of ghosts | `Ghost` |
| Cheat mode | `GameEngine.handle_cheat_key` |
| Menu, HUD, pause, game over, victory | `src/ui/` |
| Makefile, flake8, mypy, type hints, docstrings | whole project |
| Packaging, README, project management | `Makefile` (`make package`), `README.md`, this folder |

## Main technical choices

- **pygame**: simple, well documented, enough for a 2D game.
- **Logic / drawing split**: `src/logic` has the rules, `src/ui` the drawing.
  Easier to test (30 tests without a real window) and to explain.
- **Time based updates (`dt`)**: same speed on every computer; pause = do not
  call `update`.
- **Cell by cell movement + sliding animation**: simple rules (positions are
  whole numbers) and a smooth picture.
- **BFS distances for the ghosts** (cached by target cell): always the real
  walking distance, works with loops, and a different target per ghost gives
  different behaviours.
- **Highscores in a JSON file**: readable, simple, no dependency.
- **Time over = lose a life + retry the level**: the player is never stuck and
  the game still ends.
