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
FPS = 30
RED, GREEN, BLUE = (255, 0, 0), (0, 255, 0), (0, 0, 255)
WHITE, BLACK = (255, 255, 255), (0, 0, 0)
YELLOW, PURPLE = (255, 255, 0), (255, 0, 255)


def update_fps():
    fps = f'FPS: {int(CLOCK.get_fps())}'
    fps_text = FONT.render(fps, True, pg.Color("black"))
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
    obstacle_grid = load_map('maps/map4.png')
    pheromone_grid_food = np.zeros_like(obstacle_grid, dtype=float)
    pheromone_grid_hive = np.zeros_like(obstacle_grid, dtype=float)
    grid_height, grid_width = obstacle_grid.shape
    grid_ratio = grid_height / grid_width

    # Manually set food source and hive
    food_grid = np.zeros_like(obstacle_grid)
    hive_grid = np.zeros_like(obstacle_grid)
    food_grid[1, 1] = 1
    hive_grid[18, 18] = 1

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
    ants = [Ant(18, 18) for _ in range(3)]

    running = True

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    running = not running

        if running:
            for ant in ants:
                if food_grid[ant.y, ant.x] == 1:
                    ant.seek_hive()
                    ant.COUNTER = 1
                if hive_grid[ant.y, ant.x] == 1:
                    ant.seek_food()
                    ant.COUNTER = 1
                if ant.state == Ant.TO_HIVE:
                    pheromone_grid_food[ant.y, ant.x] += 1/ant.COUNTER
                else:
                    pheromone_grid_hive[ant.y, ant.x] += 1/ant.COUNTER

                ant.move(obstacle_grid, pheromone_grid_food, pheromone_grid_hive)

                # ant.COUNTER += 1

            print(pheromone_grid_hive.max())
            draw_scene(screen, grid_rect, block_size, ants, obstacle_grid, pheromone_grid_food, pheromone_grid_hive,
                       food_grid, hive_grid)

            pheromone_grid_food *= 0.98
            pheromone_grid_food[pheromone_grid_food < 0.01] = 0

            pheromone_grid_hive *= 0.98
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

    screen.blit(update_fps(), (10, 10))


class Ant:
    TO_FOOD = 0
    TO_HIVE = 1

    COUNTER = 1

    def __init__(self, x, y, direction=None):
        self.x = x
        self.y = y
        self.state = self.TO_FOOD
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
        possible_directions[self.direction] *= 10
        possible_directions[(self.direction + 1) % 4] *= 1
        possible_directions[(self.direction - 1) % 4] *= 1
        possible_directions[(self.direction + 2) % 4] *= 0.1

        # Weigh direction by pheromone.
        if self.state == self.TO_FOOD:
            possible_directions[directions.Right] *= 1 + np.exp(pheromone_grid_food[self.y, (self.x + 1)%width])
            possible_directions[directions.Left] *= 1 + np.exp(pheromone_grid_food[self.y, (self.x - 1)])
            possible_directions[directions.Up] *= 1 + np.exp(pheromone_grid_food[(self.y + 1)%height, self.x])
            possible_directions[directions.Down] *= 1 + np.exp(pheromone_grid_food[self.y - 1, self.x])
        elif self.state == self.TO_HIVE:
            possible_directions[directions.Right] *= 1 + np.exp(pheromone_grid_hive[self.y, (self.x + 1)%width])
            possible_directions[directions.Left] *= 1 + np.exp(pheromone_grid_hive[self.y, (self.x - 1)])
            possible_directions[directions.Up] *= 1 + np.exp(pheromone_grid_hive[(self.y + 1)%height, self.x])
            possible_directions[directions.Down] *= 1 + np.exp(pheromone_grid_hive[self.y - 1, self.x])
        else:
            raise Exception("Unknown state")

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

    def seek_hive(self):
        self.state = self.TO_HIVE

    def seek_food(self):
        self.state = self.TO_FOOD


if __name__ == '__main__':
    main()
