import sys

from entity.enemy.melee_enemy import MeleeEnemy
from entity.enemy.ranged_enemy import RangedEnemy
from game import Game
from entity.player import *
from map import *
import pygame

def add_debug_info(str):
    # Font setup
    font = pygame.font.SysFont(None, 36)  # Use default font, size 36

    # Render each line separately to support line breaks
    lines = str.split('\n')

    for i, line in enumerate(lines):
        text_surface = font.render(line, True, (255, 255, 255))  # White text
        pygame.screen.blit(text_surface, (10, 10 + i * 36))  # 10 px from top-left, with line spacing


# main.py - Entry point for the game


def main():
    # Initialize pygame
    pygame.init()

    # Create the game window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Python RPG Game")

    # Create game objects
    game_map = Map(GRID_SIZE, GRID_SIZE)
    player = Player(1, 1)
    enemies = [
        MeleeEnemy(8, 2),
        RangedEnemy(4, 8)
    ]

    # Create and run the game
    game = Game(screen)
    game.setup(game_map, player, enemies)

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

