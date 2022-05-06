"""Simulation for ant colony path finding."""
import math
import time
from random import random

import pygame as pg

pg.init()
CLOCK = pg.time.Clock()
FONT = pg.font.SysFont("Arial", 18)
FPS = 60
RATIO = 16/9
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = int(SCREEN_WIDTH/RATIO)
SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)


def update_fps():
    fps = f'FPS: {int(CLOCK.get_fps())}'
    fps_text = FONT.render(fps, True, pg.Color("coral"))
    return fps_text


def main():
    black = 0, 0, 0

    screen = pg.display.set_mode(SIZE)


    ants = [Ant(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, speed=120) for _ in range(5000)]
    prev_time = time.perf_counter()

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()

        screen.fill(pg.color.Color('white'))
        screen.blit(update_fps(), (10, 0))

        dt = time.perf_counter() - prev_time
        prev_time = time.perf_counter()
        for ant in ants:
            ant.update(dt)
            ant.draw(screen)

        CLOCK.tick(FPS)
        pg.display.flip()


class Ant:
    def __init__(self, x, y, speed, direction=None):
        self.pos = pg.math.Vector2(x, y)
        if direction is None:
            self.direction = random() * 2 * math.pi
        else:
            self.direction = direction
        self.color = 0, 0, 255
        self.time = CLOCK.get_time()
        self.speed = speed

    def draw(self, screen):
        pg.draw.circle(screen, self.color, self.pos, 10)

    def move(self, dt):
        self.pos.x += math.cos(self.direction) * dt * self.speed
        self.pos.y += math.sin(self.direction) * dt * self.speed

        if self.pos.x < 0:
            self.pos.x = 0
            self.direction = math.pi - self.direction
        elif self.pos.x > SCREEN_WIDTH:
            self.pos.x = SCREEN_WIDTH
            self.direction = math.pi - self.direction
        if self.pos.y < 0:
            self.pos.y = 0
            self.direction = -self.direction
        elif self.pos.y > SCREEN_HEIGHT:
            self.pos.y = SCREEN_HEIGHT
            self.direction = -self.direction

    def update(self, dt):
        self.direction += random() * math.pi - math.pi/2
        self.move(dt)


if __name__ == '__main__':
    main()
