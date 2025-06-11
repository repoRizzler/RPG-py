import math

import pygame

from context.context import *
from entity.player.player_projectile import PlayerProjectile
from entity.weapon.weapon import Weapon,WeaponType


class RangedWeapon(Weapon):
    """
    RangedWeapon class represents a weapon that fires projectiles.

    Attributes:
        damage (int): The amount of damage dealt by each projectile.
        range (float): Maximum range (distance) the projectile can travel (in some unit, e.g., tiles).
        cooldown (int): Time in milliseconds between consecutive attacks.
        projectile_speed (float): Speed at which the projectile travels.
        color (tuple): RGB color used for drawing the weapon (optional).
        name (str): Weapon name identifier.
    """

    def __init__(self, damage=8, range=5.0, cooldown=300, projectile_speed=0.4):

        """
        Initialize a ranged weapon with given parameters.

        Args:
            damage (int): Damage per projectile (default 8).
            range (float): Maximum range of projectile in game units (default 5.0).
            cooldown (int): Attack cooldown in milliseconds (default 300).
            projectile_speed (float): Projectile movement speed (default 0.4).
        """

        super().__init__(0,0,RANGE_WEAPON_LENGTH,RANGE_WEAPON_WIDTH,damage=damage, cooldown=cooldown)
        self.weapon_type = WeaponType.RANGED
        self.range = range
        self.projectile_speed = projectile_speed
        self.color = BLUE
        self.name = "Glock-16"

    def attack(self, x, y, direction, current_time, projectiles=None, **kwargs):
        """
        Perform an attack by firing a projectile if cooldown permits.

        Args:
            x (float): Starting x position of the projectile (usually player's position).
            y (float): Starting y position of the projectile.
            direction (float): Attack direction angle in degrees.
            current_time (int): Current game time in milliseconds.
            projectiles (list): Optional list to append newly created projectiles to.
            **kwargs: Additional optional parameters.

        Returns:
            bool: True if attack was successful (projectile fired), False otherwise.
        """
        if not super().attack(x, y, direction, current_time):
            return False

        if projectiles is not None and direction != (0, 0):
            angle = math.radians(direction)
            projectiles.append(PlayerProjectile(x, y, angle, self.damage, self.range, self.projectile_speed))
            return

        return False

    def get_debug_info(self, player):
        result = dict()
        mouse_pos = pygame.mouse.get_pos()
        result['mouse pos'] = f"x: {mouse_pos[0]}, y: {mouse_pos[1]}"
        return result

    def update(self, current_time, player, enemies=None, **kwargs):
        """
        Update the weapon state each frame.
        Updates the weapon's angle to face the mouse cursor and positions it relative to the player.

        Args:
            current_time (int): Current game time in milliseconds.
            player (Player): The player object holding the weapon.
            enemies (list, optional): List of enemies (not used here but available).
            **kwargs: Additional optional parameters.
        """
        angle = player.get_angle_to_mouse()

        self.update_angle(angle)

        mouse_pos = pygame.mouse.get_pos()

        player_rad = PLAYER_SIZE

        gun_start_pos_x, gun_start_pos_y = self.point_on_line_at_distance(
            (player.center_x, player.center_y),
            mouse_pos,
            player_rad*1.5)

        self.update_pos(gun_start_pos_x,gun_start_pos_y)

    def draw(self, screen, player, current_time):
        """
        Draw the ranged weapon on the screen.

        Args:
            screen (pygame.Surface): The surface to draw on.
            player (Player): The player holding the weapon.
            current_time (int): Current game time in milliseconds.
        """
        self._draw(screen,player)
    def _draw(self, screen, player):

        """
        Internal helper method to draw the weapon's graphical representation.
        Can draw the gun barrel and optionally the hitbox if debugging is enabled.

        Args:
            screen (pygame.Surface): The surface to draw on.
            player (Player): The player holding the weapon.
        """
        player_center = (player.center_x, player.center_y)
        mouse_pos = pygame.mouse.get_pos()

        player_rad = PLAYER_SIZE

        gun_start_pos_x, gun_start_pos_y = self.point_on_line_at_distance(
            player_center,
            mouse_pos,
            player_rad)

        gun_end_pos_x, gun_end_pos_y = self.point_on_line_at_distance(
            (gun_start_pos_x, gun_start_pos_y),
            mouse_pos,
            RANGE_WEAPON_LENGTH)

        if show_HitBox:
            super().draw_hit_box(screen)