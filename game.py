# game.py - Game class for handling main game logic
import pygame
from context.context import BLACK, DEBUG_MODE, BASIC_VIEW_WIDTH, BASIC_VIEW_HEIGHT, VIEWPORT_WIDTH, VIEWPORT_HEIGHT, \
    VIEW_WIDTH_PX, VIEW_HEIGHT_PX
from entity.player.player import Player
from utilities.DebugRenderer import DebugRenderer
from utilities.camera import Camera


class Game:
    """
    The main game controller class that manages the game loop,
    game state, player, enemies, projectiles, camera, and rendering.

    Attributes:
        general_view (bool): If True, shows the entire map instead of the viewport.
        screen (pygame.Surface): The main screen surface for rendering.
        clock (pygame.time.Clock): Clock object to manage frame rate.
        running (bool): Controls the main loop execution.
        current_time (int): Current game time in milliseconds.
        map (Map): The current game map.
        level (Level): The current level structure containing multiple floors.
        current_floor (int): Index of the currently active floor.
        player (Player): The player entity.
        enemies (list): List of enemy entities on the current floor.
        projectiles (list): List of active projectiles in the game.
        camera (Camera): Camera that defines the current view window.
        debug_mode (bool): If True, renders debug information.
        debug_renderer (DebugRenderer): Utility to show debug data on the screen.
    """
    def __init__(self, screen):
        """
        Initialize the Game class.

        Args:
            screen (pygame.Surface): The main surface to draw the game on.
        """
        self.general_view = False
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.current_time = 0

        # Game objects will be initialized in the setup method
        self.map = None
        self.level = None
        self.current_floor = 0
        self.player = None

        self.enemies = []

        self.projectiles = []

        self.camera = None

        # debug utils
        self.debug_mode = True
        self.debug_renderer = DebugRenderer()


    def setup(self, level, game_map):
        """
        Set up the initial game state with the given level and map.

        Args:
            level (Level): The level object containing floor data and entities.
            game_map (Map): The map layout for rendering and collision.
        """
        self.level = level
        self.map = game_map

        player_pos = level.floors[0].player_start
        self.player = Player(player_pos[0], player_pos[1])

        self.enemies = level.floors[0].get_enemies()

        self.projectiles = []
        # self.camera = Camera(BASIC_VIEW_WIDTH, BASIC_VIEW_HEIGHT)
        self.camera = Camera(VIEWPORT_WIDTH, VIEWPORT_HEIGHT)

    def handle_events(self):
        """
        Handle input events such as quit requests.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        """
        Update the game state, including player, enemies, projectiles,
        and debug information.
        """
        self.current_time = pygame.time.get_ticks()
        self.camera.update(self.player)
        # Handle keyboard input for player movement
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_1]:
            self.player.change_weapon_up()
        if keys[pygame.K_2]:
            self.player.change_weapon_down()
        if keys[pygame.K_w]:
            dy = -1
        if keys[pygame.K_s]:
            dy = 1
        if keys[pygame.K_a]:
            dx = -1
        if keys[pygame.K_d]:
            dx = 1
        if keys[pygame.K_e]:
            self.on_action()
        if keys[pygame.K_SPACE]:
            self.player.attack(self.camera,self.current_time,projectiles=self.projectiles, enemies=self.enemies, game_map=self.map)
        # Toggle key (TAB) to switch view modea
        if keys[pygame.K_TAB]:
            self.general_view = not self.general_view
            print("on camera change")
            pygame.time.wait(150)  # Small delay to prevent rapid toggling
        # pass

        self.player.move(dx, dy, self.map)

        self.player.update(self.enemies,self.camera, self.current_time)
        # Update enemies
        for enemy in self.enemies:
            enemy.update(self.camera,self.player, self.map, self.projectiles, self.current_time)

        # Update projectiles
        for projectile in self.projectiles[:]:
            projectile.update(self.map, self.player,self.enemies,self.camera)
            if not projectile.active:
                self.projectiles.remove(projectile)

        # debug setup
        self.debug_renderer.add_debug_info("PLAYER DATA", "==========================")
        self.debug_renderer.add_debug_info("player pos:", f"x:{self.player.x} y:{self.player.y}")
        self.debug_renderer.add_debug_info("player-mouse direction:", self.player.get_angle_to_mouse())


        self.debug_renderer.add_debug_info("WEAPON DATA", "==========================")


        player_weapon_debug_dict = self.player.get_weapon_debug_info()
        if player_weapon_debug_dict is not None:
            for key in player_weapon_debug_dict:
                item = player_weapon_debug_dict[key]
                self.debug_renderer.add_debug_info(f"{key} ", item)

    def render(self):
        """
        Render the current game state including the map, player, enemies,
        projectiles, and optionally debug info.
        """
        # Clear the screen
        self.screen.fill(BLACK)

        # Draw map in current view
        self.map.draw(self.screen, self.camera)


        # Draw camera border
        camera_rect = self.camera.get_rect_entity()
        camera_rect.draw_hit_box(self.screen)

        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(self.screen)

        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen,self.camera)

        # Draw player
        self.player.draw(self.screen, self.current_time)

        # add debug info
        if DEBUG_MODE:
            self.debug_renderer.render(self.screen, (10, 10))

        if self.general_view:
            # Show entire map
            self.camera.x = 0
            self.camera.y = 0
            self.camera.width = self.map.width
            self.camera.height = self.map.height
            self.camera.update(self.player)


        else:
            # Reset to viewport size (e.g., 15x10)
            self.camera.width = VIEWPORT_WIDTH
            self.camera.height = VIEWPORT_HEIGHT
            self.camera.update(self.player)


        # Update display
        pygame.display.flip()

    def run(self):
        """
        Render the current game state including the map, player, enemies,
        projectiles, and optionally debug info.
        """
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(60)  # 60 FPS

        # Cleanup when game ends
        return False

    def on_action(self):
        """
        Handle special action input, such as transitioning to the next floor.
        """
        if self.map.on_exit(self.player):
            if self.level.get_floor_count() > self.current_floor+1:
                self.current_floor += 1
                floor = self.level.get_floor(self.current_floor)
                self.map.set_floor(floor)

                self.player.set_position(floor.player_start[0], floor.player_start[1])

            else:
                self.on_game_end()

    def on_game_end(self):
        """
        Handle logic for when the game ends.
        """
        pass
