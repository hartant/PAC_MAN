*This project has been created as part of the 42 curriculum by <mbenamar>, <ahbarbou>.*

# Pac-Man — Ghosts! More ghosts!

## Description

A complete and playable Pac-Man written in **Python 3.10+** with **pygame**.
The goal of the project is to rebuild the arcade classic with a clean,
modular, object-oriented code: a maze made by an external package
(*A-Maze-ing*), a configuration file with comments, ghosts with their own
behaviour, 10 levels with a timer, a persistent top 10, and a cheat mode to
help the peer review.

Game loop: **Main menu → Start game → Win or lose → Enter name → Main menu**.

Features:

- Main menu (Start Game, View Highscores, Instructions, Exit), top 10 shown
  in the menu, resizable window.
- Maze from the A-Maze-ing package (`perfect=False`: loops, Pac-Man like).
  Level 1 uses a fixed seed, the next levels are random.
- Pacgums in the corridors, 4 super-pacgums in the corners, 4 ghosts (one
  per corner), the player starts in the middle.
- Ghosts chase the player (each color has its own way), run away and turn
  blue when edible, go back to their corner when eaten, come back after 6 s.
- Lives, score, level and remaining time always visible (HUD).
- Pause menu (Resume / Return to the main menu), Game over and Victory
  screens with name input.
- Cheat mode for the reviewers.
- Packaged as a standalone game (PyInstaller) for Itch.io.

## Instructions

### Install

Dependencies are managed with **[uv](https://docs.astral.sh/uv/)**:
`pyproject.toml` lists them and `uv.lock` pins their exact versions, so every
machine installs the same ones. The assigned A-Maze-ing package is the wheel
`mazegenerator-*.whl` at the root of the repository; it is a dependency of
the project (`[tool.uv.sources]`), installed as it is, never modified.

```bash
make install        # = uv sync  (creates .venv: pygame, the maze wheel,
                    #   flake8, mypy, pytest, pyinstaller)
```

If uv is missing, `make install` installs it first (`pip install --user uv`).
To re-install the maze package from its wheel:
`uv sync --reinstall-package mazegenerator`.

### Run

```bash
make run                                   # = uv run python pac-man.py config.json
uv run python pac-man.py my_config.json    # any JSON file with the same format
```

The program takes **exactly one argument**: the configuration file (the
packaged game started with a double click uses the `config.json` next to it). A missing
file, a wrong value or a missing key never gives a traceback: a clear message
is printed and safe defaults are used.

### Rules of the Makefile

| Rule | What it does |
|---|---|
| `make install` | Install the dependencies with uv (`uv sync`) |
| `make run` | Start the game with `config.json` |
| `make debug` | Start the game with `pdb` |
| `make clean` | Remove `__pycache__`, `.mypy_cache`, `.pytest_cache`, `build`, `dist` |
| `make lint` | `flake8 .` and `mypy .` with the flags of the subject |

### Controls

| Key | Action |
|---|---|
| Arrow keys / WASD | Move (Pac-Man goes straight until a wall; the next turn is remembered) |
| P or ESC | Pause / resume |
| R | Back to the main menu |
| Q | Quit the program |
| C | Cheat mode on / off |

Cheat mode keys (only when the cheat mode is on, a help line is shown at the
bottom of the window): `I` invincible, `F` freeze the ghosts, `N` win the level now, `L` one more life.
The cheat mode can also be started from the config file (`"cheat_mode": true`).

### Rules

- Eat all the dots (small and big) to win the level.
- A big dot makes the ghosts blue for 8 seconds: eat them for points. They
  blink at the end of the power.
- A ghost touching you costs a life. When the level time is over you also
  lose a life and the level restarts (the dots already eaten stay eaten).
- Score and lives are kept between the levels. No life left: game over.
  All the levels done: victory. Then you type your name for the highscores.

## Configuration

`config.json` is a JSON file where **lines starting with `#` are comments**
(they are removed before the JSON is read). C comments `/* ... */` (on one
or more lines) and C++ comments `// ...` are accepted too; comment marks
inside a "string" are kept. Every key is optional.

| Key | Default | Allowed values | Meaning |
|---|---|---|---|
| `highscore_filename` | `"highscores.json"` | non-empty text | File of the top 10 |
| `lives` | `3` | whole number 1–99 | Lives at the start of the game |
| `pacgum` | `1000` | whole number 1–10000 | Maximum number of small dots per level. If the maze has more free cells, the dots are spread at regular steps over the whole maze; with a big value every corridor cell gets a dot |
| `points_per_pacgum` | `10` | whole number 0–100000 | Points for a pacgum (X) |
| `points_per_super_pacgum` | `50` | whole number 0–100000 | Points for a super-pacgum (Y) |
| `points_per_ghost` | `200` | whole number 0–100000 | Points for an edible ghost (Z) |
| `seed` | `42` | whole number ≥ 1 | Seed of the maze of level 1 (always the same maze). 0 or less is refused (it would make level 1 random) |
| `level_max_time` | `90` | whole number 10–3600 | Seconds for each level |
| `cheat_mode` | `false` | `true` / `false` | Start with the cheat mode on |
| `levels` | 10 levels (15x15 → 19x19) | list of `{"width": 5–30, "height": 5–30}` | One item per level. The game is won after the last one |

Faulty config handling (never a traceback, the game always starts):

- Missing key → default value (silent).
- Wrong type, `true` instead of a number, a decimal number, text, or a
  number out of the allowed range → **warning in the terminal + default
  value** for this key only.
- A bad item in `levels` is skipped (warning). No valid level → default levels.
- Unknown keys are ignored (warning). Missing file, broken JSON or a root
  that is not an object → all defaults + error message.

Tip for the reviewers: a bigger maze needs more time. With the default speed
a 15x15 maze needs about 40 s to clear, 19x19 about 65 s (without ghosts).

## Highscore

`src/logic/highscore.py` (`ScoringSystem`) keeps the **top 10** in a JSON file
(`highscores.json` by default, in the folder where the game is started):

```json
[{"name": "Ann", "score": 4200}, {"name": "Bob", "score": 1500}]
```

- Loaded when the game starts, shown in the main menu and in *View
  Highscores*, saved as soon as a name is entered at the end of a game (win
  or lose). The list is sorted, only the 10 best are kept.
- Names: 10 characters max, ASCII letters, digits and spaces only (the name
  screen refuses other keys, and the system cleans the name again).
  Scores: non-negative integers (booleans, floats, negatives are refused).
- Robust: a missing file is a first launch; invalid JSON, a wrong format or
  bad entries give a warning and an empty list (or the good entries only).
  The file is written in a temporary file then renamed, so a crash cannot
  leave half a file. If the file cannot be written, a warning is printed and
  the game goes on.

Why a JSON file: simple to read for a human, easy to fix by hand, no
dependency, and it is enough for 10 lines.

## Maze generation

The maze comes from the assigned **A-Maze-ing** package: the wheel
`mazegenerator-*.whl` given at the start of the project, installed with
`make install` (uv) and used as it is (never modified, never copied in our code).
Our loader adapts to its interface:
`src/logic/maze.py → Maze.generate(width, height, seed)` loads the
`MazeGenerator` class of the package (`Maze.load_generator`) and calls

```python
MazeGenerator(size=(width, height), perfect=False, seed=seed).maze
```

- `perfect=False` removes some walls: there are loops, like in Pac-Man.
- **Level 1**: `seed = config.seed` (always the same maze). **Next levels**:
  seed 0 = random maze.
- The result is checked (right size, values 0–15, all the free cells are
  linked). If the generator raises an error or gives an unusable maze, we try
  again (random seed, 5 tries) then `MazeError` is raised: the menu shows a
  message and no traceback. If the package is not installed, the same clean
  `MazeError` is shown ("run: make install"). The package builds the maze with a recursive
  function, so the recursion limit is raised during the call (big mazes).
- Each cell is a number 0–15 (one bit per wall: top 1, right 2, bottom 4,
  left 8). A cell worth 15 is part of the "42" drawing in the middle.

## Implementation

- **Time based loop** (`GameEngine.run`): 60 FPS, `dt` in seconds (max 50 ms)
  is given to everybody, so the speed does not depend on the computer.
  The pause simply stops calling `update`: timers, ghosts and the power time
  are all frozen.
- **Movement**: the player and each ghost go to a new cell every
  `step_time` seconds (player 0.12 s, ghosts 0.22 s, blue ghosts 0.35 s).
  All 4 ghosts leave their corner at the start of the level. The previous cell is kept and the
  screen slides the character between the two cells (smooth animation).
  The player goes straight and keeps the next asked direction until a turn is
  possible, like the real game.
- **Ghost AI**: every ghost computes the walking distance (BFS, cached per
  level) to its target and takes the neighbour cell that is the closest.
  A ghost never turns back by itself. Red (Blinky) targets the player, pink
  (Pinky) the cell 4 steps in front of the player, cyan (Inky) alternates
  chase and wandering, orange (Clyde) chases from far and goes to its corner
  when closer than 6 cells. Different targets stop the ghosts from walking
  as one. They leave their corner one after the other (every 2 s).
  Edible ghosts go to the cell farthest from the player. An eaten ghost
  waits 6 s in its corner then comes back.
- **Collisions**: checked after each move of the player or of a ghost.
- **Levels / timer**: `levels` of the config, time left shown in the HUD. If the
  time is over: one life less, ghosts and player go back to their start, the
  timer restarts, the eaten dots stay eaten.
- **Cheat mode**: see the controls.
- **UI**: all the drawing is in `src/ui/` and only reads the game
  (`GameState` for the HUD). The window can be resized: the maze and the
  menus follow.

### Tests

`python3 -m pytest src/tests` runs 14 tests: config reader and
comments, faulty values, maze generation and walls, dots spread, super
pacgum, highscores (top 10, names, broken file).

## General Software Architecture

```
pac-man.py                 Application (entry point): config → menu → game → menu ...
│
├── src/ui/                what the player sees
│   ├── config.py          GameConfig (from_file), LevelConfig, ConfigParser
│   ├── menu.py            MainMenu (logic) + MenuScreen (drawing, loop)
│   ├── graphics.py        Renderer: maze, dots, Pac-Man, ghosts
│   ├── hud.py             Hud: score / lives / level / time, banners
│   ├── game_state.py      GameState: numbers read by the HUD
│   ├── pause.py           PauseMenu
│   ├── end_screen.py      EndScreen: game over / victory + name input
│   └── name_input.py      NameInput: the 10 characters rules
│
├── src/logic/             the rules of the game (no drawing)
│   ├── core.py            GameEngine: loop, levels, timer, collisions, cheat
│   ├── maze.py            Maze (walls, BFS, Maze.generate = A-Maze-ing loader)
│   ├── father.py          Character (base: walls rule) → Player, Ghost
│   ├── packgum.py         Pacgum: dots and super mode
│   └── highscore.py       ScoringSystem: top 10 file
│
├── src/tests/             tests (pytest)
├── pac-man.spec           PyInstaller packaging script (Itch.io build)
└── mazegenerator-*.whl    A-Maze-ing package of another group (installed, not modified)
```

Inheritance: `Player` and `Ghost` both inherit from `Character`, which owns
the position, the start cell, the step timer and the rule "never walk
through a wall" (`Character.can_go` / `Character.move`).

Relations: `pac-man.py` creates `GameConfig` and `ScoringSystem`, shows
`MenuScreen`, then creates a `GameEngine(config, scoring)`. The engine owns
the `Maze`, the `Player`, 4 `Ghost`, the `Pacgum` (dots), a `Renderer`, the
`Hud` and the `PauseMenu`. Each level builds a new maze with `Maze.generate`.
The logic never imports `pygame` drawing code and the drawing code never
changes the game.

## Project Management

How we worked (timeline, roles, risks, acceptance tests, blocking points) is
in [`project_management/`](project_management/README.md).

## Packaging

The packaging script is `pac-man.spec`, at the root of the repository.
PyInstaller (installed by uv) turns the game into a folder that runs
without Python. Build it from zero, at the root of the repository:

```bash
make install                                   # uv sync
rm -rf build dist                              # start from zero
uv run pyinstaller --noconfirm pac-man.spec    # -> dist/pac-man/
cp config.json README.md dist/pac-man/         # settings + instructions
cd dist && zip -r pac-man-linux.zip pac-man && cd ..
```

`dist/pac-man/` contains the program `pac-man`, its `_internal/` folder,
`config.json` and `README.md` (the in-package instructions). Double-click
`pac-man` to play: without an argument the packaged game reads the
`config.json` next to it and saves `highscores.json` there. A build only
runs on the system it was made on (build on Linux for Linux, on Windows for
Windows). The zip is the free (unlisted) build uploaded on Itch.io:

**Itch.io page:** <https://dexter-x.itch.io/pacman>

## Resources

- pygame documentation: https://www.pygame.org/docs/
- Python docs: `dataclasses`, `json`, `logging`, `collections.deque`,
  `tempfile`, `typing`; PEP 8, PEP 257 (docstrings), flake8 and mypy docs.
- The Pac-Man Dossier (ghost behaviours, speeds):
  https://pacman.holenet.info/
- Breadth-first search (used for the ghosts): any algorithms course.
- PyInstaller documentation: https://pyinstaller.org/
- uv documentation: https://docs.astral.sh/uv/
- Itch.io creator documentation: https://itch.io/docs/creators/

### How AI was used

AI (Claude) was used as an assistant, never as a black box. We read, ran and
tested everything and each of us can explain the code of the project:

- explaining pygame and Python concepts, step by step (game loop, events,
  fonts, dataclasses, BFS, type hints);
- writing and reviewing the UI (menu, HUD, pause, end screens) and the
  configuration parser;
- reviewing the game logic against the subject, finding bugs (ghosts
  walking on the same cell, pause not freezing the timers, scores lost
  between games...) and proposing the final logic: levels, timer, ghost
  behaviours, highscore file, cheat mode;
- writing the tests, the Makefile, the packaging script and drafts of the
  documents. The tests and the lint (`flake8`, `mypy`) are our proof that
  it works.
