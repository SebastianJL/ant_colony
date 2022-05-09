"""Simulation for ant colony path finding."""
from enum import Enum
import numpy as np
import time

import pygame as pg

pg.init()
CLOCK = pg.time.Clock()
FONT = pg.font.SysFont("Arial", 18)
FPS = 60


def update_fps():
    fps = f'FPS: {int(CLOCK.get_fps())}'
    fps_text = FONT.render(fps, True, pg.Color("coral"))
    return fps_text


def main():

    grid_width, grid_height = 100, 100
    screensize_multiplier = 4
    obstacle_grid = np.zeros((grid_width, grid_height), dtype=bool)
    pheromone_grid = np.zeros((grid_width, grid_height, 2), dtype=float)

    screen = pg.display.set_mode((grid_width * screensize_multiplier, grid_height * screensize_multiplier))

    ants = [Ant(grid_width//2, grid_height//2, speed=120) for _ in range(5000)]
    prev_time = time.perf_counter()

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()

        screen.fill(pg.color.Color('black'))
        screen.blit(update_fps(), (10, 0))

        dt = time.perf_counter() - prev_time
        prev_time = time.perf_counter()
        for ant in ants:
            ant.move(obstacle_grid, pheromone_grid)
            pg.draw.rect(screen, (0, 0, 255), pg.Rect(ant.pos.x*screensize_multiplier,
                                                      ant.pos.y*screensize_multiplier,
                                                      screensize_multiplier,
                                                      screensize_multiplier))
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
            self.direction = np.random.choice(list(Direction))
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
        if self.pos.x != obstacle_grid.shape[1]-1:
            if obstacle_grid[int(self.pos.x)+1, int(self.pos.y)]:
                possible_directions[Direction.Right.value] = 0
        if self.pos.x != 0:
            if obstacle_grid[int(self.pos.x)-1, int(self.pos.y)]:
                possible_directions[Direction.Left.value] = 0
        if self.pos.y != obstacle_grid.shape[0]-1:
            if obstacle_grid[int(self.pos.x), int(self.pos.y)+1]:
                possible_directions[Direction.Up.value] = 0
        if self.pos.y != 0:
            if obstacle_grid[int(self.pos.x), int(self.pos.y)-1]:
                possible_directions[Direction.Down.value] = 0

        # Weigh direction by self.direction.
        # Todo: Maybe remove? -> current implementation causes NaN values
        #possible_directions[self.direction.value] *= 0.5
        #possible_directions[(self.direction.value + 1) % 4] *= 0.2
        #possible_directions[(self.direction.value - 1) % 4] *= 0.2
        #possible_directions[(self.direction.value + 2) % 4] *= 0.1

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
