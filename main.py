"""Simulation for ant colony path finding."""
import random
import numpy as np

from PIL import Image

import directions
import pygame as pg

pg.init()
pg.display.set_caption("Ant Simulation")
pygame_icon = pg.image.load("ant.png")
pg.display.set_icon(pygame_icon)
CLOCK = pg.time.Clock()
FONT = pg.font.SysFont("Arial", 16)
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
    obstacle_grid = load_map('maps/map2.png')
    pheromone_grid = np.zeros_like(obstacle_grid)
    grid_height, grid_width = obstacle_grid.shape
    grid_ratio = grid_height / grid_width

    # Create screen
    info_object = pg.display.Info()
    SCREEN_WIDTH, SCREEN_HEIGHT = info_object.current_w//2, info_object.current_h//2
    screen_ratio = SCREEN_HEIGHT / SCREEN_WIDTH

    if grid_ratio > screen_ratio:
        block_size = SCREEN_HEIGHT // grid_height
    else:
        block_size = SCREEN_WIDTH // grid_width

    screen = pg.display.set_mode((grid_width * block_size, grid_height * block_size))

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
            ant.move(obstacle_grid, pheromone_grid)

        draw_scene(screen, grid_rect, ants, obstacle_grid, block_size)

        CLOCK.tick(FPS)
        pg.display.flip()


def draw_scene(screen, grid_rect, ants, obstacle_grid, block_size):
    """Draw ants, obstacles and pheromones."""
    grid_width, grid_height = obstacle_grid.shape
    top, left = grid_rect.top, grid_rect.left

    # Draw background and grid background.
    screen.fill(pg.color.Color('black'))
    pg.draw.rect(screen, (130, 130, 130), grid_rect)

    # Draw ants.
    for ant in ants:
        ant_rect = pg.Rect(
            left + ant.x*block_size, top + ant.y*block_size,
            block_size, block_size)
        pg.draw.rect(screen, BLUE, ant_rect)

    for (x, y) in np.argwhere(obstacle_grid):
        obstacle_rect = pg.Rect(
            left + y*block_size, top + x*block_size,
            block_size, block_size)
        pg.draw.rect(screen, GREEN, obstacle_rect)

    # TODO: draw pheromones
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

    def move(self, obstacle_grid, pheromone_grid):

        # Choose direction
        possible_directions = np.array([1, 1, 1, 1])

        # Check if direction is blocked by obstacle.
        height, width = obstacle_grid.shape
        if obstacle_grid[self.y, (self.x + 1)%width]:
            possible_directions[directions.Right] = 0
        if obstacle_grid[self.y, (self.x - 1)]:
            possible_directions[directions.Left] = 0
        if obstacle_grid[(self.y + 1)%height, self.x]:
            possible_directions[directions.Up] = 0
        if obstacle_grid[self.y - 1, self.x]:
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
