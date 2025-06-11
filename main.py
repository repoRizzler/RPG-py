import sys

from entity.enemy.melee_enemy import MeleeEnemy
from entity.enemy.ranged_enemy import RangedEnemy
from game import Game
from entity.player.player import Player
from map.MapUtility import MapUtility
from map.map import *
import pygame


# map_path = "./LevelEditor/maps/demo_level_1.json"
map_path = "./LevelEditor/maps/map_test.json"
def add_debug_info(str):
    # Font setup
    font = pygame.font.SysFont(None, 36)  # Use default font, size 36

    # Render each line separately to support line breaks
    lines = str.split('\n')

    for i, line in enumerate(lines):
        text_surface = font.render(line, True, (255, 255, 255))  # White text
        pygame.screen.blit(text_surface, (10, 10 + i * 36))  # 10 px from top-left, with line spacing


# main.py - Entry point for the game
def load_level():
    print("\n Loading level...")
    level = MapUtility.load_level(map_path)
    if level:
        print(f"Loaded: {level}")

        # Show level info
        info = MapUtility.get_level_info(map_path)
        if info:
            print(f"Level info: {info['floor_count']} floors")
            for floor_info in info['floors']:
                print(f"  Floor {floor_info['index'] + 1}: {floor_info['dimensions']}, "
                      f"{floor_info['enemy_count']} enemies, {floor_info['item_count']} items")
        return level
    raise IOError("Level not found")
def main():

    # Initialize pygame
    pygame.init()

    # Create the game window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Python RPG Game")

    # Create game objects
    level = load_level()
    game_map = Map(level.floors[0])
    # player = Player(1, 1)
    # enemies = [
    #     MeleeEnemy(8, 2),
    #     RangedEnemy(4, 8)
    # ]

    # Create and run the game
    game = Game(screen)
    game.setup(level,game_map)

    # Start the game loop
    try:
        game.run()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Cleanup
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    main()

