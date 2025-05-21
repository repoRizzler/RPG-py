from entity.enemy.enemy import Enemy, EnemyState
from context.context import *
import pygame

class MeleeEnemy(Enemy):
    """Close range enemy that attacks directly"""

    def __init__(self, x, y):
        super().__init__(x, y)
        self.attack_radius = 1.2
        self.color = RED

    def draw(self, screen):
        center_x = int((self.x + 0.5) * TILE_SIZE)
        center_y = int((self.y + 0.5) * TILE_SIZE)

        # Draw enemy as circle
        pygame.draw.circle(screen, self.color, (center_x, center_y), TILE_SIZE // 3)

        # Draw state indicator
        super().draw(screen)

    def prepare_attack(self, current_time):
        # Melee enemies attack immediately when in range
        self.state = EnemyState.ATTACK

    def update(self, player, game_map, projectiles, current_time):
        super().update(player, game_map, projectiles, current_time)
        # Additional state handling specific to MeleeEnemy
        if self.state == EnemyState.ATTACK:
            # Melee attack - damage player if in range
            if self.distance_to(player.x, player.y) <= self.attack_radius:
                if current_time >= self.next_attack_time:
                    player.take_damage(self.attack_damage)
                    self.next_attack_time = current_time + self.attack_cooldown
            else:
                self.state = EnemyState.CHASE

