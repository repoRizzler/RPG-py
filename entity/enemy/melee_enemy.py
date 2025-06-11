from entity.enemy.enemy import Enemy, EnemyState
from context.context import *
import pygame

class MeleeEnemy(Enemy):
    """
    Enemy subclass for close-range melee attackers.

    Extends:
        Enemy: The base enemy class with AI and movement logic.

    Attributes:
        attack_radius (float): Distance within which the enemy can perform a melee attack.
        color (Color): Debug color for visualizing this enemy type.
    """

    def __init__(self, x, y):
        """
        Initializes a MeleeEnemy instance with specific size and behavior.

        Args:
            x (int): X-coordinate on the map grid.
            y (int): Y-coordinate on the map grid.
        """
        super().__init__(x, y,ENEMY_WIDTH*2,ENEMY_HEIGHT*2)
        self.attack_radius = 1.2
        self.color = RED

    def draw(self, screen,camera):
        """
        Draws the melee enemy and its hitbox if debug is enabled.

        Args:
            screen (pygame.Surface): The rendering surface.
            camera (Camera): Camera for coordinate transformation.

        Returns:
            None
        """
        center_x, center_y = self.get_center(camera)

        # Draw enemy as circle
        # pygame.draw.circle(screen, self.color, (center_x, center_y), TILE_SIZE // 3)
        # Draw state indicator
        super().draw(screen,camera)
        if show_HitBox:
            super().draw_hit_box(screen)

    def prepare_attack(self, current_time):
        """
        Prepares an immediate melee attack by switching to ATTACK state.

        Args:
            current_time (int): Current game time in milliseconds.

        Returns:
           None
        """
        # Melee enemies attack immediately when in range
        self.state = EnemyState.ATTACK

    def update(self, camera,player, game_map, projectiles, current_time):
        """
        Updates the melee enemy state, performs melee attack when in range.

        Args:
            camera (Camera): Camera for screen-relative coordinates.
            player (Player): Player instance.
            game_map (Map): Current game map.
            projectiles (list[Projectile]): List of active projectiles.
            current_time (int): Current game time in milliseconds.

        Returns:
            None
        """
        super().update(camera,player, game_map, projectiles, current_time)
        # Additional state handling specific to MeleeEnemy
        if self.state == EnemyState.ATTACK:
            # Melee attack - damage player if in range
            if self.distance_to(player.x, player.y) <= self.attack_radius:
                if current_time >= self.next_attack_time:
                    player.take_damage(self.attack_damage)
                    self.next_attack_time = current_time + self.attack_cooldown
            else:
                self.state = EnemyState.CHASE

