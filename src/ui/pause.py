import pygame as pg

YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
GREY = (150, 150, 150)


class PauseMenu:
    def __init__(self) -> None:
        # (text on screen, answer we give back)
        self.items: list[tuple[str, str]] = [
            ("Resume", "resume"),
            ("Return to main menu", "menu"),
        ]
        self.selected: int = 0
        self.fonts: dict[int, pg.font.Font] = {}

    def handle_key(self, key: str) -> str:
        """key = "up", "down", "enter", "space" or "escape".

        Returns "pause" (stay paused), "resume" or "menu".
        """
        if key == "up":
            self.selected = (self.selected - 1) % len(self.items)
        elif key == "down":
            self.selected = (self.selected + 1) % len(self.items)
        elif key in ("enter", "space"):
            return self.items[self.selected][1]
        elif key == "escape":
            return "resume"
        return "pause"

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
        # dark see-through layer over the game
        shade = pg.Surface(screen.get_size(), pg.SRCALPHA)
        shade.fill((0, 0, 0, 170))
        screen.blit(shade, (0, 0))

        self.draw_text(screen, "Paused", 90, 250, YELLOW)
        for i, (label, _) in enumerate(self.items):
            if i == self.selected:
                self.draw_text(screen, f"> {label} <", 44,
                               370 + i * 60, YELLOW)
            else:
                self.draw_text(screen, label, 44, 370 + i * 60, WHITE)
        self.draw_text(screen, "P or ESC to resume", 28, 720, GREY)
