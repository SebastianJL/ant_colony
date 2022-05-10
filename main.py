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
YELLOW, PURPLE = (255, 255, 0), (255, 0, 255)


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
    pheromone_grid_food = np.zeros_like(obstacle_grid, dtype=float)
    pheromone_grid_hive = np.zeros_like(obstacle_grid, dtype=float)
    grid_height, grid_width = obstacle_grid.shape
    grid_ratio = grid_height / grid_width

    # Manually set food source and hive
    food_grid = np.zeros_like(obstacle_grid)
    hive_grid = np.zeros_like(obstacle_grid)
    food_grid[50, 100] = 1
    hive_grid[grid_height//2, grid_width//2] = 1

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
    ants = [Ant(grid_width//2, grid_height//2) for _ in range(500)]

    # Ant states
    to_food = 0
    to_hive = 1

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()

        for ant in ants:
            if food_grid[ant.y, ant.x] == 1:
                ant.switch_state_food()
            if hive_grid[ant.y, ant.x] == 1:
                ant.switch_state_hive()
            if ant.state == to_food:
                pheromone_grid_food[ant.y, ant.x] += 1
            else:
                pheromone_grid_hive[ant.y, ant.x] += 1

            ant.move(obstacle_grid, pheromone_grid_food, pheromone_grid_hive)

        draw_scene(screen, grid_rect, block_size, ants, obstacle_grid, pheromone_grid_food, pheromone_grid_hive,
                   food_grid, hive_grid)

        pheromone_grid_food *= 0.9
        pheromone_grid_food[pheromone_grid_food < 0.01] = 0

        pheromone_grid_hive *= 0.9
        pheromone_grid_hive[pheromone_grid_hive < 0.01] = 0
        # pheromone_grid = pheromone_grid.clip(0, None)

        CLOCK.tick(FPS)
        pg.display.flip()


def draw_scene(screen, grid_rect, block_size, ants, obstacle_grid, pheromone_grid_food, pheromone_grid_hive,
               food_grid, hive_grid):
    """Draw ants, obstacles and pheromones."""
    grid_width, grid_height = obstacle_grid.shape
    top, left = grid_rect.top, grid_rect.left

    # Draw background and grid background.
    screen.fill(pg.color.Color('black'))
    pg.draw.rect(screen, (130, 130, 130), grid_rect)

    # Draw food pheromones.
    for (y, x) in np.argwhere(pheromone_grid_food):
        pheromone_rect = pg.Rect(
            left + x*block_size, top + y*block_size,
            block_size, block_size)
        pg.draw.rect(screen, GREEN, pheromone_rect)

    # Draw hive pheromones.
    for (y, x) in np.argwhere(pheromone_grid_hive):
        pheromone_rect = pg.Rect(
            left + x * block_size, top + y * block_size,
            block_size, block_size)
        pg.draw.rect(screen, RED, pheromone_rect)

    # Draw ants.
    for ant in ants:
        ant_rect = pg.Rect(
            left + ant.x*block_size, top + ant.y*block_size,
            block_size, block_size)
        pg.draw.rect(screen, BLUE, ant_rect)

    # Draw obstacles.
    for (y, x) in np.argwhere(obstacle_grid):
        obstacle_rect = pg.Rect(
            left + x*block_size, top + y*block_size,
            block_size, block_size)
        pg.draw.rect(screen, BLACK, obstacle_rect)

    # Draw food.
    for (y, x) in np.argwhere(food_grid):
        obstacle_rect = pg.Rect(
            left + x*block_size, top + y*block_size,
            block_size, block_size)
        pg.draw.rect(screen, YELLOW, obstacle_rect)

    # Draw hive.
    for (y, x) in np.argwhere(hive_grid):
        obstacle_rect = pg.Rect(
            left + x * block_size, top + y * block_size,
            block_size, block_size)
        pg.draw.rect(screen, PURPLE, obstacle_rect)

    screen.blit(update_fps(), (10, 0))


class Ant:
    def __init__(self, x, y, direction=None):
        to_food = 0
        to_hive = 1
        self.x = x
        self.y = y
        self.state = to_food
        if direction is None:
            self.direction = np.random.choice(directions.directions)
        else:
            self.direction = direction

    def move(self, obstacle_grid, pheromone_grid_food, pheromone_grid_hive):

        # Choose direction
        possible_directions = np.array([1, 1, 1, 1], dtype=float)

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

        # Prefer current direction.
        possible_directions[self.direction] *= 3
        possible_directions[(self.direction + 1) % 4] *= 0.4
        possible_directions[(self.direction - 1) % 4] *= 0.4
        possible_directions[(self.direction + 2) % 4] *= 0.1

        # Weigh direction by pheromone.
        to_food = 0
        to_hive = 1
        if self.state == to_food:
            possible_directions[directions.Right] *= 1 + pheromone_grid_food[self.y, (self.x + 1)%width]
            possible_directions[directions.Left] *= 1 + pheromone_grid_food[self.y, (self.x - 1)]
            possible_directions[directions.Up] *= 1 + pheromone_grid_food[(self.y + 1)%height, self.x]
            possible_directions[directions.Down] *= 1 + pheromone_grid_food[self.y - 1, self.x]

        if self.state == to_hive:
            possible_directions[directions.Right] *= 1 + pheromone_grid_hive[self.y, (self.x + 1)%width]
            possible_directions[directions.Left] *= 1 + pheromone_grid_hive[self.y, (self.x - 1)]
            possible_directions[directions.Up] *= 1 + pheromone_grid_hive[(self.y + 1)%height, self.x]
            possible_directions[directions.Down] *= 1 + pheromone_grid_hive[self.y - 1, self.x]


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

    def switch_state_food(self):
        to_food = 0
        to_hive = 1
        if self.state == to_food:
            self.state = to_hive

    def switch_state_hive(self):
        to_food = 0
        to_hive = 1
        if self.state == to_hive:
            self.state = to_food

if __name__ == '__main__':
    main()
