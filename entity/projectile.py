import math
from context.context import *
import pygame

class Projectile:
    def __init__(self, x, y, angle, damage):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 0.4
        self.damage = damage
        self.active = True

    def update(self, game_map, player):
        # Move projectile in the direction of its angle
        dx = math.cos(self.angle) * self.speed
        dy = math.sin(self.angle) * self.speed

        self.x += dx
        self.y += dy

        # Check for collision with walls
        if game_map.is_wall(self.x, self.y):
            self.active = False
            return

        # Check for collision with player
        if math.sqrt((self.x - player.x) ** 2 + (self.y - player.y) ** 2) < 0.5:
            player.take_damage(self.damage)
            self.active = False

    def draw(self, screen):
        center_x = int((self.x + 0.5) * TILE_SIZE)
        center_y = int((self.y + 0.5) * TILE_SIZE)
        pygame.draw.circle(screen, RED, (center_x, center_y), TILE_SIZE // 8)