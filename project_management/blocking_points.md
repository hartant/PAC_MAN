# Blocking points and conflicts

| Problem | How we solved it |
|---|---|
| First `git push` refused (empty repository, then password authentication removed) | Created the first commit, used a personal access token / SSH key, added the teammate as collaborator |
| Window not resizable, menu and maze did not follow the size | Window created with `RESIZABLE`, all sizes computed from the real window size every frame |
| Player moved the whole corridor with one key press | Cell by cell movement with a step time; direction memory (like the real game) |
| Logic and UI written in parallel by two people | Fixed the interface first (UI reads numbers/positions only), merged file by file |
| `pygame` and `pygame-ce` both in `pyproject.toml` (conflict) | Kept only `pygame` |
| Highscores always empty (list read before the game ran) | Highscore system object shared by the menu and the engine |
| Big mazes crash the A-Maze-ing package (recursion) | Raised the recursion limit during the call, limited the size, clean `MazeError` |
| Decision: what to do when the level time is over | Lose a life and retry (dots stay eaten) |
| Decision: meaning of `pacgum: 42` in the config | Kept as a checked key, not used (dots in all corridors, see README) |
