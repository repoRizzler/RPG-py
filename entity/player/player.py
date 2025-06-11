from context.context import *
from entity.weapon.weapon import *
from entity.weapon.MeleeWeapon import MeleeWeapon
from entity.weapon.RangedWeapon import RangedWeapon
import pygame



class Player(RectEntity):
    """
    The player character controlled by the user.

    Inherits from:
        RectEntity: Provides hitbox and collision capabilities.

    Attributes:
        x (float): Player's x-position on the game grid.
        y (float): Player's y-position on the game grid.
        center_x (int): Player's center x-position on the screen (pixels).
        center_y (int): Player's center y-position on the screen (pixels).
        speed (float): Movement speed of the player.
        hp (int): Current hit points of the player.
        max_hp (int): Maximum hit points of the player.
        weapons (list[Weapon]): List of player's weapons (melee and ranged).
        current_weapon_id (int): Index of currently selected weapon.
        weapon (Weapon): Currently equipped weapon (can be melee or ranged).
    """
    def __init__(self, x, y):
        """
        Initializes the player at a specific grid position.

        Args:
            x (float): Starting x-position on the grid.
            y (float): Starting y-position on the grid.
        """
        super().__init__(x, y, PLAYER_SIZE*1.5,PLAYER_SIZE*1.5)
        self.x = x  # Grid x position
        self.y = y  # Grid y position

        self.center_x = 0 # player center x on Screen
        self.center_y = 0 # player center x on Screen

        self.speed = 0.2  # Speed for smooth movement
        self.hp = 10
        self.max_hp = 10

        # Combat attributes
        self.weapons = [
            MeleeWeapon(damage=20, cooldown=50),
            RangedWeapon(damage=20, cooldown=50)
        ]
        self.current_weapon_id = 0
        self.weapon = None
        self.weapon = MeleeWeapon(damage=20, cooldown=500)


    def draw(self, screen,current_time):
        """
        Renders the player on the screen along with health bar and weapon indicators.

        Args:
            screen (pygame.Surface): The rendering surface.
            current_time (int): Current time in milliseconds (used by weapon draw).

        Returns:
            None
        """

        # Draw player as a blue circle
        pygame.draw.circle(screen, BLUE, (self.center_x, self.center_y), PLAYER_SIZE)

        # Draw health bar above player
        health_bar_width = TILE_SIZE
        health_bar_height = 5
        health_ratio = self.hp / self.max_hp
        health_bar_fill_width = health_bar_width * health_ratio

        bar_x = self.center_x - health_bar_width // 2
        bar_y = self.center_y - TILE_SIZE // 2 - 10

        # Background (empty health)
        pygame.draw.rect(screen, RED, (bar_x, bar_y, health_bar_width, health_bar_height))
        # Foreground (filled health)
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, health_bar_fill_width, health_bar_height))
        if self.weapon is not None:
            self.weapon.draw(screen, self, current_time)
        if show_HitBox:
            self.draw_hit_box(screen)
        # self.weapon.draw_attack_indicator(screen,self.x,self.y,direction=self.attack_direction)

    def update(self, enemies,camera,current_time):
        """
        Updates player position and weapon logic.

        Args:
            enemies (list[Enemy]): List of enemies in the game.
            camera (Camera): Camera used to calculate screen-relative positions.
            current_time (int): Current game time in milliseconds.

        Returns:
            None
        """

        self.center_x = int((self.x - camera.x + 0.5) * TILE_SIZE)
        self.center_y = int((self.y - camera.y + 0.5) * TILE_SIZE)
        self.update_pos(self.center_x, self.center_y)

        if self.weapon is not None:
            self.weapon.update(current_time,self,enemies=enemies)
        # if isinstance(self.weapon, MeleeWeapon):
        #     self.weapon.update_swing(current_time)

        # # Check for hits during swing
        # hit_enemies = self.weapon.check_swing_hit(self.x, self.y, enemies, current_time)
        # for enemy in hit_enemies:
        #     enemy.take_damage(self.weapon.damage)


    def move(self, dx, dy, game_map):
        """
        Moves the player by delta x and y, checking for wall collisions.

        Args:
            dx (float): Change in x-direction.
            dy (float): Change in y-direction.
            game_map (Map): Game map used for wall collision detection.

        Returns:
            None
        """
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed
        if not game_map.is_wall_area(new_x, self.y, width=1.0, height=1.0):
            self.x = new_x
        if not game_map.is_wall_area(self.x, new_y, width=1.0, height=1.0):
            self.y = new_y


    def take_damage(self, amount):
        """
       Reduces the player's health by the specified amount.

       Args:
           amount (int): Amount of damage received.

       Returns:
           None
       """
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0

    def attack(self,camera, current_time, projectiles, enemies, game_map):
        """
        Performs an attack using the currently selected weapon.

        Args:
            camera (Camera): Camera for position offset.
            current_time (int): Current game time in milliseconds.
            projectiles (list[Projectile]): List to append new projectiles (for ranged).
            enemies (list[Enemy]): List of enemies in range (for ranged).
            game_map (Map): The game map (for ranged line-of-sight).

        Returns:
            None
        """
        x ,y = camera.apply(self.x, self.y)
        if self.weapon.weapon_type == WeaponType.MELEE:
            self.weapon.attack(
                x ,y,
                self.get_angle_to_mouse(),
                current_time,
            )
        elif self.weapon.weapon_type == WeaponType.RANGED:
            self.weapon.attack(
                x ,y,
                self.get_angle_to_mouse(),
                current_time,
                projectiles=projectiles,
                enemies=enemies,
                game_map=game_map
            )

    def get_angle_to_mouse(self):
        """
        Calculates the angle between the player and the mouse cursor.

        Returns:
            float: Angle in degrees from the player to the mouse position.
        """

        mouse_pos = pygame.mouse.get_pos()
        dx = mouse_pos[0] - self.center_x
        dy = mouse_pos[1] - self.center_y
        angle = math.degrees(math.atan2(dy, dx))
        return angle

    def get_weapon_debug_info(self):
        """
        Returns weapon-related debug information.

        Returns:
            dict: Dictionary containing debug info about weapon and player position.
        """
        res = self.weapon.get_debug_info(self)
        res["player_pos: "] = f"x: {self.x}, y: {self.x}"
        res["player_centre: "] = f"x: {self.center_x}, y: {self.center_y}"
        return res
    def set_position(self, x, y):
        """
        Sets the player position directly on the grid.

        Args:
            x (float): New x-coordinate.
            y (float): New y-coordinate.

        Returns:
            None
        """
        self.x = x
        self.y = y
    def change_weapon_up(self):
        """
       Switches to the next weapon in the inventory (cyclic).

       Returns:
           None
       """
        if self.current_weapon_id+1 >= self.weapons.__len__():
            self.current_weapon_id = 0
            return
        self.current_weapon_id+=1
        self.weapon = self.weapons[self.current_weapon_id]
    def change_weapon_down(self):
        """
        Switches to the previous weapon in the inventory (cyclic).

        Returns:
            None
        """
        if self.current_weapon_id -1 < 0:
            self.current_weapon_id = self.weapons.__len__()-1
            return
        self.current_weapon_id -= 1
        self.weapon = self.weapons[self.current_weapon_id]







