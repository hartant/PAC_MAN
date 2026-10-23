"""Main menu: logic (MainMenu) and pygame screens (MenuScreen)."""

from dataclasses import dataclass

import pygame as pg

YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
GREY = (150, 150, 150)
BLACK = (0, 0, 0)

# Real pygame keys -> simple names used by the menu logic
KEY_NAMES: dict[int, str] = {
    pg.K_UP: "up",
    pg.K_w: "up",
    pg.K_DOWN: "down",
    pg.K_s: "down",
    pg.K_RETURN: "enter",
    pg.K_KP_ENTER: "enter",
    pg.K_SPACE: "space",
    pg.K_ESCAPE: "escape",
}

INSTRUCTIONS: list[str] = [
    "Controls",
    "Arrow keys or WASD : move",
    "P : pause / resume",
    "Q : quit",
    "",
    "Rules",
    "Eat all the pacgums to win the level.",
    "Super-pacgums make the ghosts edible.",
    "A ghost touches you: you lose a life.",
    "No lives left: game over.",
]


@dataclass
class MenuItem:
    """One line of the menu."""

    label: str
    target: str  # screen to go to when this item is chosen


class MainMenu:
    """Menu logic only. It knows key names, not pygame."""

    def __init__(self) -> None:
        """Create the 4 menu items and select the first one."""
        self.items: list[MenuItem] = [
            MenuItem("Start Game", "playing"),
            MenuItem("View Highscores", "highscores"),
            MenuItem("Instructions", "instructions"),
            MenuItem("Exit", "quit"),
        ]
        self.selected: int = 0

    def handle_key(self, key: str) -> str:
        """React to a key name and return the screen to show next.

        Args:
            key: "up", "down", "enter" or "space" (others are ignored).

        Returns:
            "menu" if we stay here, else the target of the chosen item.
        """
        if key == "up":
            self.selected = (self.selected - 1) % len(self.items)
        elif key == "down":
            self.selected = (self.selected + 1) % len(self.items)
        elif key in ("enter", "space"):
            return self.items[self.selected].target
        return "menu"


class MenuScreen:
    """Draws the menu screens and runs their loop."""

    def __init__(self, screen: pg.Surface,
                 highscores: list[tuple[str, int]]) -> None:
        """Prepare fonts and state. pg.init() must already be called.

        Args:
            screen: the pygame window surface.
            highscores: list of (name, score), best first.
        """
        self.screen = screen
        self.highscores = highscores[:10]
        self.menu = MainMenu()
        self.current = "menu"
        self.clock = pg.time.Clock()
        self.font_title = pg.font.Font(None, 90)
        self.font_item = pg.font.Font(None, 44)
        self.font_small = pg.font.Font(None, 28)

    def draw_text(self, text: str, font: pg.font.Font, y: int,
                  color: tuple[int, int, int]) -> None:
        """Draw text centered horizontally at height y."""
        surface = font.render(text, True, color)
        rect = surface.get_rect(center=(self.screen.get_width() // 2, y))
        self.screen.blit(surface, rect)

    def draw_scores(self, start_y: int, step: int,
                    font: pg.font.Font) -> None:
        """Draw the highscore list (or a message if it is empty)."""
        if not self.highscores:
            self.draw_text("No scores yet", font, start_y, GREY)
            return
        for i, (name, score) in enumerate(self.highscores):
            self.draw_text(f"{i + 1}. {name} - {score} pts",
                           font, start_y + i * step, WHITE)

    def draw_menu(self) -> None:
        """Draw title, the 4 items and the top 10 scores."""
        self.draw_text("Pac-Man", self.font_title, 100, YELLOW)
        for i, item in enumerate(self.menu.items):
            if i == self.menu.selected:
                self.draw_text(f"> {item.label} <", self.font_item,
                               210 + i * 50, YELLOW)
            else:
                self.draw_text(item.label, self.font_item,
                               210 + i * 50, WHITE)
        self.draw_text("Push SPACE to play", self.font_small, 440, GREY)
        self.draw_text("highscores:", self.font_small, 490, WHITE)
        self.draw_scores(525, 26, self.font_small)

    def draw_highscores(self) -> None:
        """Draw the full highscores screen."""
        self.draw_text("Highscores", self.font_title, 100, YELLOW)
        self.draw_scores(200, 50, self.font_item)
        self.draw_text("Press any key to go back", self.font_small,
                       self.screen.get_height() - 40, GREY)

    def draw_instructions(self) -> None:
        """Draw the controls and rules."""
        self.draw_text("Instructions", self.font_title, 100, YELLOW)
        for i, line in enumerate(INSTRUCTIONS):
            color = YELLOW if line in ("Controls", "Rules") else WHITE
            self.draw_text(line, self.font_small, 200 + i * 40, color)
        self.draw_text("Press any key to go back", self.font_small,
                       self.screen.get_height() - 40, GREY)

    def handle_event(self, event: pg.event.Event) -> str | None:
        """Handle one pygame event.

        Returns:
            "playing" or "quit" when the menu is finished, else None.
        """
        if event.type == pg.QUIT:
            return "quit"
        if event.type != pg.KEYDOWN:
            return None
        if self.current == "menu":
            key = KEY_NAMES.get(event.key, "")
            nxt = self.menu.handle_key(key)
            if nxt in ("playing", "quit"):
                return nxt
            self.current = nxt
        else:  # highscores or instructions: any key goes back
            self.current = "menu"
        return None

    def run(self) -> str:
        """Run the menu loop until the player starts or quits.

        Returns:
            "playing" or "quit".
        """
        while True:
            for event in pg.event.get():
                result = self.handle_event(event)
                if result is not None:
                    return result
            self.screen.fill(BLACK)
            if self.current == "menu":
                self.draw_menu()
            elif self.current == "highscores":
                self.draw_highscores()
            else:
                self.draw_instructions()
            pg.display.flip()
            self.clock.tick(60)