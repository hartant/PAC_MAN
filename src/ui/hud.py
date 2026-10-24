import pygame as pg

from src.ui.fake_state import FakeState

YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
RED = (255, 60, 60)


class Hud:
    def __init__(self) -> None:
        self.font = pg.font.Font(None, 32)

    def draw_text(self, screen: pg.Surface, text: str, cx: int, cy: int,
                  color: tuple[int, int, int] = WHITE) -> None:
        surface = self.font.render(text, True, color)
        screen.blit(surface, surface.get_rect(center=(cx, cy)))

    def draw_lives(self, screen: pg.Surface, lives: int,
                   cx: int, cy: int) -> None:
        gap = 26
        start = cx - (lives - 1) * gap // 2
        for i in range(lives):
            pg.draw.circle(screen, YELLOW, (start + i * gap, cy), 9)

    def draw(self, screen: pg.Surface, state: FakeState,
             band: int = 60) -> None:
        w, h = screen.get_size()
        cy = h - band // 2
        minutes, seconds = divmod(max(0, state.time_left), 60)
        low_time = state.time_left <= 10

        self.draw_text(screen, f"Score: {state.score}", int(w * 0.14), cy)
        self.draw_text(screen, "Lives:", int(w * 0.36), cy)
        self.draw_lives(screen, state.lives, int(w * 0.36) + 90, cy)
        self.draw_text(screen, f"Level: {state.level}", int(w * 0.65), cy)
        self.draw_text(screen, f"Time: {minutes}:{seconds:02d}",
                       int(w * 0.86), cy, RED if low_time else WHITE)
