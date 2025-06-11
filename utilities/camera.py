from context.context import TILE_SIZE
from entity.HitBox.RectangleHitbox import RectEntity


class Camera:
    """
    Represents a camera viewport in a tile-based game world.

    The camera tracks a rectangular area of the map in tile units, usually centered on
    the player or another target. It provides functionality to update its position,
    convert world coordinates to screen coordinates relative to the camera, and check
    whether a tile is visible within the camera's view.
    """
    def __init__(self, width, height):
        """
        Initialize the Camera object.

        Args:
            width (int): Width of the camera viewport in tiles.
            height (int): Height of the camera viewport in tiles.
        """
        self.width = width  # In tiles / cells
        self.height = height
        self.x = 0
        self.y = 0

    def update(self, player):
        """
        Update the camera position to center on the player.
        Ensures the camera does not move to negative coordinates.

        Args:
            player (Player): The player object, expected to have x and y attributes representing
                             position in world tile coordinates (float).
        """

        # Center the camera on the player (floating point for smooth movement)
        self.x = player.x - self.width // 2
        self.y = player.y - self.height // 2

        # Clamp to world boundaries to prevent negative coordinates
        if self.x < 0:
            self.x = 0
        if self.y < 0:
            self.y = 0

    def apply(self, x, y):
        """
        Convert world tile coordinates to camera-relative coordinates (screen coordinates in tiles).

        Args:
            x (int or float): X coordinate in world tile units.
            y (int or float): Y coordinate in world tile units.

        Returns:
            tuple: (x, y) coordinates relative to the camera's top-left corner.
        """
        return x - self.x, y - self.y

    def is_visible(self, x, y):
        """
        Check if a tile at world coordinates (x, y) is currently visible within the camera viewport.

        Args:
            x (int or float): X coordinate in world tile units.
            y (int or float): Y coordinate in world tile units.

        Returns:
            bool: True if the tile is within the camera's visible area, False otherwise.
        """
        return (self.x <= x < self.x + self.width) and (self.y <= y < self.y + self.height)


    def get_rect_entity(self):
        """
        Get the camera's bounding rectangle as a RectEntity object in pixel coordinates.

        Returns:
            RectEntity: Rectangle representing the camera's view area in pixels,
                        centered on the camera's viewport center.
        """
        # Camera's center in world space (tile-based)
        center_x = self.x + self.width / 2
        center_y = self.y + self.height / 2
        return RectEntity(
            center_x * TILE_SIZE,
            center_y * TILE_SIZE,
            self.width * TILE_SIZE,
            self.height * TILE_SIZE
        )
