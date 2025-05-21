# game.py - Game class for handling main game logic
import pygame
from context.context import BLACK


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.current_time = 0

        # Game objects will be initialized in the setup method
        self.map = None
        self.player = None
        self.enemies = []
        self.projectiles = []

    def setup(self, game_map, player, enemies):
        """Set up the game with initial objects"""
        self.map = game_map
        self.player = player
        self.enemies = enemies
        self.projectiles = []

    def handle_events(self):
        """Process pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        """Update game state"""
        self.current_time = pygame.time.get_ticks()

        # Handle keyboard input for player movement
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_w]:
            dy = -1
        if keys[pygame.K_s]:
            dy = 1
        if keys[pygame.K_a]:
            dx = -1
        if keys[pygame.K_d]:
            dx = 1

        self.player.move(dx, dy, self.map)

        # Update enemies
        for enemy in self.enemies:
            enemy.update(self.player, self.map, self.projectiles, self.current_time)

        # Update projectiles
        for projectile in self.projectiles[:]:
            projectile.update(self.map, self.player)
            if not projectile.active:
                self.projectiles.remove(projectile)

    def render(self):
        """Render the game state"""
        # Clear the screen
        self.screen.fill(BLACK)

        # Draw map
        self.map.draw(self.screen)

        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(self.screen)

        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)

        # Draw player
        self.player.draw(self.screen)

        # Update display
        pygame.display.flip()

    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(60)  # 60 FPS

        # Cleanup when game ends
        return False