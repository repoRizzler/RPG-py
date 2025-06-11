
import pygame
import math

from context.context import *
from entity.weapon.weapon import Weapon, WeaponType
from context.context import TILE_SIZE, RED, GREEN, BLUE


class MeleeWeapon(Weapon):
    """
    Melee weapon class representing a swinging blade weapon.

    Handles swing animation, collision detection with enemies, and cooldown management.

    Attributes:
        damage (int): Damage inflicted per hit.
        cooldown (int): Minimum cooldown time in milliseconds between swings.
        reach (float): Maximum reach of the weapon in pixels.
        swing_duration (int): Duration of the swing animation in milliseconds.
        player_direction (float): Angle (degrees) the player faces when starting attack.
        is_attacking (bool): Whether the weapon is currently swinging.
        swing_direction (float): Direction of the swing (angle in degrees).
        attack_start_time (int): Timestamp when the current swing started.
        hit_enemies (set): Set of enemies hit in the current swing to avoid multiple hits.
        swing_start_angle (float): Initial angle of the swing animation relative to player direction.
        swing_deviation (float): Total angular deviation of the swing (how wide the blade swings).
        current_angle (float): Current angle of the blade during swing or idle.
        handle_length (float): Length of the weapon handle in pixels.
        blade_length (float): Length of the weapon blade in pixels.
    """
    def __init__(self,damage=15, cooldown=100, reach=2.0, swing_duration=300):
        """
        Initialize a MeleeWeapon instance.

        Args:
            damage (int, optional): Damage inflicted by weapon hits. Default is 15.
            cooldown (int, optional): Cooldown time between attacks in milliseconds. Default is 100.
            reach (float, optional): Reach multiplier in tiles (converted to pixels). Default is 2.0.
            swing_duration (int, optional): Duration of swing animation in milliseconds. Default is 300.
        """
        super().__init__(0,0,MELEE_WEAPON_LENGTH,MELEE_WEAPON_WIDTH,damage, cooldown)
        self.weapon_type = WeaponType.MELEE
        self.reach = reach * TILE_SIZE  # Weapon reach in pixels
        self.handle_length = self.reach * 0.1
        self.blade_length = self.reach * 0.5

        self.swing_duration = swing_duration  # Duration of swing animation in ms

        self.player_direction = 0  # Direction player is facing when attack starts

        # Attack state
        self.is_attacking = False
        self.swing_direction = 0
        self.attack_start_time = 0
        self.hit_enemies = set()  # Track enemies hit during current swing to avoid multiple hits

        # Swing animation parameters
        self.swing_start_angle = -35  # Starting angle relative to facing direction
        self.swing_deviation = 50  # deviation of the angle form player to  a mouse position
        self.current_angle = 0

    def attack(self, x, y, direction, current_time, **kwargs):
        """
        Initiates a melee attack swing if the cooldown has elapsed and no current attack is active.

        Args:
            x (float): X-coordinate for the attack origin (unused here).
            y (float): Y-coordinate for the attack origin (unused here).
            direction (float): Player's facing direction in degrees at attack start.
            current_time (int): Current time in milliseconds.

        Returns:
            bool: True if attack started, False otherwise (e.g., on cooldown or already attacking).
        """
        if not self.can_attack(current_time) or self.is_attacking:
            return False

        # Start the attack
        self.last_attack_time = current_time
        self.is_attacking = True
        self.attack_start_time = current_time
        self.player_direction = direction
        self.swing_start_angle = direction - self.swing_deviation
        self.hit_enemies.clear()  # Reset hit enemies for new swing

        return True

    def update(self, current_time,player, enemies=None):
        """
        Updates the swing animation state and checks for enemy collisions during an active swing.

        Args:
            current_time (int): Current time in milliseconds.
            player (Player): Player instance with positional and directional info.
            enemies (list, optional): List of enemy objects to check collision against.
        """
        if not self.is_attacking:
            self.current_angle = player.get_angle_to_mouse()
            super().update_angle(self.current_angle)
            return

        # Check if swing is complete
        elapsed_time = current_time - self.attack_start_time
        if elapsed_time >= self.swing_duration:
            self.is_attacking = False
            self.current_angle = player.get_angle_to_mouse()
            return


        swing_progress = self.get_attack_progress()
        if swing_progress >= 1.0:
            self.is_attacking = False
        else:
            # Smooth easing function (ease-out)
            t = 1 - (1 - swing_progress) ** 3
            # angle_diff = self.target_angle - self.start_angle
            self.current_angle = self.swing_start_angle + (self.swing_deviation*2 * t)


        super().update_angle(self.current_angle)


        # Check for enemy collisions during swing
        if enemies:
            self._check_enemy_collisions(player, current_time, enemies)

    def _check_enemy_collisions(self, player, current_time, enemies):
        """
        Checks if the blade collides with any enemies during the swing.

        Enemies already hit in the current swing are ignored.

        Args:
            player (Player): Player instance (currently unused in method).
            current_time (int): Current time in milliseconds (currently unused).
            enemies (list): List of enemy objects to test collisions against.
        """
        # Compute player's center in pixels
        # player_center = (player.center_x, player.center_y)
        # angle_rad = math.radians(self.current_angle)

        # Blade positions
        # handle_x = player_center[0] + math.cos(angle_rad) * (self.reach * 0.1)
        # handle_y = player_center[1] + math.sin(angle_rad) * (self.reach * 0.1)

        # blade_start_x = handle_x + math.cos(angle_rad) * self.handle_length
        # blade_start_y = handle_y + math.sin(angle_rad) * self.handle_length

        # blade_end_x = blade_start_x + math.cos(angle_rad) * self.blade_length
        # blade_end_y = blade_start_y + math.sin(angle_rad) * self.blade_length

        for enemy in enemies:
            if enemy in self.hit_enemies:
                continue  # already hit

            # # Enemy center in pixels
            # enemy_center_x = (enemy.x + 0.5) * TILE_SIZE
            # enemy_center_y = (enemy.y + 0.5) * TILE_SIZE


            if super().collides_with_rect(enemy):
                enemy.take_damage(self.damage)
                self.hit_enemies.add(enemy)


            # if dist <= self.blade_width / 2:
            #     enemy.take_damage(self.damage)
            #     self.hit_enemies.add(enemy)

    def draw(self, screen, player, current_time):
        """
        Draws the weapon on the screen.

        Args:
            screen (pygame.Surface): Pygame surface to draw on.
            player (Player): Player instance for position reference.
            current_time (int): Current time in milliseconds.
        """
        self._draw(screen,player)

    def _draw(self, screen,player):
        """
        Internal drawing method for the melee weapon.

        Calculates blade and handle positions based on the player's position and mouse position.

        Args:
            screen (pygame.Surface): Surface to draw on.
            player (Player): Player instance with position attributes.
        """

        player_center = (player.center_x, player.center_y)
        mouse_pos = pygame.mouse.get_pos()

        player_rad = PLAYER_SIZE

        handle_start_pos_x,handle_start_pos_y = self.point_on_line_at_distance(
            player_center,
            mouse_pos,
            player_rad *1.5)

        blade_start_pos_x,blade_start_pos_y = self.point_on_line_at_distance(
            (handle_start_pos_x,handle_start_pos_y),
            mouse_pos,
            self.handle_length)

        blade_end_pos_x,blade_end_pos_y = self.point_on_line_at_distance(
            (blade_start_pos_x,blade_start_pos_y),
            mouse_pos,
            self.blade_length)
        current_angle_rad = math.radians(self.current_angle)


        # the position in

        if self.is_attacking:

            blade_start_pos_x = handle_start_pos_x + math.cos(current_angle_rad) * self.handle_length
            blade_start_pos_y = handle_start_pos_y + math.sin(current_angle_rad) * self.handle_length
            blade_end_pos_x = blade_start_pos_x + math.cos(current_angle_rad) * self.blade_length
            blade_end_pos_y = blade_start_pos_y + math.sin(current_angle_rad) * self.blade_length


        # the position in hitbox states for the centre of a shape
        super().update_pos(blade_start_pos_x,blade_start_pos_y)

        # pygame.draw.line(screen, RED,
        #                  (handle_start_pos_x, handle_start_pos_y),
        #                  (blade_start_pos_x, blade_start_pos_y),
        #                  self.blade_width.__int__())
        #
        # pygame.draw.line(screen, WHITE,
        #                  (blade_start_pos_x, blade_start_pos_y),
        #                  (blade_end_pos_x, blade_end_pos_y),
        #                  self.blade_width.__int__())

        if show_HitBox:
            super().draw_hit_box(screen)

    def get_attack_progress(self):
        """
        Returns the current progress of the attack swing.

        Returns:
            float: Value between 0.0 (start) and 1.0 (end) indicating swing progress.
        """
        if not self.is_attacking:
            return 0.0

        elapsed_time = pygame.time.get_ticks() - self.attack_start_time
        return min(elapsed_time / self.swing_duration, 1.0)

    def get_attack_direction(self):
        """
        Returns the direction angle the player faced at the start of the attack.

        Returns:
            float: Attack start direction in degrees.
        """
        return self.player_direction

    def get_weapon_pos(self,player):
        """
        Returns the weapon's current position in pixels relative to the player.

        Args:
            player (Player): Player instance with grid position attributes.

        Returns:
            tuple[int, int]: (x, y) position of the weapon in pixels.
        """
        weapon_x = (player.x * TILE_SIZE) + 10
        weapon_y = (player.y * TILE_SIZE) + 10

        return (weapon_x,weapon_y)


    def get_debug_info(self,player):
        """
        Returns a dictionary of debug info related to the weapon state.

        Args:
            player (Player): Player instance.

        Returns:
            dict: Debug information including weapon position and angle.
        """
        result = dict()

        weapon_pos = self.get_weapon_pos(player)

        weapon_pos_str = f"wepon-x: {weapon_pos[0]}, wepon-y: {weapon_pos[1]}"

        result["weapon-pos"] = weapon_pos_str

        result["weapon-angle"] = self.player_direction


        return result

