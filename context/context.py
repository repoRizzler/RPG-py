# Constants
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640


#grid settings

GRID_WIDTH = 100
GRID_HEIGHT = 100

VIEWPORT_WIDTH = 15
VIEWPORT_HEIGHT = 10

TILE_SIZE = SCREEN_HEIGHT / VIEWPORT_HEIGHT

#Camera settings
BASIC_VIEW_WIDTH = 340
BASIC_VIEW_HEIGHT = 340

# Viewport surface size (camera render target)
VIEW_WIDTH_PX = VIEWPORT_WIDTH * TILE_SIZE
VIEW_HEIGHT_PX = VIEWPORT_HEIGHT * TILE_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BROWN = (139, 69, 19)
GREY = (100, 100, 100)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)


# debug data
DEBUG_MODE = False
show_HitBox = True
show_player_info = True
show_enemy_info = True


# Player Weapon basic stats
RANGE_WEAPON_LENGTH = 25
RANGE_WEAPON_WIDTH = 10
MELEE_WEAPON_LENGTH = 50
MELEE_WEAPON_WIDTH = 10


# enemy basic stats
ENEMY_WIDTH = TILE_SIZE // 3
ENEMY_HEIGHT = TILE_SIZE // 3


## player data
PLAYER_SIZE = TILE_SIZE // 3
