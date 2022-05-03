"""Simulation for ant colony path finding."""
import math
import time
from random import random

import pygame as pg

pg.init()
clock = pg.time.Clock()
font = pg.font.SysFont("Arial", 18)
fps = 60
ratio = 16/9
width = 1200
height = int(width/ratio)
size = (width, height)


def update_fps():
    fps = f'FPS: {int(clock.get_fps())}'
    fps_text = font.render(fps, True, pg.Color("coral"))
    return fps_text


def main():
    black = 0, 0, 0

    screen = pg.display.set_mode(size)

    ants = [Ant(width//2, height//2, speed=120) for _ in range(5000)]
    prev_time = time.perf_counter()

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()

        screen.fill(black)
        screen.blit(update_fps(), (10, 0))

        dt = time.perf_counter() - prev_time
        prev_time = time.perf_counter()
        for ant in ants:
            ant.update(dt)
            ant.draw(screen)

        clock.tick(fps)
        pg.display.flip()


class Ant:
    def __init__(self, x, y, speed, direction=None):
        self.pos = pg.math.Vector2(x, y)
        if direction is None:
            self.direction = random() * 2 * math.pi
        else:
            self.direction = direction
        self.color = 0, 0, 255
        self.time = clock.get_time()
        self.speed = speed

    def draw(self, screen):
        pg.draw.circle(screen, self.color, self.pos, 10)

    def move(self, dt):
        self.pos.x += math.cos(self.direction) * dt * self.speed
        self.pos.y += math.sin(self.direction) * dt * self.speed

        if self.pos.x < 0:
            self.pos.x = 0
            self.direction = math.pi - self.direction
        elif self.pos.x > width:
            self.pos.x = width
            self.direction = math.pi - self.direction
        if self.pos.y < 0:
            self.pos.y = 0
            self.direction = -self.direction
        elif self.pos.y > height:
            self.pos.y = height
            self.direction = -self.direction

    def update(self, dt):
        self.direction += random() * math.pi - math.pi/2
        self.move(dt)


if __name__ == '__main__':
    main()
