import pygame as pg
from src.ui.graphics import Renderer
from src.logic.father import Player, Ghost
from src.logic.maze import Maze
from src.ui.hud import Hud
from src.ui.pause import PauseMenu
from src.ui.end_screen import EndScreen
from src.ui.menu import KEY_NAMES
from src.ui.fake_state import make_fake_state
from typing import List


# arrow keys and WASD -> direction of the move
KEY_TO_DIRECTION = {
    pg.K_UP: Maze.TOP, pg.K_w: Maze.TOP,
    pg.K_DOWN: Maze.BUTTOM, pg.K_s: Maze.BUTTOM,
    pg.K_LEFT: Maze.LEFT, pg.K_a: Maze.LEFT,
    pg.K_RIGHT: Maze.RIGHT, pg.K_d: Maze.RIGHT,
}


class GameEngine():
    def __init__(self, wx, wy, matrix, cheat_mode: bool = False):
        pg.init()
        self.matrix: List[List[int]] = matrix
        self.cheat_mode = cheat_mode
        # reuse the menu window; create it only if it does not exist
        screen = pg.display.get_surface()
        if screen is None:
            screen = pg.display.set_mode((wx, wy), pg.RESIZABLE)
        self.screen = screen
        self.window_width, self.window_height = screen.get_size()

        self.offset_x: int = 0
        self.offset_y: int = 0
        self.cell_size: int = 0

        self.calculate_layout(margin=20)
        self.runing: bool = True
        self.result: str = "quit"    # "quit" or "menu"
        self.clock = pg.time.Clock()

        self.maze = Maze(self.matrix)

        self.graphic = Renderer(self.matrix,
                                self.screen,
                                self.offset_x,
                                self.offset_y,
                                self.cell_size
                                )
        self.graphic.set_layout(self.screen, self.offset_x,
                                self.offset_y, self.cell_size)

        self.player = Player((len((self.matrix)) // 2,
                              len((self.matrix[0])) // 2),
                             len((self.matrix)) // 2,
                             len((self.matrix[0])) // 2, "Ahmed")

        self.ghosts: List[Ghost] = [
            Ghost(0, 0, "red", self.maze),
            Ghost(0, (len((self.matrix)) - 1), "pink", self.maze),
            Ghost((len(self.matrix[0]) - 1), 0, "cyan", self.maze),
            Ghost((len(self.matrix[0]) - 1), (len((self.matrix)) - 1),
                  "orange", self.maze)
        ]

        self.state = make_fake_state(self.matrix)
        self.hud = Hud()

        self.paused: bool = False
        self.player_name: str = ""
        self.pause_menu = PauseMenu()

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
        self.graphic.set_layout(self.screen, self.offset_x,
                                self.offset_y, self.cell_size)

    def calculate_layout(self, margin: int = 40) -> None:
        rows: int = len(self.matrix)
        cols: int = len(self.matrix[0])

        # Mssaha dyal l-HUD f l-t7t wla l-foq
        space: int = 60

        u_width = self.window_width - (margin * 2)
        u_height = (self.window_height - space) - (margin * 2)

        cell_size = min(
            u_width // cols,
            u_height // rows
        )

        # Check ila kan l-size sghir bzzaf (t-la3 mesg f terminal)
        if cell_size < 15:
            print("WARNING: Window size is too small! Maze tiles will be too tiny to display properly.")

        self.cell_size = max(10, cell_size)  # Safe minimum size

        maze_width = cols * self.cell_size
        maze_height = rows * self.cell_size

        # Hisab offsets bash l-maze y-ji m-sawwi f l-wast dyal l-fnatra
        self.offset_x = (self.window_width - maze_width) // 2
        self.offset_y = margin + ((self.window_height - space - (margin * 2)) - maze_height) // 2

    def run(self) -> str:
        # holding a key repeats the move: after 250 ms, then every 120 ms
        move_timer = 0.0
        move_interval = 0.12

        ghost_timer = 0.0
        ghost_intreval = 0.20

        pg.key.set_repeat(250, 120)
        while self.runing:
            dt = self.clock.tick(60) / 1000.0

            self.refresh_layout()
            self.handle_event()
            # self.check_end()

            move_timer += dt

            # this for the player
            while move_timer >= move_interval:
                self.player.move(self.maze)
                move_timer -= move_interval

            # this for the ghosts

            ghost_timer += dt

            while ghost_timer >= ghost_intreval:
                for ghost in self.ghosts:
                    ghost.move(
                        self.player.pos_y,
                        self.player.pos_x,
                    )
                ghost_timer -= ghost_intreval

            self.draw()
            self.touched_ghost()
            pg.display.flip()
        pg.key.set_repeat()      # turn the repeat off
        return self.result

    def draw(self):
        self.screen.fill("black")
        self.graphic.draw_maze()
        self.graphic.draw_pacgums(self.state.pacgums)
        self.graphic.draw_super_pacgums(self.state.super_pacgums)
        # self.graphic.draw_ghosts(self.state.ghosts)               # new
        self.graphic.draw_ghosts(self.ghosts, 0.5)               # new
        self.player_control()
        self.hud.draw(self.screen, self.state)
        if self.paused:
            self.pause_menu.draw(self.screen)

    def handle_event(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.runing = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_q:
                    self.runing = False
                if self.paused:
                    self.handle_pause_key(event.key)
                    continue
                if event.key in (pg.K_p, pg.K_ESCAPE):
                    self.paused = True
                    self.pause_menu.selected = 0
                if event.key == pg.K_r:
                    self.result = "menu"      # go back to the menu
                    self.runing = False
                if event.key == pg.K_g:
                    self.state.status = "game_over"
                if event.key == pg.K_v:
                    self.state.status = "victory"
                direction = KEY_TO_DIRECTION.get(event.key)
                if direction is not None:
                    # ONE key press = ONE cell
                    self.player.set_direction(direction)
                    # self.player.move(self.maze, direction)

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

    def update(self):
        pass

    def check_end(self) -> None: # I stop this and fake state for new and use game_over_x()
        """If the game is over (win or lose), ask the player's name."""
        if self.state.status not in ("game_over", "victory"):
            print(self.state.status)
            return
        end_screen = EndScreen(self.state.status, self.state.score)
        name = end_screen.run()
        if name is None:                  # window closed
            self.result = "quit"
        else:
            self.player_name = name
            # friend: save the score here, example:
            # save_highscore(name, self.state.score)
            self.result = "menu"
        self.runing = False

    def player_control(self):
        """Only draws the player (the move is done in handle_event)."""
        self.graphic.draw_player(self.player.pos_x, self.player.pos_y)

    def game_over_x(self) -> None:
        self.game_over: str = ""
        self.player.lives = 3
        print("Game over !!!")
        end_screen = EndScreen("Game over", 50)
        name = end_screen.run()
        if name is None:                  # window closed
            self.result = "quit"
        else:
            self.player_name = name
            print(self.player_name)
            self.result = "menu"

    def touched_ghost(self) -> None:
        self.game_over: str = ""
        for ghost in self.ghosts:
            if (self.player.pos_x == ghost.pos_x
               and self.player.pos_y == ghost.pos_y):
                if not self.cheat_mode:
                    self.player.lives -= 1
                    self.reset_entities_position()
                    print(f"Player lives: {self.player.lives}")
                if self.player.lives == 0:
                    self.game_over_x()

    def reset_entities_position(self) -> None:
        self.player.pos_x = len((self.matrix)) // 2
        self.player.pos_y = len((self.matrix[0])) // 2

        self.ghosts[0].pos_x = 0
        self.ghosts[0].pos_y = 0
        self.ghosts[1].pos_x = 0
        self.ghosts[1].pos_y = len((self.matrix)) - 1
        self.ghosts[2].pos_x = len(self.matrix[0]) - 1
        self.ghosts[2].pos_y = 0
        self.ghosts[3].pos_x = len(self.matrix[0]) - 1
        self.ghosts[3].pos_y = len((self.matrix)) - 1
