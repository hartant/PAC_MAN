# Risk analysis

| Risk | Impact | Probability | What we did |
|---|---|---|---|
| Bad config file crashes the game | High (a crash = not functional) | Medium | Every key checked, defaults, warnings, tests (`test_config.py`) |
| The maze generator fails (it is not ours) | High | Low | `build_maze` catches errors, checks the maze, retries, `MazeError` shown in the menu; recursion limit raised for big mazes |
| Highscore file missing / corrupted / read-only | Medium | Medium | Every case handled, file written safely, tests (`test_highscore.py`) |
| Ghosts walk on the same cell (unfair / ugly) | Medium | Happened | Different target per ghost, no U-turn, staggered start |
| Level too long for the time limit | Medium | Happened | Measured the clear time per maze size, limited default sizes to 15–19 |
| Two members edit the same file | Medium | Medium | Clear ownership of folders, small commits, one shared file (`core.py`) tested by both |
| Assigned package replaced during the peer review | Medium | Certain | Loader only uses `MazeGenerator(size, perfect, seed).maze` |
| Package does not run on another machine | High | Medium | `make package` tested; the folder contains config.json and README |
| We cannot explain the code (AI misuse) | High | Medium | Files explained one by one, tests, code kept simple |
| Lack of time before the defense | High | Medium | Mandatory features first, packaging and documents planned at the end |
