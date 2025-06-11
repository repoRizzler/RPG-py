# enemy.py - Enemy class and AI state machine

import pygame
import math
import random
from enum import Enum, auto

import context.context
from context.context import TILE_SIZE, RED, WHITE, GREEN, GREY
from entity.HitBox.RectangleHitbox import RectEntity
from utilities.pathfinding import a_star_pathfinding


# Enum for enemy states
class EnemyState(Enum):
    IDLE = auto()
    CHASE = auto()
    ATTACK = auto()
    COOLDOWN = auto()
    DEAD = auto()


class Enemy(RectEntity):
    """
    Base Enemy class with common AI behavior.
    Extends RectEntity for hitbox handling and collision.

    Attributes:
        x (int): Enemy's x position on the map.
        y (int): Enemy's y position on the map.
        state (EnemyState): Current state of the enemy (e.g. IDLE, CHASE).
        detection_radius (int): Radius within which the player can be detected.
        attack_radius (int): Radius within which the enemy can attack.
        attack_damage (int): Damage dealt by the enemy.
        path (list[tuple[int, int]]): Sequence of grid cells toward the target.
        next_attack_time (int): Next allowed time for attack.
        attack_cooldown (int): Time delay between attacks in milliseconds.
        color (Color): Debug color used for drawing the enemy.
        hp (int): Hit points of the enemy.
    """

    def __init__(self, x, y, width, height):
        """
         Initializes a base Enemy instance. Not intended to be used directly—meant to be extended by enemy type subclasses.

        Args:
            x (int): X-coordinate on the map grid.
            y (int): Y-coordinate on the map grid.
            width (int): Width of the enemy in map units.
            height (int): Height of the enemy in map units.
        """
        super().__init__(x+width, y+height, width, height)
        self.x = x
        self.y = y
        self.state = EnemyState.IDLE
        self.speed = 0.1
        self.detection_radius = 5
        self.attack_radius = 0  # Will be set by subclasses
        self.attack_damage = 10
        self.path = []
        self.next_attack_time = 0
        self.attack_cooldown = 1000  # milliseconds
        self.color = RED  # Default color, overridden by subclasses

        self.hp = 1

    def draw(self,screen,camera):
        """
        Draws the enemy's current state indicator on the screen.

        Args:
            screen (pygame.Surface): The surface to draw on.
            camera (Camera): The camera object to adjust position relative to screen.

        Returns:
            None
        """
        center_x, center_y = self.get_center(camera)

        # Draw state indicator
        state_colors = {
            EnemyState.IDLE: WHITE,
            EnemyState.CHASE: GREEN,
            EnemyState.ATTACK: RED,
            EnemyState.COOLDOWN: GREY,
            EnemyState.DEAD: context.context.BLACK
        }
        pygame.draw.circle(screen, state_colors[self.state],
                           (center_x, center_y - TILE_SIZE // 2), TILE_SIZE // 8)

    def distance_to(self, x, y):
        """
        Calculates the Euclidean distance to a target (x, y) position.

        Args:
            x (float): Target X position.
            y (float): Target Y position.

        Returns:
            float: Distance to the target.
        """
        return math.sqrt((self.x - x) ** 2 + (self.y - y) ** 2)

    def can_see_player(self, player, game_map):
        """
        Determines whether the enemy can see the player.

        Checks both distance (detection radius) and line of sight using Bresenham's algorithm.

        Args:
            player (Player): The player object.
            game_map (Map): The current game map.

        Returns:
            bool: True if the player is visible, otherwise False.
        """
        # Check if player is within detection radius
        if self.distance_to(player.x, player.y) > self.detection_radius:
            return False

        # Implement improved line-of-sight check using Bresenham's line algorithm
        # Get grid coordinates of enemy and player
        start_x, start_y = int(self.x), int(self.y)
        end_x, end_y = int(player.x), int(player.y)

        # Calculate line path between enemy and player
        # Implementation of Bresenham's line algorithm
        dx = abs(end_x - start_x)
        dy = abs(end_y - start_y)
        sx = 1 if start_x < end_x else -1
        sy = 1 if start_y < end_y else -1
        err = dx - dy

        x, y = start_x, start_y

        # Check each cell along the line
        while (x != end_x or y != end_y):
            # Check if current cell is a wall
            if game_map.is_wall(x, y) and (x != start_x or y != start_y):
                return False  # Wall blocks line of sight

            # Move to the next cell
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

            # Edge case: check if we're about to cross a wall corner diagonally
            # This prevents "shooting through corners"
            if (game_map.is_wall(x - sx, y) and game_map.is_wall(x, y - sy)):
                return False

        # If we reached the player without hitting a wall, there's line of sight
        return True

    def move_toward_player(self, player, game_map):
        """
        Moves the enemy toward the player using A* pathfinding.

        Args:
            player (Player): The player instance.
            game_map (Map): The current game map.

        Returns:
            None
        """
        # A* pathfinding implementation
        if len(self.path) == 0 or random.random() < 0.05:  # Occasionally recalculate path
            self.path = a_star_pathfinding(self.x, self.y, player.x, player.y, game_map)

        if len(self.path) > 0:
            next_x, next_y = self.path[0]
            dx = next_x - self.x
            dy = next_y - self.y

            # Normalize movement vector
            length = math.sqrt(dx ** 2 + dy ** 2)
            if length > 0:
                dx /= length
                dy /= length

            # Move toward next point
            new_x = self.x + dx * self.speed
            new_y = self.y + dy * self.speed

            # Check if we've reached the next point
            if abs(new_x - next_x) < 0.1 and abs(new_y - next_y) < 0.1:
                self.path.pop(0)

            # Check for wall collision
            if not game_map.is_wall(new_x, self.y):
                self.x = new_x
            if not game_map.is_wall(self.x, new_y):
                self.y = new_y

    def heuristic(self, a, b):
        """
        Calculates the Manhattan distance between two points.

        Args:
            a (tuple[int, int]): First point (x, y).
            b (tuple[int, int]): Second point (x, y).

        Returns:
            int: Manhattan distance.
        """
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def update(self,camera ,player, game_map, projectiles, current_time):
        """
         Updates the enemy's behavior and position based on its state.

        Args:
            camera (Camera): Camera used to offset screen position.
            player (Player): The player object.
            game_map (Map): The current map.
            projectiles (list[Projectile]): List of active projectiles.
            current_time (int): Current time in milliseconds.

        Returns:
        None
        """

        # IDLE state logic
        if self.state == EnemyState.IDLE:
            if self.can_see_player(player, game_map):
                self.state = EnemyState.CHASE

        # CHASE state logic - basic movement
        elif self.state == EnemyState.CHASE:
           #==== uncomment to make eneny forget about player when out of reach =======================
            # if not self.can_see_player(player, game_map):
            #     # print(f"Enemy lost sight of player, changing to IDLE state")
            #     self.state = EnemyState.IDLE
            #     return
            # Check if in attack range
            if self.distance_to(player.x, player.y) <= self.attack_radius and self.can_see_player(player, game_map):
                # print(f"Enemy in attack range, preparing to attack")
                self.prepare_attack(current_time)
            else:
                # print(f"Enemy moving toward player")
                self.move_toward_player(player, game_map)
        pos = self.get_center(camera)
        super().update_pos(pos[0], pos[1])

    def prepare_attack(self, current_time):
        """
        Placeholder for attack logic. To be overridden by subclasses.

        Args:
            current_time (int): Current time in milliseconds.

        Returns:
            None
        """
        pass
    def take_damage(self, damage):
        """
        Reduces enemy HP by a given damage amount. Transitions to DEAD state if HP falls below 0.

        Args:
            damage (int): Amount of damage received.

        Returns:
            None
        """
        self.hp -= damage
        print("attack on enemy")
        print(f"enemy hp: {self.hp}")
        if self.hp < 0:
            self.hp = 0
            self.state = EnemyState.DEAD
    def get_center(self, camera):
        """
        Gets the center coordinates of the enemy relative to the camera, in screen pixels.

        Args:
            camera (Camera): Camera object for coordinate transformation.

        Returns:
            tuple[int, int]: (x, y) center screen coordinates.
        """
        x,y = camera.apply(self.x, self.y)
        center_x = int((x + 0.5) * TILE_SIZE)
        center_y = int((y + 0.5) * TILE_SIZE)
        return center_x, center_y
