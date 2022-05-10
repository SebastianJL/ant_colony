"""Simulation for ant colony path finding."""
import random
import numpy as np

from PIL import Image

import directions
import pygame as pg

pg.init()
CLOCK = pg.time.Clock()
FONT = pg.font.SysFont("Arial", 18)
FPS = 60
RED, GREEN, BLUE = (255, 0, 0), (0, 255, 0), (0, 0, 255)
WHITE, BLACK = (255, 255, 255), (0, 0, 0)


def update_fps():
    fps = f'FPS: {int(CLOCK.get_fps())}'
    fps_text = FONT.render(fps, True, pg.Color("coral"))
    return fps_text


def load_map(filename) -> (np.ndarray, np.ndarray, np.ndarray):
    """Load map from image.

    The image is interpreted as a luminance image with any value smaller than 255
    interpreted as an obstacle.
    """

    with Image.open(filename) as img:
        img = img.convert('L')
        img_np = np.array(img)

    obstacles = img_np < 255
    return obstacles


def main():
    # Load map
    obstacle_grid = load_map('map.png')
    pheromone_grid = np.zeros_like(obstacle_grid, dtype=float)
    grid_height, grid_width = obstacle_grid.shape

    # Create screen
    info_object = pg.display.Info()
    SCREEN_WIDTH, SCREEN_HEIGHT = info_object.current_w//2, info_object.current_h//2
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # Create rectangles representing the screen and the grid.
    screen_rect = screen.get_rect()
    grid_rect = pg.rect.Rect(0, 0, grid_width, grid_height).fit(screen_rect)

    # Create ants
    ants = [Ant(grid_width//2, grid_height//2) for _ in range(1000)]

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()

        for ant in ants:
            pheromone_grid[ant.x, ant.y] += 1
            ant.move(obstacle_grid)

        draw_scene(screen, grid_rect, ants, obstacle_grid, pheromone_grid)

        pheromone_grid *= 0.9
        pheromone_grid[pheromone_grid < 0.01] = 0
        # pheromone_grid = pheromone_grid.clip(0, None)

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

    # Draw pheromones.
    for (x, y) in np.argwhere(pheromone_grid):
        pheromone_rect = pg.Rect(
            left + y*block_size, top + x*block_size,
            block_size, block_size)
        pg.draw.rect(screen, GREEN, pheromone_rect)

    # Draw ants.
    for ant in ants:
        ant_rect = pg.Rect(
            left + ant.y*block_size, top + ant.x*block_size,
            block_size, block_size)
        pg.draw.rect(screen, BLUE, ant_rect)

    # Draw obstacles.
    for (x, y) in np.argwhere(obstacle_grid):
        obstacle_rect = pg.Rect(
            left + y*block_size, top + x*block_size,
            block_size, block_size)
        pg.draw.rect(screen, BLACK, obstacle_rect)

    # TODO: Draw food.

    screen.blit(update_fps(), (10, 0))


class Ant:
    def __init__(self, x, y, direction=None):
        self.x = x
        self.y = y
        if direction is None:
            self.direction = np.random.choice(directions.directions)
        else:
            self.direction = direction

    def move(self, obstacle_grid):

        # Choose direction
        possible_directions = np.array([1, 1, 1, 1], dtype=float)

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

        # Prefer current direction.
        possible_directions[self.direction] *= 3
        possible_directions[(self.direction + 1) % 4] *= 0.4
        possible_directions[(self.direction - 1) % 4] *= 0.4
        possible_directions[(self.direction + 2) % 4] *= 0.1

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
