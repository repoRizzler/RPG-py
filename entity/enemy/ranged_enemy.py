import math
import pygame
from context.context import *
from entity.projectile import Projectile
from entity.enemy.enemy import Enemy, EnemyState


class RangedEnemy(Enemy):
    """Shooter enemy that attacks from distance"""

    def __init__(self, x, y):
        super().__init__(x, y)
        self.attack_radius = 6
        self.color = YELLOW
        self.cooldown_timer = 0
        self.shoot_cooldown = 1500  # milliseconds

    def draw(self, screen):
        center_x = int((self.x + 0.5) * TILE_SIZE)
        center_y = int((self.y + 0.5) * TILE_SIZE)

        # Draw enemy as square
        pygame.draw.rect(screen, self.color,
                         (center_x - TILE_SIZE // 3, center_y - TILE_SIZE // 3,
                          TILE_SIZE // 1.5, TILE_SIZE // 1.5))

        # Draw state indicator
        super().draw(screen)

    def prepare_attack(self, current_time):
        # Ranged enemies go to cooldown state before attacking
        self.state = EnemyState.COOLDOWN
        self.cooldown_timer = current_time + self.shoot_cooldown

    def update(self, player, game_map, projectiles, current_time):
        # First run the base class update (handles IDLE and CHASE states)
        super().update(player, game_map, projectiles, current_time)
        print(self.state)
        # Then handle states specific to RangedEnemy
        if self.state == EnemyState.COOLDOWN:
            # Keep checking if player is still in range during cooldown
            # if not self.can_see_player(player, game_map):
            #     self.state = EnemyState.IDLE
            #     return

            # If player moves out of range during cooldown, go back to chase
            if self.distance_to(player.x, player.y) > self.attack_radius:
                self.state = EnemyState.CHASE
                return

            # Wait for cooldown timer to expire
            if current_time >= self.cooldown_timer:
                self.state = EnemyState.ATTACK

        elif self.state == EnemyState.ATTACK:
            # Ranged attack - create projectile if we can still see player
            if self.can_see_player(player, game_map):
                angle = math.atan2(player.y - self.y, player.x - self.x)
                projectiles.append(Projectile(self.x, self.y, angle, self.attack_damage))
                # Go back to CHASE after shooting to allow movement
                self.state = EnemyState.CHASE
            else:
                self.state = EnemyState.CHASE