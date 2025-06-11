from enum import Enum
from entity.projectile import *


class WeaponType(Enum):
    """
    Enum representing types of weapons.

    Attributes:
        MELEE (int): Melee weapon type.
        RANGED (int): Ranged weapon type.
    """
    MELEE = 1
    RANGED = 2


class Weapon(RectEntity):
    """
    Base weapon class providing common weapon functionality.

    Extends:
        RectEntity: For position and collision hitbox handling.

    Attributes:
        damage (int): Damage dealt by the weapon per attack.
        cooldown (int): Minimum cooldown time between attacks in milliseconds.
        last_attack_time (int): Timestamp of the last attack.
        weapon_type (WeaponType or None): Type of weapon (MELEE or RANGED).
    """

    def __init__(self, x, y, width, length, damage=10, cooldown=50):
        """
       Initializes a weapon instance.

       Args:
           x (float): X-coordinate position.
           y (float): Y-coordinate position.
           width (float): Width of the weapon's hitbox.
           length (float): Length of the weapon's hitbox.
           damage (int, optional): Damage inflicted by the weapon. Defaults to 10.
           cooldown (int, optional): Cooldown time in milliseconds between attacks. Defaults to 50.
       """

        super().__init__(x, y, width, length)
        self.damage = damage
        self.cooldown = cooldown
        self.last_attack_time = 0
        self.weapon_type = None


    def can_attack(self, current_time):
        """
        Checks if the weapon can perform an attack based on its cooldown timer.

        Args:
            current_time (int): Current time in milliseconds.

        Returns:
            bool: True if cooldown period has passed and weapon can attack, False otherwise.
        """
        return current_time - self.last_attack_time >= self.cooldown

    def attack(self, x, y, direction, current_time, **kwargs):
        """
        Attempts to perform an attack action.

        Should be overridden by subclasses for specific attack behavior.

        Args:
            x (float): X-coordinate of attack origin.
            y (float): Y-coordinate of attack origin.
            direction (any): Direction of attack (type dependent on subclass).
            current_time (int): Current time in milliseconds.
            **kwargs: Additional optional parameters.

        Returns:
            bool: True if attack was performed, False if weapon is on cooldown.
        """
        if not self.can_attack(current_time):
            return False
        self.last_attack_time = current_time
        return True

    def point_on_line_at_distance(self, a, b, n):
        """
        Calculates a point along the line segment from point a to b at a distance n from a.

        Args:
            a (tuple[float, float]): Starting point coordinates (x, y).
            b (tuple[float, float]): Ending point coordinates (x, y).
            n (float): Distance from point a along the line toward point b.

        Returns:
            tuple[float, float]: Coordinates of the point at distance n along the line.
        """
        # a and b are 3D points like (x, y, z)
        ax, ay  = a
        bx, by = b

        # Direction vector d = b - a
        dx = bx - ax
        dy = by - ay

        # Length of vector d
        length = math.sqrt(dx**2 + dy**2)

        # Unit direction vector
        ux = dx / length
        uy = dy / length

        # New point at distance n from a
        cx = ax + ux * n
        cy = ay + uy * n

        return cx, cy

    def _distance_to_segment(self, px, py, x1, y1, x2, y2):

        """
        Calculates the shortest distance from a point to a line segment.

        Args:
            px (float): X-coordinate of the point.
            py (float): Y-coordinate of the point.
            x1 (float): X-coordinate of the first endpoint of the segment.
            y1 (float): Y-coordinate of the first endpoint of the segment.
            x2 (float): X-coordinate of the second endpoint of the segment.
            y2 (float): Y-coordinate of the second endpoint of the segment.

        Returns:
            float: Minimum distance from the point to the line segment.
        """
        line_mag_sq = (x2 - x1) ** 2 + (y2 - y1) ** 2
        if line_mag_sq == 0:
            return math.hypot(px - x1, py - y1)  # line is a point

        # Projection factor
        t = max(0, min(1, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / line_mag_sq))
        proj_x = x1 + t * (x2 - x1)
        proj_y = y1 + t * (y2 - y1)

        return math.hypot(px - proj_x, py - proj_y)
