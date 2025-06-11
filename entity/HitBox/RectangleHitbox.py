import pygame
from utilities.HitboxUtilities import *

class RectEntity:
    """
    Base class for rectangular entities with rotation and collision detection.

    Attributes:
        pos (pygame.Vector2): Position of the entity center on the map.
        width (float): Width of the rectangle.
        height (float): Height of the rectangle.
        angle (float): Rotation angle in degrees.
        color (tuple[int, int, int]): Color used for rendering the hitbox.
    """
    def __init__(self, x, y, width, height, angle=0):
        """
        Initializes a rectangular entity with a position, size, and angle.

        Args:
            x (float): X-coordinate of the center.
            y (float): Y-coordinate of the center.
            width (float): Width of the rectangle.
            height (float): Height of the rectangle.
            angle (float, optional): Rotation angle in degrees. Defaults to 0.
        """
        self.pos = pygame.Vector2(x, y)
        self.width = width
        self.height = height
        self.angle = angle
        self.color = (0, 255, 0)

    def get_corners(self):
        """
        Calculates the corner points of the rectangle, considering rotation.

        Returns:
            list[pygame.Vector2]: List of 4 rotated corner positions.
        """
        hw, hh = self.width / 2, self.height / 2
        corners = [
            pygame.Vector2(-hw, -hh),
            pygame.Vector2(hw, -hh),
            pygame.Vector2(hw, hh),
            pygame.Vector2(-hw, hh),
        ]
        rotated = [corner.rotate(self.angle) + self.pos for corner in corners]
        return rotated

    def draw_hit_box(self, surface):
        """
        Draws the hitbox polygon on the provided surface.

        Args:
           surface (pygame.Surface): Surface to render the polygon on.

        Returns:
            None
        """
        pygame.draw.polygon(surface, self.color, self.get_corners(), 2)

    def collides_with_rect(self, other):
        """
        Checks collision with another rectangular entity using polygon intersection.

        Args:
            other (RectEntity): The other rectangle to check collision against.

        Returns:
            bool: True if there is a collision, False otherwise.
        """
        return polygons_collide(self.get_corners(), other.get_corners())

    def on_collision(self):
        """
        Changes the entity's color to red, indicating collision.

        Returns:
            None
        """
        self.color = (255, 0, 0)

    def off_collision(self):
        """
        Resets the entity's color to green, indicating no collision.

        Returns:
            None
        """
        self.color = (0, 255, 0)
    def update_pos(self,x,y):
        """
        Updates the position of the entity.

        Args:
            x (float): New x-coordinate.
            y (float): New y-coordinate.

        Returns:
            None
        """
        self.pos.x = x
        self.pos.y = y
    def update_angle(self, angle):
        """
       Updates the rotation angle of the entity.

       Args:
           angle (float): New angle in degrees.

       Returns:
           None
       """
        self.angle = angle