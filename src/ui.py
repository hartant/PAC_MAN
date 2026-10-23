import pygame as pg


YELLOW = (255, 255, 0)


# class Button():
#     @staticmethod
#     def draw_centered(screen: pg.Surface,
#                       font: pg.font.Font,
#                       text: str,
#                       y: int,
#                       color: tuple[int, int, int]) -> None:
#         surface = font.render(text, True, color)
#         rect = surface.get_rect(center=(screen.get_width() // 2, y))
#         screen.blit(surface, rect)


class Render():
    def __init__(self):
        self.run = True
        self.clock = pg.time.Clock()
        self.win = (800, 800)
        self.screen = pg.display.set_mode(self.win)
        self.offset_x: int = 0
        self.offset_y: int = 0
        self._small = pg.font.Font(None, 28)
        self.lines: list = ["Start Game",
                            "View Highscores",
                            "Instructions", "Exit"]

    @staticmethod
    def draw_centered(screen: pg.Surface,
                      font: pg.font.Font,
                      text: str,
                      y: int,
                      color: tuple[int, int, int]) -> None:
        surface = font.render(text, True, color)
        rect = surface.get_rect(center=(screen.get_width() // 2, y))
        screen.blit(surface, rect)

    def main(self):
        while self.run:
            self.screen.fill("black")
            for event in pg.event.get():
                if event.type == pg.quit:
                    self.run = False

            keys = pg.key.get_pressed()
            self.draw_menu()

            if keys[pg.K_q]:
                self.run = False

            pg.display.flip()
            self.clock.tick(60)

    def draw_menu(self):
        for i, line in enumerate(self.lines):
            self.draw_centered(self.screen,
                               self._small,
                               line,
                               200 + i * 45,
                               YELLOW)


# class Menu():
#     def __init__(self):
#         pass

if __name__ == "__main__":
    pg.init()
    start = Render()
    start.main()
    pg.quit()
