from typing import Optional, Dict, List, Any, Tuple

from context.map_context import *
from entity.enemy.enemy import Enemy
from entity.enemy.melee_enemy import MeleeEnemy
from entity.enemy.ranged_enemy import RangedEnemy
from entity.weapon.MeleeWeapon import MeleeWeapon


class Floor:
    """Represents a single floor in a level with all its entities and terrain."""

    def __init__(self, floor_data: Dict[str, Any] = None):
        """
        Initialize a floor from data dictionary or create empty floor.

        Args:
            floor_data: Dictionary containing floor data from JSON
        """
        if floor_data is None:
            floor_data = {
                "grid": [[FLOOR_TILE for _ in range(30)] for _ in range(20)],
                "player_start": None,
                "level_exit": None,
                "enemies": [],
                "items": []
            }

        self.grid = floor_data.get("grid", [])
        self.player_start = floor_data.get("player_start")
        self.level_exit = floor_data.get("level_exit")
        self.enemies = floor_data.get("enemies", [])
        self.items = floor_data.get("items", [])

        # Calculate dimensions
        self.height = len(self.grid)
        self.width = len(self.grid[0]) if self.height > 0 else 0

    def get_tile(self, x: int, y: int) -> int:
        """Get tile type at position (x, y)."""
        if 0 <= y < self.height and 0 <= x < self.width:
            return self.grid[y][x]
        return WALL_TILE  # Out of bounds is considered wall

    def set_tile(self, x: int, y: int, tile_type: int) -> bool:
        """Set tile type at position (x, y). Returns True if successful."""
        if 0 <= y < self.height and 0 <= x < self.width:
            self.grid[y][x] = tile_type
            return True
        return False

    def is_walkable(self, x: int, y: int) -> bool:
        """Check if position is walkable (not a wall)."""
        return self.get_tile(x, y) != WALL_TILE

    def get_enemies_at(self, x: int, y: int) -> List[Dict[str, Any]]:
        """Get all enemies at position (x, y)."""
        return [enemy for enemy in self.enemies if enemy.get("pos") == [x, y]]

    def get_items_at(self, x: int, y: int) -> List[Dict[str, Any]]:
        """Get all items at position (x, y)."""
        return [item for item in self.items if item.get("pos") == [x, y]]

    def add_enemy(self, x: int, y: int, enemy_type: str) -> bool:
        """Add enemy at position. Returns True if successful."""
        if self.is_walkable(x, y):
            self.enemies.append({"type": enemy_type, "pos": [x, y]})
            return True
        return False

    def add_item(self, x: int, y: int, item_subtype: str) -> bool:
        """Add item at position. Returns True if successful."""
        if self.is_walkable(x, y):
            self.items.append({"subtype": item_subtype, "pos": [x, y]})
            return True
        return False

    def remove_enemies_at(self, x: int, y: int) -> int:
        """Remove all enemies at position. Returns count of removed enemies."""
        initial_count = len(self.enemies)
        self.enemies = [enemy for enemy in self.enemies if enemy.get("pos") != [x, y]]
        return initial_count - len(self.enemies)

    def remove_items_at(self, x: int, y: int) -> int:
        """Remove all items at position. Returns count of removed items."""
        initial_count = len(self.items)
        self.items = [item for item in self.items if item.get("pos") != [x, y]]
        return initial_count - len(self.items)

    def get_spawn_points(self) -> List[Tuple[int, int]]:
        """Get all valid spawn points (walkable tiles without entities)."""
        spawn_points = []
        for y in range(self.height):
            for x in range(self.width):
                if (self.is_walkable(x, y) and
                        not self.get_enemies_at(x, y) and
                        not self.get_items_at(x, y) and
                        [x, y] != self.player_start and
                        [x, y] != self.level_exit):
                    spawn_points.append((x, y))
        return spawn_points

    def to_dict(self) -> Dict[str, Any]:
        """Convert floor to dictionary for JSON serialization."""
        return {
            "grid": self.grid,
            "player_start": self.player_start,
            "level_exit": self.level_exit,
            "enemies": self.enemies,
            "items": self.items
        }
    def get_enemies(self):
        res = []
        for e in self.enemies:
            if e["type"] == "melee":
                pos = e["pos"]
                res.append(MeleeEnemy(pos[0], pos[1]))
            elif e["type"] == "ranged":
                pos = e["pos"]
                res.append(RangedEnemy(pos[0], pos[1]))
        return res
    def __str__(self) -> str:
        return f"Floor({self.width}x{self.height}, {len(self.enemies)} enemies, {len(self.items)} items)"
