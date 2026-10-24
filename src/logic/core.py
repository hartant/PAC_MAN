import pygame as pg
from src.ui.graphics import Renderer
from src.logic.father import Player
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
    def __init__(self, wx, wy, matrix):
        pg.init()
        self.matrix: List[List[int]] = matrix

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

        self.player = Player((0, 0), 0, 0, "Ahmed")

       
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
        pg.key.set_repeat(250, 120)
        while self.runing:
            self.refresh_layout()
            self.handle_event()
            self.check_end
            self.check_end()
            

            self.draw()
            pg.display.flip()
            self.clock.tick(60)
        pg.key.set_repeat()      # turn the repeat off
        return self.result

    def draw(self):
        self.screen.fill("black")
        self.graphic.draw_maze()
        self.graphic.draw_pacgums(self.state.pacgums)
        self.graphic.draw_super_pacgums(self.state.super_pacgums)
        self.graphic.draw_ghosts(self.state.ghosts)               # new
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
                    self.player.move(self.maze, direction)

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
    
    def check_end(self) -> None:
        """If the game is over (win or lose), ask the player's name."""
        if self.state.status not in ("game_over", "victory"):
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