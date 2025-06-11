from typing import Optional, Dict, List, Any

from map.floor import Floor


class Level:
    """Represents a complete level with multiple floors."""

    def __init__(self, level_data: Dict[str, Any] = None, filename: str = None):
        """
        Initialize level from data dictionary or create empty level.

        Args:
            level_data: Dictionary containing level data from JSON
            filename: Original filename if loaded from file
        """
        self.filename = filename
        self.floors = []

        if level_data is None:
            # Create default single floor level
            self.add_floor()
        else:
            # Load floors from data
            floors_data = level_data.get("floors", [])
            for floor_data in floors_data:
                self.floors.append(Floor(floor_data))

    def add_floor(self, floor_data: Dict[str, Any] = None) -> Floor:
        """Add a new floor to the level."""
        new_floor = Floor(floor_data)
        self.floors.append(new_floor)
        return new_floor

    def get_floor(self, floor_index: int) -> Optional[Floor]:
        """Get floor by index. Returns None if index is invalid."""
        if 0 <= floor_index < len(self.floors):
            return self.floors[floor_index]
        return None

    def remove_floor(self, floor_index: int) -> bool:
        """Remove floor by index. Returns True if successful."""
        if 0 <= floor_index < len(self.floors) and len(self.floors) > 1:
            self.floors.pop(floor_index)
            return True
        return False

    def get_floor_count(self) -> int:
        """Get total number of floors."""
        return len(self.floors)

    def validate_level(self) -> List[str]:
        """Validate level structure and return list of issues found."""
        issues = []

        if not self.floors:
            issues.append("Level has no floors")
            return issues

        for i, floor in enumerate(self.floors):
            if not floor.player_start and i == 0:
                issues.append(f"Floor {i + 1}: Missing player start position")

            if not floor.level_exit and i < len(self.floors) - 1:
                issues.append(f"Floor {i + 1}: Missing exit (required for non-final floors)")

            if floor.width == 0 or floor.height == 0:
                issues.append(f"Floor {i + 1}: Invalid dimensions ({floor.width}x{floor.height})")

            # Check if player start is on walkable tile
            if floor.player_start:
                x, y = floor.player_start
                if not floor.is_walkable(x, y):
                    issues.append(f"Floor {i + 1}: Player start is on non-walkable tile")

            # Check if exit is on walkable tile
            if floor.level_exit:
                x, y = floor.level_exit
                if not floor.is_walkable(x, y):
                    issues.append(f"Floor {i + 1}: Level exit is on non-walkable tile")

        return issues

    def to_dict(self) -> Dict[str, Any]:
        """Convert level to dictionary for JSON serialization."""
        return {
            "floors": [floor.to_dict() for floor in self.floors]
        }

    def __str__(self) -> str:
        return f"Level({len(self.floors)} floors, file: {self.filename or 'unsaved'})"
