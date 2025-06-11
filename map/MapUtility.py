import json
import os
from typing import Optional, Dict, List, Any

from map.Level import Level


class MapUtility:
    """Utility class for loading, saving, and managing map files."""

    @staticmethod
    def load_level(filepath: str) -> Optional[Level]:
        """
        Load level from JSON file.

        Args:
            filepath: Path to the JSON file

        Returns:
            Level object or None if loading failed
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)

            level = Level(data, filepath)
            return level

        except FileNotFoundError:
            print(f"Error: File '{filepath}' not found")
            return None
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in '{filepath}': {e}")
            return None
        except Exception as e:
            print(f"Error loading '{filepath}': {e}")
            return None

    @staticmethod
    def save_level(level: Level, filepath: str) -> bool:
        """
        Save level to JSON file.

        Args:
            level: Level object to save
            filepath: Path where to save the file

        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            with open(filepath, 'w') as f:
                json.dump(level.to_dict(), f, indent=2)

            level.filename = filepath
            return True

        except Exception as e:
            print(f"Error saving to '{filepath}': {e}")
            return False

    @staticmethod
    def list_map_files(directory: str = "maps") -> List[str]:
        """
        List all JSON map files in directory.

        Args:
            directory: Directory to search for map files

        Returns:
            List of filenames (without full path)
        """
        try:
            if not os.path.exists(directory):
                return []

            files = []
            for filename in os.listdir(directory):
                if filename.endswith('.json'):
                    files.append(filename)

            return sorted(files)

        except Exception as e:
            print(f"Error listing files in '{directory}': {e}")
            return []

    @staticmethod
    def get_level_info(filepath: str) -> Optional[Dict[str, Any]]:
        """
        Get basic information about a level without fully loading it.

        Args:
            filepath: Path to the JSON file

        Returns:
            Dictionary with level info or None if failed
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)

            floors_data = data.get("floors", [])
            info = {
                "filename": os.path.basename(filepath),
                "floor_count": len(floors_data),
                "floors": []
            }

            for i, floor_data in enumerate(floors_data):
                grid = floor_data.get("grid", [])
                height = len(grid)
                width = len(grid[0]) if height > 0 else 0

                floor_info = {
                    "index": i,
                    "dimensions": f"{width}x{height}",
                    "has_player_start": floor_data.get("player_start") is not None,
                    "has_exit": floor_data.get("level_exit") is not None,
                    "enemy_count": len(floor_data.get("enemies", [])),
                    "item_count": len(floor_data.get("items", []))
                }
                info["floors"].append(floor_info)

            return info

        except Exception as e:
            print(f"Error getting info for '{filepath}': {e}")
            return None

