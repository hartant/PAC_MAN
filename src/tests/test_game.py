"""Tests of the game rules (maze, player, ghosts, engine)."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.logic.core import GameEngine, GHOST_STEP, PLAYER_STEP  # noqa: E402
from src.logic.father import EATEN, NORMAL  # noqa: E402
from src.logic.highscore import ScoringSystem  # noqa: E402
from src.logic.maze import Maze, build_maze  # noqa: E402
from src.ui.config import GameConfig  # noqa: E402


def make_engine() -> GameEngine:
    config = GameConfig()
    config.seed = 42
    scoring = ScoringSystem("/nonexistent/scores.json")
    engine = GameEngine(config, scoring, 800, 600)
    engine.ready_left = 0.0
    return engine


def test_same_seed_same_maze() -> None:
    assert build_maze(15, 15, 42) == build_maze(15, 15, 42)


def test_walls_are_consistent() -> None:
    maze = Maze(build_maze(15, 15, 42))
    for row in range(maze.rows):
        for col in range(maze.cols):
            for direction, (d_row, d_col) in Maze.OFFSETS.items():
                if maze.can_move(row, col, direction):
                    assert maze.can_move(row + d_row, col + d_col,
                                         Maze.OPPOSITE[direction])


def test_all_ghosts_move_from_the_start() -> None:
    engine = make_engine()
    engine.freeze_ghosts = False
    engine.invincible = True
    start = [(g.pos_x, g.pos_y) for g in engine.ghosts]
    for _ in range(int(GHOST_STEP / 0.02) + 2):
        engine.update(0.02)
    for ghost, before in zip(engine.ghosts, start):
        assert (ghost.pos_x, ghost.pos_y) != before


def test_ghost_is_slower_than_player() -> None:
    assert GHOST_STEP > PLAYER_STEP


def test_touching_a_ghost_costs_a_life() -> None:
    engine = make_engine()
    engine.invincible = False
    ghost = engine.ghosts[0]
    engine.player.pos_x, engine.player.pos_y = ghost.pos_x, ghost.pos_y
    lives = engine.player.lives
    engine.check_collisions()
    assert engine.player.lives == lives - 1


def test_eating_a_super_pacgum_makes_ghosts_edible() -> None:
    engine = make_engine()
    engine.invincible = False
    row, col = engine.maze.corners()[0]
    engine.ghosts[0].pos_x = engine.ghosts[0].pos_y = 1
    engine.player.pos_x, engine.player.pos_y = col, row
    engine.eat_dots()
    assert all(g.edible for g in engine.ghosts)
    assert engine.player.score == engine.config.points_per_super_pacgum
    # eat a ghost
    ghost = engine.ghosts[1]
    engine.player.pos_x, engine.player.pos_y = ghost.pos_x, ghost.pos_y
    engine.check_collisions()
    assert ghost.state == EATEN
    assert engine.player.lives == engine.config.lives


def test_eaten_ghost_comes_back() -> None:
    engine = make_engine()
    ghost = engine.ghosts[0]
    ghost.eat(1.0)
    ghost.update(1.5, engine.player, GHOST_STEP)
    assert ghost.state == NORMAL


def test_time_over_costs_a_life() -> None:
    engine = make_engine()
    engine.time_left = 0.01
    engine.update(0.05)
    assert engine.player.lives == engine.config.lives - 1


def test_no_life_left_is_game_over() -> None:
    engine = make_engine()
    engine.player.lives = 1
    engine.lose_life("CAUGHT!")
    assert engine.end_kind == "game_over"


def test_winning_all_levels_is_victory() -> None:
    engine = make_engine()
    engine.level_index = len(engine.config.levels) - 1
    engine.next_level()
    assert engine.end_kind == "victory"
