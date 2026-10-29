# Team organization

| Member | Role | Main files |
|---|---|---|
| hartant (<login1>) | Parsing and visualisation | `src/ui/*` (config, menu, graphics, HUD, pause, end screens), `pac-man.py` |
| Ahmed Barbouri (<login2>) | Game logic | `src/logic/*` (maze, player, ghosts, dots, engine) |

Shared file: `src/logic/core.py` (the engine uses the UI classes), so both
of us tested it after every change.

## How we decided

- The **interface between UI and logic** was fixed early: the UI only reads
  numbers (score, lives, level, time) and positions, the logic never draws.
  This let us work in parallel.
- Each feature was done in small steps (one file at a time) and explained to
  the other member before the merge, so both can explain the whole project
  during the defense.
- Technical choices (pygame, BFS ghosts, one `step_time` per character,
  JSON highscores) were discussed together; we kept the simplest one.

## Git workflow

- Branches: `main` (stable), `Dexter` (logic work), `hartant` (UI work).
- Small commits, a clear message, `git pull` before `git push`.
- Generated files (`__pycache__`, `highscores.json`, `dist/`) are in `.gitignore`.
- The assigned A-Maze-ing package is never modified.

## Handling issues

Problems were written in the acceptance test plan with the person who fixes
them. A bug in the file of the other member was reported, not edited.
