"""Simulation for ant colony path finding."""
import math
import time
from enum import Enum
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

    grid_width, grid_height = 50, 50
    obstacle_grid = np.zeros((grid_width, grid_height), dtype=bool)
    pheromone_grid = np.zeros((grid_width, grid_height, 2), dtype=np.float)


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


class Direction(Enum):
    Right: int = 0
    Up: int = 1
    Left: int = 2
    Down: int = 3


class Ant:
    def __init__(self, x, y, speed, direction=None):
        self.pos = pg.math.Vector2(x, y)
        if direction is None:
            self.direction = random.choice(list(Direction))
        else:
            self.direction = direction

    def move(self, obstacle_grid, pheromone_grid):

        # Choose direction
        possible_directions = np.array([1, 1, 1, 1])

        # Check if direction is blocked by wall.
        if self.pos.x == 0:
            possible_directions[Direction.Left.value] = 0
        elif self.pos.x == obstacle_grid.shape[1] - 1:
            possible_directions[Direction.Right.value] = 0
        if self.pos.y == 0:
            possible_directions[Direction.Down.value] = 0
        elif self.pos.y == obstacle_grid.shape[0] - 1:
            possible_directions[Direction.Up.value] = 0

        # Check if direction is blocked by obstacle.
        if obstacle_grid[self.pos.x+1, self.pos.y]:
            possible_directions[Direction.Right.value] = 0
        if obstacle_grid[self.pos.x-1, self.pos.y]:
            possible_directions[Direction.Left.value] = 0
        if obstacle_grid[self.pos.x, self.pos.y+1]:
            possible_directions[Direction.Up.value] = 0
        if obstacle_grid[self.pos.x, self.pos.y-1]:
            possible_directions[Direction.Down.value] = 0

        # Weigh direction by self.direction.
        # Todo: Maybe remove?
        possible_directions[self.direction.value] *= 0.5
        possible_directions[(self.direction.value + 1) % 4] *= 0.2
        possible_directions[(self.direction.value - 1) % 4] *= 0.2
        possible_directions[(self.direction.value + 2) % 4] *= 0.1

        # Weigh direction by pheromone.
        # Todo: implement

        possible_directions = possible_directions/sum(possible_directions)
        self.direction = np.random.choice(list(Direction), p=possible_directions)

        # Move
        if self.direction == Direction.Right:
            self.pos.x += 1
        elif self.direction == Direction.Up:
            self.pos.y += 1
        elif self.direction == Direction.Left:
            self.pos.x -= 1
        elif self.direction == Direction.Down:
            self.pos.y -= 1



if __name__ == '__main__':
    main()
