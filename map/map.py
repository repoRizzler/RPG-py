from context.context import *
import pygame

class Map:
    """
   Represents a game map composed of a grid of tiles, including floors, walls, and exits.

   The map is constructed from a 'floor' object that provides the grid layout,
   dimensions, and exit position. The Map class provides functionality for drawing
   visible tiles based on a camera view, and for querying tile properties such as walls
   and exit positions.
   Attributes:
       floor (Floor): Floor object.
   """
    def __init__(self, floor):
        """
        Initialize the Map object from a floor object.

        Args:
            floor (Floor): A floor object containing the grid layout, width, height,
                           and exit position information.
        """
        self.floor = None
        self.grid = None
        self.width = 0
        self.height = 0
        self.set_floor(floor)

    def set_floor(self, floor):
        """
        Set the current floor to the provided floor object and initialize the map grid,
        width, height, and mark the exit position on the grid.

        Args:
            floor (Floor): The floor object to use as the current map layout.
        """
        self.floor = floor
        self.grid = floor.grid
        self.width = floor.width
        self.height = floor.height

        exit_pos = floor.level_exit
        self.grid[exit_pos[1]][exit_pos[0]] = 2

    def draw(self, screen, camera):

        """
        Draw the visible portion of the map to the screen using the camera's position and size.

        Args:
            screen (pygame.Surface): The surface to draw the map tiles on.
            camera (Camera): Camera object providing x, y position and visible width and height
                             in tile units.
        """

        cam_x_int =round(camera.x)
        cam_y_int =round(camera.y)
        for y in range(cam_y_int -1 , cam_y_int + camera.height + 1):
            for x in range(cam_x_int -1, cam_x_int + camera.width +1):
                if 0 <= x < self.width and 0 <= y < self.height:

                    screen_x, screen_y = camera.apply(x, y)
                    # pos_x, pos_y = x+cam_offset_x-camera.x, y+cam_offset_y - camera.y

                    rect = pygame.Rect(screen_x * TILE_SIZE, screen_y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    # rect = pygame.Rect(pos_x * TILE_SIZE, pos_y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    tile = self.grid[y][x]
                    if tile == 0:
                        pygame.draw.rect(screen, BLUE, rect, 1)
                        pygame.draw.rect(screen, GREY, rect)
                    elif tile == 1:
                        pygame.draw.rect(screen, BLACK, rect, 1)
                    elif tile == 2:
                        pygame.draw.rect(screen, GREY, rect)
                        pygame.draw.rect(screen, GREEN, rect,1)

    def is_wall(self, x, y):
        """
        Check if the tile at the specified coordinates is a wall.

        Args:
            x (int or float): X coordinate of the tile.
            y (int or float): Y coordinate of the tile.

        Returns:
            bool: True if the tile is a wall or out of bounds, False otherwise.
        """
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return True
        return self.grid[int(y)][int(x)] == 1
    def is_exit(self,x,y):
        """
        Check if the tile at the specified coordinates is the exit.

        Args:
            x (int or float): X coordinate of the tile.
            y (int or float): Y coordinate of the tile.

        Returns:
            bool: True if the tile is the exit or out of bounds, False otherwise.
        """
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return True
        return self.grid[int(y)][int(x)] == 2

    def is_wall_area(self, x, y, width=1.0, height=1.0):
        """
        Check if any corner of a rectangular area intersects a wall tile.
        Useful for collision detection for entities larger than one tile.

        Args:
            x (float): X coordinate of the top-left corner of the area.
            y (float): Y coordinate of the top-left corner of the area.
            width (float, optional): Width of the area in tiles (default 1.0).
            height (float, optional): Height of the area in tiles (default 1.0).

        Returns:
            bool: True if any corner of the area intersects a wall tile, False otherwise.
        """
        for corner_x in [x, x + width - 0.01]:
            for corner_y in [y, y + height - 0.01]:
                if self.is_wall(int(corner_x), int(corner_y)):
                    return True
        return False
    def on_exit(self, player, width=1.0, height=1.0):
        """
        Check if the player's bounding box is overlapping any exit tile.

        Args:
            player (Player): The player object, expected to have x and y attributes.
            width (float, optional): Width of the player's bounding box in tiles (default 1.0).
            height (float, optional): Height of the player's bounding box in tiles (default 1.0).

        Returns:
            bool: True if any corner of the player overlaps an exit tile, False otherwise.
        """
        x,y = round(player.x), round(player.y)
        for corner_x in [x, x + width - 0.01]:
            for corner_y in [y, y + height - 0.01]:
                if self.is_exit(int(corner_x), int(corner_y)):
                    return True
