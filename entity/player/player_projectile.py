from entity.projectile import *


class PlayerProjectile(Projectile):
    """
    Projectile fired by the player, with damage, speed, and distance limitations.

    Inherits from:
        Projectile: Base class for projectile behavior and rendering.

    Attributes:
        origin_x (float): X-coordinate where the projectile was created.
        origin_y (float): Y-coordinate where the projectile was created.
        max_distance (float): Maximum distance the projectile can travel before deactivating.
        speed (float): Speed of the projectile.
        color (tuple[int, int, int]): Color used to represent the projectile visually.
    """
    def __init__(self, x, y, angle, damage, max_distance, speed=0.4):
        """
        Initializes a player projectile with specified position, direction, and properties.

        Args:
            x (float): Starting x-position of the projectile.
            y (float): Starting y-position of the projectile.
            angle (float): Direction of movement in radians.
            damage (int): Amount of damage the projectile deals.
            max_distance (float): How far the projectile can travel before deactivating.
            speed (float, optional): Movement speed of the projectile. Defaults to 0.4.
        """
        super().__init__(x, y, angle, damage)
        self.origin_x = x # player x /  source of the projectile
        self.origin_y = y # player y / source of the projectile
        self.max_distance = max_distance
        self.speed = speed
        self.color = BLUE

    def update(self, game_map, player,enemies,camera):
        """
       Updates the projectile's position and checks for collisions and distance limits.

       Movement is applied based on angle and speed. The projectile is deactivated if it:
       - Exceeds its max distance (currently commented out),
       - Collides with a wall,
       - Collides with any enemy.

       Args:
           game_map (Map): Current map, used to check for wall collisions.
           player (Player): The player that fired the projectile (not currently used).
           enemies (list[Enemy]): List of potential enemy targets.
           camera (Camera): Camera for coordinate transformation (passed to super).

       Returns:
           None
       """
        # Move projectile in the direction of its angle
        dx = math.cos(self.angle) * self.speed
        dy = math.sin(self.angle) * self.speed

        self.x += dx
        self.y += dy

        super().update(game_map,player,enemies,camera)
        print("player proj.")
        print(f"pos: {self.pos}")
        print(f"pos x-y: {self.pos.x}-{self.pos.y}")
        print(f"x: {self.x}, y: {self.y}")
        print(f"origin x: {self.origin_x},origin y: {self.origin_y}")


        # Check if projectile has exceeded max distance

        # distance = math.sqrt((self.x - self.origin_x) ** 2 + (self.y - self.origin_y) ** 2)
        # if distance > self.max_distance:
        #     self.active = False
        #     return

        # Check for collision with walls
        if game_map.is_wall(self.x, self.y):
            self.active = False
            return

        # Check for collision with enemies
        for enemy in enemies:
            if self.collides_with_rect(enemy):
                enemy.take_damage(self.damage)
                self.active = False
                return
            if math.sqrt((self.x - enemy.x) ** 2 + (self.y - enemy.y) ** 2) < 0.5:
                enemy.take_damage(self.damage)
                self.active = False
                return

    def draw(self, screen):
        """
       Draws the projectile on the screen using screen coordinates.

       Args:
           screen (pygame.Surface): Surface to draw the projectile on.

       Returns:
           None
       """
        center_x = int((self.x + 0.5) * TILE_SIZE)
        center_y = int((self.y + 0.5) * TILE_SIZE)
        # pygame.draw.circle(screen, self.color, (center_x, center_y), TILE_SIZE // 8)
        super().draw(screen)

