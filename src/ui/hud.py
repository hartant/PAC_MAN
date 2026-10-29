"""Bottom bar (score, lives, level, time), top messages and big banners."""

import pygame as pg

from src.ui.game_state import GameState

YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
RED = (255, 60, 60)
BLUE = (90, 160, 255)
ORANGE = (255, 170, 40)

MAX_ICONS = 5           # more lives than this are shown as "x 7"


class Hud:
    """Draws the information of the game on the screen."""

    def __init__(self) -> None:
        """Create the fonts. pg.init() must already be called."""
        self.font = pg.font.Font(None, 32)
        self.small = pg.font.Font(None, 24)
        self.banner_fonts: dict[int, pg.font.Font] = {}

    def draw_text(self, screen: pg.Surface, text: str, cx: int, cy: int,
                  color: tuple[int, int, int] = WHITE,
                  small: bool = False) -> None:
        """Draw a text centered on (cx, cy)."""
        font = self.small if small else self.font
        surface = font.render(text, True, color)
        screen.blit(surface, surface.get_rect(center=(cx, cy)))

    def draw_lives(self, screen: pg.Surface, lives: int,
                   cx: int, cy: int) -> None:
        """One yellow circle per life (or one circle and "x N")."""
        if lives > MAX_ICONS:
            pg.draw.circle(screen, YELLOW, (cx - 20, cy), 9)
            self.draw_text(screen, f"x {lives}", cx + 14, cy)
            return
        gap = 26
        start = cx - (lives - 1) * gap // 2
        for i in range(lives):
            pg.draw.circle(screen, YELLOW, (start + i * gap, cy), 9)

    def draw(self, screen: pg.Surface, state: GameState,
             band: int = 60) -> None:
        """Draw the bottom bar and the small messages at the top."""
        w, h = screen.get_size()
        cy = h - band // 2
        minutes, seconds = divmod(max(0, state.time_left), 60)
        low_time = state.time_left <= 10

        self.draw_text(screen, f"Score: {state.score}", int(w * 0.14), cy)
        self.draw_text(screen, "Lives:", int(w * 0.36), cy)
        self.draw_lives(screen, state.lives, int(w * 0.36) + 90, cy)
        self.draw_text(screen, f"Level: {state.level}/{state.level_count}",
                       int(w * 0.65), cy)
        self.draw_text(screen, f"Time: {minutes}:{seconds:02d}",
                       int(w * 0.86), cy, RED if low_time else WHITE)

        if state.power_left > 0:
            self.draw_text(screen, f"POWER {state.power_left}", int(w * 0.5),
                           14, BLUE)
        if state.cheat_text:
            self.draw_text(screen, state.cheat_text, int(w * 0.5), h - 8,
                           ORANGE, small=True)

    def banner_font(self, size: int) -> pg.font.Font:
        """A big font (kept in a cache, like in the menu)."""
        if size not in self.banner_fonts:
            self.banner_fonts[size] = pg.font.Font(None, size)
        return self.banner_fonts[size]

    def draw_banner(self, screen: pg.Surface, text: str,
                    sub_text: str = "",
                    color: tuple[int, int, int] = YELLOW) -> None:
        """A big message in the middle of the screen (READY!, ...)."""
        w, h = screen.get_size()
        size = max(30, min(w, h) // 8)
        band = pg.Surface((w, size * 2), pg.SRCALPHA)
        band.fill((0, 0, 0, 190))
        top = h // 2 - size
        screen.blit(band, (0, top))
        title = self.banner_font(size).render(text, True, color)
        screen.blit(title, title.get_rect(center=(w // 2, h // 2 - size // 5)))
        if sub_text:
            small = self.banner_font(max(20, size // 3)).render(
                sub_text, True, WHITE)
            screen.blit(small, small.get_rect(
                center=(w // 2, h // 2 + size // 2 + size // 8)))
