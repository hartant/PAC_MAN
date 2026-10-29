# Acceptance test plan

"Auto" = covered by `make test` (30 tests). "Manual" = played by a human.

| # | Feature (subject) | How it was tested | Result |
|---|---|---|---|
| 1 | Usage: one argument, no traceback on error | Manual: no argument, missing file, broken JSON | OK |
| 2 | Config comments with `#` | Auto: `test_comments_are_ignored` | OK |
| 3 | Wrong / missing values → defaults + message | Auto: `test_wrong_values_give_defaults`, `test_broken_files...` | OK |
| 4 | Maze from A-Maze-ing, fixed seed on level 1 | Auto: `test_first_level_is_always_the_same_maze` | OK |
| 5 | Generator failure handled | Auto: `test_generator_error_is_a_clean_maze_error` | OK |
| 6 | Walls: no walking through walls | Auto: `test_walls_are_the_same_on_both_sides`, player tests | OK |
| 7 | Player starts in the middle, 3 lives, respawn | Auto: engine tests | OK |
| 8 | Pacgums / super-pacgums, points from the config | Auto: dots tests, `test_player_eats_dots...` | OK |
| 9 | Super-pacgum makes ghosts edible for a time | Auto: `test_super_pacgum_makes_all_ghosts_edible...` | OK |
| 10 | Eat an edible ghost (+Z), it respawns | Auto: `test_edible_ghost_is_eaten...` | OK |
| 11 | Ghost touch = lose a life, game over at 0 | Auto: engine tests | OK |
| 12 | Level won when all dots eaten, next level, score and lives kept | Auto: `test_won_level_goes_to_next_level...` | OK |
| 13 | Victory after the last level | Auto: `test_finishing_the_last_level_is_a_victory` | OK |
| 14 | Level time limit | Auto: `test_time_over_costs_a_life...` | OK |
| 15 | Pause freezes everything, resume, back to menu | Auto: `test_pause_freezes_the_game` + manual | OK |
| 16 | Highscore: top 10, names, scores, file errors | Auto: `test_highscore.py` | OK |
| 17 | Name asked after win or lose, then main menu | Manual + scripted run of `pac-man.py` | OK |
| 18 | Menu: 4 items, highscores, instructions | Auto + manual | OK |
| 19 | HUD: score, lives, level, time | Auto + manual | OK |
| 20 | Resize the window | Manual | OK |
| 21 | Cheat mode (invincible, skip level, freeze, extra life) | Auto: `test_cheat_keys` + manual | OK |
| 22 | flake8 and mypy (subject flags and `--strict`) | `make lint`, `make lint-strict` | OK |
| 23 | Package starts on a clean folder | `make package` + run of the binary | OK on Linux; to repeat on the machine of the defense |

## Bugs found and fixed (history)

| Bug | Found by | Fix |
|---|---|---|
| Player ran to the wall with one key | Visual test | Cell by cell movement with a step time |
| Ghosts ended on the same cell | Manual + simulation | Different target per ghost, no U-turn, slower ghosts |
| Pause did not stop the timers | Review of `core.py` | Update is not called while paused, game time instead of the wall clock |
| Scores lost between games / empty highscores in the menu | Manual | `ScoringSystem` saved in a file and given to the menu |
| `true` accepted as `1` in the config | Review | `bool` is refused for numbers |
| Points and lives were fixed numbers in the code | Review | Read from the config |
| Even sized maze: player started inside the "42" | Review | `Maze.start_cell` takes the nearest free cell |
| 50x50 maze crashed the generator (recursion) | Test | Higher recursion limit + max size 40 + `MazeError` |
| Super mode gave invincibility instead of edible ghosts | Review | Real edible state, blue ghosts that run away |
| No levels, no timer, no victory | Review against the subject | Levels from the config, timer, victory screen |
