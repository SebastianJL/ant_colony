"""Simulation for ant colony path finding."""
import random
import numpy as np
import time
import directions
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

    grid_width, grid_height = 50, 50
    screensize_multiplier = 8
    obstacle_grid = np.zeros((grid_width, grid_height), dtype=bool)
    obstacle_grid[0, :] = True
    obstacle_grid[:, 0] = True
    pheromone_grid = np.zeros((grid_width, grid_height, 2), dtype=float)

    info_object = pg.display.Info()
    SCREEN_WIDTH, SCREEN_HEIGHT = info_object.current_w//2, info_object.current_h//2
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    screen_rect = screen.get_rect()
    grid_rect = pg.rect.Rect(0, 0, grid_width, grid_height).fit(screen_rect)

    ants = [Ant(grid_width//2, grid_height//2, speed=120) for _ in range(1000)]

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()

        for ant in ants:
            ant.move(obstacle_grid, pheromone_grid)

        draw_scene(screen, grid_rect, ants, obstacle_grid, pheromone_grid)

        CLOCK.tick(FPS)
        pg.display.flip()


def draw_scene(screen, grid_rect, ants, obstacle_grid, pheromone_grid):
    """Draw ants, obstacles and pheromones."""
    grid_width, grid_height = obstacle_grid.shape
    block_size = grid_rect.width//grid_width
    top, left = grid_rect.top, grid_rect.left

    # Draw background and grid background.
    screen.fill(pg.color.Color('black'))
    pg.draw.rect(screen, (130, 130, 130), grid_rect)

    # Draw ants.
    for ant in ants:
        ant_rect = pg.Rect(
            left + ant.y*block_size, top + ant.x*block_size,
            block_size, block_size)
        pg.draw.rect(screen, (0, 0, 255), ant_rect)

    # TODO: Draw obstacles
    # TODO: draw pheromones

    screen.blit(update_fps(), (10, 0))


class Ant:
    def __init__(self, x, y, speed, direction=None):
        self.x = x
        self.y = y
        if direction is None:
            self.direction = np.random.choice(directions.directions)
        else:
            self.direction = direction

    def move(self, obstacle_grid, pheromone_grid):

        # Choose direction
        possible_directions = np.array([1, 1, 1, 1])

        # Check if direction is blocked by obstacle.
        height, width = obstacle_grid.shape
        if obstacle_grid[(self.x + 1)%width, self.y]:
            possible_directions[directions.Right] = 0
        if obstacle_grid[(self.x - 1), self.y]:
            possible_directions[directions.Left] = 0
        if obstacle_grid[self.x, (self.y + 1)%height]:
            possible_directions[directions.Up] = 0
        if obstacle_grid[self.x, self.y - 1]:
            possible_directions[directions.Down] = 0

        # Weigh direction by self.direction.
        # Todo: Maybe remove? -> current implementation causes NaN values
        # possible_directions[self.direction.value] *= 0.5
        # possible_directions[(self.direction.value + 1) % 4] *= 0.2
        # possible_directions[(self.direction.value - 1) % 4] *= 0.2
        # possible_directions[(self.direction.value + 2) % 4] *= 0.1

        # Weigh direction by pheromone.
        # Todo: implement

        possible_directions = possible_directions/sum(possible_directions)
        self.direction = random.choices(directions.directions, weights=possible_directions)[0]

        # Move
        if self.direction == directions.Right:
            self.x = (self.x + 1)%width
        elif self.direction == directions.Up:
            self.y = (self.y + 1)%height
        elif self.direction == directions.Left:
            self.x = (self.x - 1)%width
        elif self.direction == directions.Down:
            self.y = (self.y - 1)%height


if __name__ == '__main__':
    main()
