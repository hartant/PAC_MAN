import pygame as pg

from src.ui.name_input import NameInput

YELLOW = (255, 255, 0)
GREEN = (80, 255, 80)
RED = (255, 60, 60)
WHITE = (255, 255, 255)
GREY = (150, 150, 150)


class EndScreen:
    """Game over / victory screen where the player types a name."""

    def __init__(self, kind: str, score: int) -> None:
        """kind = "game_over" or "victory"."""
        self.kind = kind
        self.score = score
        self.name = NameInput()
        self.clock = pg.time.Clock()
        self.fonts: dict[int, pg.font.Font] = {}

    def font(self, size: int, scale: float) -> pg.font.Font:
        real = max(10, int(size * scale))
        if real not in self.fonts:
            self.fonts[real] = pg.font.Font(None, real)
        return self.fonts[real]

    def draw_text(self, screen: pg.Surface, text: str, size: int, y: int,
                  color: tuple[int, int, int]) -> None:
        w, h = screen.get_size()
        scale = max(0.3, min(w, h) / 800)
        surface = self.font(size, scale).render(text, True, color)
        rect = surface.get_rect(center=(w // 2, int(y * h / 800)))
        screen.blit(surface, rect)

    def draw(self, screen: pg.Surface) -> None:
        w, h = screen.get_size()
        scale = max(0.3, min(w, h) / 800)
        screen.fill((0, 0, 0))

        if self.kind == "victory":
            self.draw_text(screen, "VICTORY!", 110, 130, GREEN)
            self.draw_text(screen, "Congratulations! You finished all the "
                           "levels!", 36, 210, WHITE)
        else:
            self.draw_text(screen, "GAME OVER", 110, 130, RED)
        self.draw_text(screen, f"Final score: {self.score}", 56, 320, YELLOW)

        self.draw_text(screen, "Enter your name:", 40, 440, WHITE)
        box = pg.Rect(0, 0, int(460 * scale), int(60 * scale))
        box.center = (w // 2, int(520 * h / 800))
        pg.draw.rect(screen, WHITE, box, 2)
        cursor = "_" if pg.time.get_ticks() // 500 % 2 == 0 else " "
        self.draw_text(screen, self.name.text + cursor, 48, 520, YELLOW)

        self.draw_text(screen, "Max 10 letters, numbers or spaces", 26, 590,
                       GREY)
        self.draw_text(screen, "Press ENTER to save", 30, 700, GREY)

    def run(self) -> str | None:
        """Loop until the player presses ENTER with a valid name.

        Returns the name, or None if the window was closed.
        """
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return None
                if event.type != pg.KEYDOWN:
                    continue
                if event.key in (pg.K_RETURN, pg.K_KP_ENTER):
                    if self.name.is_valid():
                        pg.event.clear()
                        return self.name.result()
                elif event.key == pg.K_BACKSPACE:
                    self.name.backspace()
                else:
                    self.name.add_char(event.unicode)
            surface = pg.display.get_surface()
            if surface is not None:
                self.draw(surface)
            pg.display.flip()
            self.clock.tick(60)
