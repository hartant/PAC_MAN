import pygame as pg


pg.init()

screen = pg.display.set_mode((800, 600))
clock = pg.time.Clock()

run = True

print(type(pg.event))

i = 0
while run:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
    screen.fill("yellow")

    keys = pg.key.get_pressed()
    if keys[pg.K_q]:
        run = 0

    if i >= 100:
        pg.draw.circle(screen, "red", (400, 300), 30)

    if i >= 200:
        pg.draw.circle(screen, "red", (410, 310), 30)

    if i >= 300:
        pg.draw.circle(screen, "red", (420, 320), 30)

    if i >= 400:
        pg.draw.circle(screen, "red", (430, 330), 30)

    if i >= 500:
        pg.draw.circle(screen, "red", (430, 330), 30)

    pg.display.flip()
    clock.tick(60)
    print(f"index {i}")
    i += 1
pg.quit()
