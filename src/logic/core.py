"""The game engine: levels, timer, lives, collisions, cheat mode, screens.

One GameEngine runs one whole game (from level 1 to the victory or the game
over). It returns "menu" or "quit" to pac-man.py when the game is finished.
"""

import logging
import math
from typing import List, Optional, Tuple

import pygame as pg

from src.logic.father import EATEN, Ghost, Player
from src.logic.highscore import ScoringSystem
from src.logic.maze import Maze
from src.logic.packgum import SUPER, Pacgum
from src.ui.config import GameConfig
from src.ui.end_screen import EndScreen
from src.ui.game_state import GameState
from src.ui.graphics import Renderer
from src.ui.hud import Hud
from src.ui.menu import KEY_NAMES
from src.ui.pause import PauseMenu

# arrow keys and WASD -> direction of the move
KEY_TO_DIRECTION = {
    pg.K_UP: Maze.TOP, pg.K_w: Maze.TOP,
    pg.K_DOWN: Maze.BUTTOM, pg.K_s: Maze.BUTTOM,
    pg.K_LEFT: Maze.LEFT, pg.K_a: Maze.LEFT,
    pg.K_RIGHT: Maze.RIGHT, pg.K_d: Maze.RIGHT,
}

# times are in seconds
PLAYER_STEP = 0.12          # the player goes to a new cell every 0.12 s
GHOST_STEP = 0.22           # a ghost is almost 2 times slower than us
EDIBLE_STEP = 0.35          # a blue ghost is even slower
RESPAWN_TIME = 6.0          # an eaten ghost comes back after 6 s
SUPERMODE_TIME = 8.0        # the ghosts stay blue for 8 s
FLASH_TIME = 2.5            # they blink during the last seconds
READY_TIME = 2.0            # "READY!" before a level starts
MAX_DT = 0.05               # never count more than 50 ms in one frame
HUD_BAND = 60               # height of the bottom bar (pixels)


class GameEngine():
    """Runs the game: updates the characters, draws, reads the keyboard."""

    def __init__(self, config: GameConfig, scoring: ScoringSystem,
                 wx: int = 1200, wy: int = 900) -> None:
        """Prepare the game and build the maze of level 1.

        Args:
            config: the settings read in config.json.
            scoring: the highscores (a score is added at the end).
            wx: width of the window if it does not exist yet.
            wy: height of the window if it does not exist yet.

        Raises:
            MazeError: if the maze of the first level cannot be made.
        """
        pg.init()
        self.config: GameConfig = config
        self.scoring: ScoringSystem = scoring

        # reuse the menu window; create it only if it does not exist
        screen = pg.display.get_surface()
        if screen is None:
            screen = pg.display.set_mode((wx, wy), pg.RESIZABLE)
        self.screen: pg.Surface = screen
        self.window_width, self.window_height = screen.get_size()
        self.clock = pg.time.Clock()

        self.runing: bool = True
        self.result: str = "quit"           # "quit" or "menu"
        self.paused: bool = False
        self.end_kind: Optional[str] = None  # "game_over" or "victory"

        # cheat mode (for the peer review)
        self.cheat_mode: bool = config.cheat_mode
        self.invincible: bool = config.cheat_mode
        self.freeze_ghosts: bool = False

        self.level_index: int = 0
        self.time_left: float = float(config.level_max_time)
        self.ready_left: float = 0.0        # > 0: waiting before the start
        self.banner: str = ""
        self.banner_sub: str = ""

        self.offset_x: int = 0
        self.offset_y: int = 0
        self.cell_size: int = 0

        self.player: Player = Player(0, 0, config.lives)
        self.state: GameState = GameState()
        self.hud: Hud = Hud()
        self.pause_menu: PauseMenu = PauseMenu()

        self.matrix: List[List[int]] = []
        self.maze: Maze
        self.ghosts: List[Ghost] = []
        self.packgum: Pacgum
        self.graphic: Renderer
        self.load_level()

    # ------------------------------------------------------------------
    # levels
    # ------------------------------------------------------------------

    def load_level(self) -> None:
        """Build the maze, the dots and the ghosts of the current level.

        The first level uses the seed of the config (always the same maze),
        the next levels use a random maze.
        """
        level = self.config.levels[self.level_index]
        seed = self.config.seed if self.level_index == 0 else None
        self.matrix = Maze.generate(level.width, level.height, seed)
        self.maze = Maze(self.matrix)

        row, col = self.maze.start_cell()
        self.player.new_level(col, row)
        self.ghosts = Ghost.create_all(self.maze)
        self.packgum = Pacgum(self.maze, self.player,
                              self.config.points_per_pacgum,
                              self.config.points_per_super_pacgum,
                              SUPERMODE_TIME)

        self.calculate_layout(margin=20)
        self.graphic = Renderer(self.matrix, self.screen, self.offset_x,
                                self.offset_y, self.cell_size, self.player)
        self.time_left = float(self.config.level_max_time)
        self.start_ready("READY!", f"Level {self.level_index + 1}")

    def start_ready(self, text: str, sub_text: str = "") -> None:
        """Freeze everybody for 2 seconds and show a message."""
        self.ready_left = READY_TIME
        self.banner = text
        self.banner_sub = sub_text

    def next_level(self) -> None:
        """Go to the next level, or finish the game (victory)."""
        self.level_index += 1
        if self.level_index >= len(self.config.levels):
            self.end_kind = "victory"
            return
        try:
            self.load_level()
        except Exception as err:        # MazeError or anything unexpected
            logging.error("Cannot load level %d: %s", self.level_index + 1,
                          err)
            self.end_kind = "game_over"

    # ------------------------------------------------------------------
    # layout (where the maze is drawn in the window)
    # ------------------------------------------------------------------

    def refresh_layout(self) -> None:
        """If the window size changed, recompute the maze layout."""
        screen = pg.display.get_surface()
        if screen is None:
            return
        self.screen = screen
        size = screen.get_size()
        if size != (self.window_width, self.window_height):
            self.window_width, self.window_height = size
            self.calculate_layout(margin=20)

    def calculate_layout(self, margin: int = 40) -> None:
        """Compute the cell size and put the maze in the middle."""
        usable_width = self.window_width - margin * 2
        usable_height = self.window_height - HUD_BAND - margin * 2

        # cells are squares: use the smallest of the two sizes
        cell_size = min(usable_width // self.maze.cols,
                        usable_height // self.maze.rows)
        self.cell_size = max(10, cell_size)     # never smaller than 10 px

        maze_width = self.maze.cols * self.cell_size
        maze_height = self.maze.rows * self.cell_size
        self.offset_x = (self.window_width - maze_width) // 2
        self.offset_y = margin + (usable_height - maze_height) // 2

    # ------------------------------------------------------------------
    # main loop
    # ------------------------------------------------------------------

    def run(self) -> str:
        """Play until the game ends. Returns "menu" or "quit"."""
        while self.runing:
            dt = min(self.clock.tick(60) / 1000.0, MAX_DT)

            self.refresh_layout()
            self.handle_event()
            if self.runing and not self.paused:
                self.update(dt)
            self.draw()
            pg.display.flip()

            if self.runing and self.end_kind is not None:
                self.finish_game()
        return self.result

    def update(self, dt: float) -> None:
        """Move everything. `dt` = seconds since the last frame."""
        if self.ready_left > 0:             # READY! : nobody moves
            self.ready_left -= dt
            return

        self.time_left -= dt
        if self.time_left <= 0:
            self.lose_life("TIME UP!", restart_timer=True)
            return

        self.update_supermode(dt)

        if self.player.update(dt, self.maze, PLAYER_STEP):
            self.eat_dots()
        self.check_collisions()
        if self.ready_left > 0 or self.end_kind:    # something happened
            return

        if not self.freeze_ghosts:
            for ghost in self.ghosts:
                step = EDIBLE_STEP if ghost.edible else GHOST_STEP
                ghost.update(dt, self.player, step)
            self.check_collisions()

    def update_supermode(self, dt: float) -> None:
        """Count the power time down and calm the ghosts at the end."""
        was_super = self.packgum.supermode
        self.packgum.update(dt)
        if was_super and not self.packgum.supermode:
            for ghost in self.ghosts:
                ghost.set_edible(False)
        blink = (self.packgum.supermode
                 and self.packgum.supermode_left < FLASH_TIME)
        for ghost in self.ghosts:
            ghost.flash = blink

    def eat_dots(self) -> None:
        """The player is in a new cell: eat the dot, check the win."""
        if self.packgum.eat_pacgum() == SUPER:
            for ghost in self.ghosts:
                ghost.set_edible(True)
        if self.packgum.all_eaten():
            self.next_level()

    def check_collisions(self) -> None:
        """A ghost and the player in the same cell: eat it or lose a life."""
        for ghost in self.ghosts:
            if ghost.state == EATEN:
                continue
            if (ghost.pos_x, ghost.pos_y) != (self.player.pos_x,
                                              self.player.pos_y):
                continue
            if ghost.edible:
                self.player.update_score(self.config.points_per_ghost)
                ghost.eat(RESPAWN_TIME)
            elif not self.invincible:
                self.lose_life("CAUGHT!")
                return

    def lose_life(self, text: str, restart_timer: bool = False) -> None:
        """One life less. No life left = game over, else try again.

        The dots already eaten stay eaten.
        """
        self.player.lives -= 1
        if self.player.lives <= 0:
            self.end_kind = "game_over"
            return
        self.player.reset_position()
        for ghost in self.ghosts:
            ghost.reset()
        self.packgum.supermode = False
        if restart_timer:
            self.time_left = float(self.config.level_max_time)
        self.start_ready(text, f"Lives left: {self.player.lives}")

    # ------------------------------------------------------------------
    # drawing
    # ------------------------------------------------------------------

    def draw(self) -> None:
        """Draw one frame (layers: later = on top)."""
        self.graphic.set_layout(self.screen, self.offset_x,
                                self.offset_y, self.cell_size)
        self.screen.fill("black")
        self.graphic.draw_maze()
        self.graphic.draw_pacgums(self.packgum.pacgums_state)
        self.graphic.draw_super_pacgums(self.packgum.super_pacgums_state)
        self.graphic.draw_ghosts(self.ghosts)
        self.graphic.draw_player()

        self.sync_state()
        self.hud.draw(self.screen, self.state, HUD_BAND)
        if self.ready_left > 0 and not self.paused:
            self.hud.draw_banner(self.screen, self.banner, self.banner_sub)
        if self.paused:
            self.pause_menu.draw(self.screen)

    def sync_state(self) -> None:
        """Copy the real numbers in the state read by the HUD."""
        self.state.score = self.player.score
        self.state.lives = self.player.lives
        self.state.level = self.level_index + 1
        self.state.level_count = len(self.config.levels)
        self.state.time_left = math.ceil(max(0.0, self.time_left))
        self.state.power_left = 0
        if self.packgum.supermode:
            self.state.power_left = math.ceil(self.packgum.supermode_left)
        self.state.cheat_text = self.cheat_text()

    def cheat_text(self) -> str:
        """The help line shown while the cheat mode is on."""
        if not self.cheat_mode:
            return ""
        invincible = "ON" if self.invincible else "off"
        frozen = "ON" if self.freeze_ghosts else "off"
        return (f"CHEAT  I: invincible {invincible} | "
                f"F: freeze ghosts {frozen} | N: next level | "
                f"L: +1 life | C: stop cheat")

    # ------------------------------------------------------------------
    # keyboard
    # ------------------------------------------------------------------

    def handle_event(self) -> None:
        """Read the keyboard and the window events."""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.runing = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_q:
                    self.runing = False
                elif self.paused:
                    self.handle_pause_key(event.key)
                else:
                    self.handle_game_key(event.key)

    def handle_game_key(self, key: int) -> None:
        """Keys while we play."""
        if key in (pg.K_p, pg.K_ESCAPE):
            self.paused = True
            self.pause_menu.selected = 0
        elif key == pg.K_r:
            self.result = "menu"          # go back to the menu
            self.runing = False
        elif key == pg.K_c:
            self.cheat_mode = not self.cheat_mode
            self.invincible = self.cheat_mode
            self.freeze_ghosts = False
        elif self.cheat_mode and key == pg.K_i:
            self.invincible = not self.invincible
        elif self.cheat_mode and key == pg.K_f:
            self.freeze_ghosts = not self.freeze_ghosts
        elif self.cheat_mode and key == pg.K_l:
            self.player.lives += 1
        elif self.cheat_mode and key == pg.K_n and self.ready_left <= 0:
            self.next_level()               # win the level right now
        elif key in KEY_TO_DIRECTION:
            self.player.set_direction(KEY_TO_DIRECTION[key])

    def handle_pause_key(self, key: int) -> None:
        """Keys while the game is paused."""
        if key == pg.K_p:
            action = "resume"
        else:
            action = self.pause_menu.handle_key(KEY_NAMES.get(key, ""))
        if action == "resume":
            self.paused = False
        elif action == "menu":
            self.result = "menu"
            self.runing = False

    # ------------------------------------------------------------------
    # end of the game
    # ------------------------------------------------------------------

    def ask_name(self, kind: str) -> Optional[str]:
        """Show the game over / victory screen. Returns the typed name.

        Returns None if the window was closed.
        """
        return EndScreen(kind, self.player.score).run()

    def finish_game(self) -> None:
        """Game over or victory: ask the name and save the score."""
        name = self.ask_name(self.end_kind or "game_over")
        if name is None:                  # window closed
            self.result = "quit"
        else:
            self.scoring.add(name, self.player.score)
            self.result = "menu"
        self.runing = False

    def get_top_players(self) -> List[Tuple[str, int]]:
        """The top 10 (name, score), best first."""
        return self.scoring.top()
