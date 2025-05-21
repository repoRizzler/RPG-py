from context.context import *
import pygame

class Player:
    def __init__(self, x, y):
        self.x = x  # Grid x position
        self.y = y  # Grid y position
        self.speed = 0.2  # Speed for smooth movement
        self.hp = 10
        self.max_hp = 10
    def draw(self, screen):
        # Draw player as a blue circle
        center_x = int((self.x + 0.5) * TILE_SIZE)
        center_y = int((self.y + 0.5) * TILE_SIZE)
        pygame.draw.circle(screen, BLUE, (center_x, center_y), TILE_SIZE // 3)

        # Draw health bar above player
        health_bar_width = TILE_SIZE
        health_bar_height = 5
        health_ratio = self.hp / self.max_hp
        health_bar_fill_width = health_bar_width * health_ratio

        bar_x = center_x - health_bar_width // 2
        bar_y = center_y - TILE_SIZE // 2 - 10

        # Background (empty health)
        pygame.draw.rect(screen, RED, (bar_x, bar_y, health_bar_width, health_bar_height))
        # Foreground (filled health)
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, health_bar_fill_width, health_bar_height))

    def move(self, dx, dy, game_map):
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed
        if not game_map.is_wall_area(new_x, self.y, width=1.0, height=1.0):
            self.x = new_x
        if not game_map.is_wall_area(self.x, new_y, width=1.0, height=1.0):
            self.y = new_y

    def get_debug_info(self):
        center_x = int((self.x + 0.5) * TILE_SIZE)
        center_y = int((self.y + 0.5) * TILE_SIZE)
        return f"x: {self.x}, y: {self.y}\ncenter_x: {center_x}, center_y: {center_y}"

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0