import math
import pygame
from context.context import *
from entity.projectile import Projectile
from entity.enemy.enemy import Enemy, EnemyState


class RangedEnemy(Enemy):
    """
    Enemy subclass that attacks from a distance using projectiles.

    Extends:
        Enemy: The base enemy class with AI and movement logic.

    Attributes:
        attack_radius (float): Distance within which the enemy can shoot.
        color (Color): Debug color for this enemy type.
        cooldown_timer (int): Time after which the enemy is allowed to shoot again.
        shoot_cooldown (int): Delay between shots in milliseconds.
    """

    def __init__(self, x, y):
        """
        Initializes a RangedEnemy with projectile attack capabilities.

        Args:
            x (int): X-coordinate on the map grid.
            y (int): Y-coordinate on the map grid.
        """
        super().__init__(x, y,ENEMY_WIDTH*2,ENEMY_HEIGHT*2)
        self.attack_radius = 6
        self.color = YELLOW
        self.cooldown_timer = 0
        self.shoot_cooldown = 1500  # milliseconds

    def draw(self, screen,camera):
        """
        Draws the ranged enemy and optionally its hitbox if enabled.

        Args:
            screen (pygame.Surface): The rendering surface.
            camera (Camera): Camera object for view transformation.

        Returns:
            None
        """
        center_x, center_y = self.get_center(camera)

        # Draw enemy as square
        # pygame.draw.rect(screen, self.color,
        #                  (center_x - TILE_SIZE // 3, center_y - TILE_SIZE // 3,
        #                   TILE_SIZE // 1.5, TILE_SIZE // 1.5))

        if show_HitBox:
            super().draw_hit_box(screen)
        # Draw state indicator
        super().draw(screen,camera)

    def prepare_attack(self, current_time):
        """
        Prepares a ranged attack by entering a cooldown phase.

        Args:
            current_time (int): Current game time in milliseconds.

        Returns:
            None
        """
        # Ranged enemies go to cooldown state before attacking
        self.state = EnemyState.COOLDOWN
        self.cooldown_timer = current_time + self.shoot_cooldown

    def update(self, camera, player, game_map, projectiles, current_time):
        """
        Updates enemy behavior, handling cooldown and projectile attacks.

        Args:
            camera (Camera): Camera for coordinate transformation.
            player (Player): The player instance.
            game_map (Map): Current map for collision and visibility checks.
            projectiles (list[Projectile]): Active projectile list.
            current_time (int): Game time in milliseconds.

        Returns:
            None
        """
        # First run the base class update (handles IDLE and CHASE states)
        super().update(camera,player, game_map, projectiles, current_time)
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