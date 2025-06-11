import math
from context.context import *
import pygame

from entity.HitBox.RectangleHitbox import RectEntity
from utilities import camera


class Projectile(RectEntity):
    def __init__(self, x, y, angle, damage, radius = TILE_SIZE //8 ):
        super().__init__(x+radius, y+radius, radius,radius, angle=angle)
        self.color = RED
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 0.4
        self.damage = damage
        self.active = True

    def update(self, game_map, player, enemies, camera):
        # Move projectile in the direction of its angle
        dx = math.cos(self.angle) * self.speed
        dy = math.sin(self.angle) * self.speed

        self.x += dx
        self.y += dy

        x,y = self.get_center(camera)
        super().update_pos(x,y)

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
        # pygame.draw.circle(screen, RED, (center_x, center_y), TILE_SIZE // 8)
        super().draw_hit_box(screen)

    def get_center(self, camera):
        x,y = camera.apply(self.x, self.y)
        center_x = int((x + 0.5) * TILE_SIZE)
        center_y = int((y + 0.5) * TILE_SIZE)
        return center_x, center_y