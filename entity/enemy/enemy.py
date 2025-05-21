# enemy.py - Enemy class and AI state machine

import pygame
import math
import random
from enum import Enum, auto
from context.context import TILE_SIZE, RED, WHITE, GREEN, GREY
from utilities.pathfinding import a_star_pathfinding


# Enum for enemy states
class EnemyState(Enum):
    IDLE = auto()
    CHASE = auto()
    ATTACK = auto()
    COOLDOWN = auto()


class Enemy:
    """Base Enemy class with common functionality"""

    def __init__(self, x, y):
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

    def draw(self, screen):
        center_x = int((self.x + 0.5) * TILE_SIZE)
        center_y = int((self.y + 0.5) * TILE_SIZE)

        # Draw state indicator
        state_colors = {
            EnemyState.IDLE: WHITE,
            EnemyState.CHASE: GREEN,
            EnemyState.ATTACK: RED,
            EnemyState.COOLDOWN: GREY
        }
        pygame.draw.circle(screen, state_colors[self.state],
                           (center_x, center_y - TILE_SIZE // 2), TILE_SIZE // 8)

    def distance_to(self, x, y):
        return math.sqrt((self.x - x) ** 2 + (self.y - y) ** 2)

    def can_see_player(self, player, game_map):
        """
        Check if the enemy can see the player, considering:
        1. Distance (detection radius)
        2. Line of sight (no walls in between)
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
        """Common movement logic when chasing the player"""
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
        Calculate the Manhattan distance heuristic between two points
        """
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def update(self, player, game_map, projectiles, current_time):
        """Base update method with common state logic"""
        # Print state for debugging
        # print(f"Enemy at ({self.x}, {self.y}) in state {self.state}, distance to player: {self.distance_to(player.x, player.y)}")

        # IDLE state logic
        if self.state == EnemyState.IDLE:
            if self.can_see_player(player, game_map):
                # print(f"Enemy sees player, changing to CHASE state")
                self.state = EnemyState.CHASE

        # CHASE state logic - basic movement
        elif self.state == EnemyState.CHASE:
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

    def prepare_attack(self, current_time):
        """Prepare for attack, override in subclasses"""
        pass