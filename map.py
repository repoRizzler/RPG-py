from context.context import *
import pygame
class Map:
    def __init__(self, width, height):
        self.width = width  # Grid width
        self.height = height  # Grid height
        # Initialize empty grid (0 = floor, 1 = wall)
        self.grid = [[0 for _ in range(width)] for _ in range(height)]
        # Add some walls for testing (wall on the right side)
        for y in range(height):
            self.grid[y][width - 1] = 1  # Right wall

        # Add a few more walls for testing
        self.grid[3][3] = 1
        self.grid[3][4] = 1
        self.grid[3][5] = 1
        self.grid[7][2] = 1
        self.grid[7][3] = 1
        self.grid[7][4] = 1

    def draw(self, screen):
        for y in range(self.height):
            for x in range(self.width):
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if self.grid[y][x] == 0:  # Floor
                    pygame.draw.rect(screen, GREY, rect)
                    pygame.draw.rect(screen, BLACK, rect, 1)  # Grid lines
                else:  # Wall
                    pygame.draw.rect(screen, BLACK, rect)

    def is_wall(self, x, y):
        # Check if position is a wall or out of bounds
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return True  # Out of bounds is treated as a wall
        return self.grid[int(y)][int(x)] == 1

    def is_wall_area(self, x, y, width=1.0, height=1.0):
        # Check all corners of the area
        for corner_x in [x, x + width - 0.01]:
            for corner_y in [y, y + height - 0.01]:
                if corner_x < 0 or corner_y < 0 or corner_x >= self.width or corner_y >= self.height:
                    return True
                if self.grid[int(corner_y)][int(corner_x)] == 1:
                    return True
        return False

    def get_debug_wals_info(self):
        return


    def take_damage(self, amount):
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0