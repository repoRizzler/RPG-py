import pygame
from typing import Dict, Any, Tuple, Optional, Union
from collections import OrderedDict


class DebugRenderer:
    """
    A flexible debug system for Pygame that can render debug information
    both through instance methods and static methods for global access.
    """

    # Class-level storage for static debug data
    _static_debug_data: Dict[str, Any] = OrderedDict()
    _static_enabled: bool = True

    def __init__(self, font_size: int = 16, font_name: Optional[str] = None,
                 text_color: Tuple[int, int, int] = (255, 255, 255),
                 background_color: Optional[Tuple[int, int, int]] = (0, 0, 0, 128),
                 padding: int = 5, line_spacing: int = 2):
        """
        Initialize the debug renderer.

        Args:
            font_size: Size of the debug text font
            font_name: Font name (None for default)
            text_color: RGB color for debug text
            background_color: RGBA color for background (None for no background)
            padding: Padding around the debug text block
            line_spacing: Extra spacing between lines
        """
        pygame.font.init()

        self.font = pygame.font.Font(font_name, font_size)
        self.text_color = text_color
        self.background_color = background_color
        self.padding = padding
        self.line_spacing = line_spacing

        # Instance-level debug data
        self.debug_data: Dict[str, Any] = OrderedDict()
        self.enabled = True

    def add_debug_info(self, key: str, value: Any) -> None:
        """Add or update debug information for this instance."""
        self.debug_data[key] = value

    def remove_debug_info(self, key: str) -> None:
        """Remove debug information for this instance."""
        self.debug_data.pop(key, None)

    def clear_debug_info(self) -> None:
        """Clear all instance debug information."""
        self.debug_data.clear()

    def set_enabled(self, enabled: bool) -> None:
        """Enable/disable debug rendering for this instance."""
        self.enabled = enabled

    @classmethod
    def add_static_debug_info(cls, key: str, value: Any) -> None:
        """Add or update static debug information (accessible from anywhere)."""
        cls._static_debug_data[key] = value

    @classmethod
    def remove_static_debug_info(cls, key: str) -> None:
        """Remove static debug information."""
        cls._static_debug_data.pop(key, None)

    @classmethod
    def clear_static_debug_info(cls) -> None:
        """Clear all static debug information."""
        cls._static_debug_data.clear()

    @classmethod
    def set_static_enabled(cls, enabled: bool) -> None:
        """Enable/disable static debug rendering globally."""
        cls._static_enabled = enabled

    def _format_value(self, value: Any) -> str:
        """Format a value for display."""
        if isinstance(value, float):
            return f"{value:.2f}"
        elif isinstance(value, (list, tuple)):
            if len(value) <= 4:  # Short sequences
                formatted_items = [self._format_value(item) for item in value]
                return f"({', '.join(formatted_items)})"
            else:
                return f"[{len(value)} items]"
        elif isinstance(value, dict):
            return f"{{+{len(value)} keys}}"
        else:
            return str(value)

    def _prepare_debug_lines(self) -> list[str]:
        """Prepare all debug lines for rendering."""
        lines = []

        # Add static debug data if enabled
        if self._static_enabled and self._static_debug_data:
            lines.append("=== GLOBAL DEBUG ===")
            for key, value in self._static_debug_data.items():
                formatted_value = self._format_value(value)
                lines.append(f"{key}: {formatted_value}")

            # Add separator if we have instance data too
            if self.enabled and self.debug_data:
                lines.append("")

        # Add instance debug data if enabled
        if self.enabled and self.debug_data:
            if self._static_enabled and self._static_debug_data:
                lines.append("=== INSTANCE DEBUG ===")

            for key, value in self.debug_data.items():
                formatted_value = self._format_value(value)
                lines.append(f"{key}: {formatted_value}")

        return lines

    def render(self, surface: pygame.Surface, position: Tuple[int, int] = (10, 10)) -> None:
        """
        Render debug information to the surface.

        Args:
            surface: Pygame surface to render to
            position: Top-left position to start rendering
        """
        if not self.enabled and not (self._static_enabled and self._static_debug_data):
            return

        lines = self._prepare_debug_lines()
        if not lines:
            return

        # Calculate dimensions
        line_height = self.font.get_height() + self.line_spacing
        max_width = max(self.font.size(line)[0] for line in lines) if lines else 0
        total_height = len(lines) * line_height - self.line_spacing  # Remove spacing from last line

        # Draw background if specified
        if self.background_color:
            bg_rect = pygame.Rect(
                position[0] - self.padding,
                position[1] - self.padding,
                max_width + 2 * self.padding,
                total_height + 2 * self.padding
            )

            # Create a surface with alpha for transparency
            if len(self.background_color) == 4:  # RGBA
                bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
                bg_surface.fill(self.background_color)
                surface.blit(bg_surface, bg_rect.topleft)
            else:  # RGB
                pygame.draw.rect(surface, self.background_color, bg_rect)

        # Render text lines
        x, y = position
        for line in lines:
            text_surface = self.font.render(line, True, self.text_color)
            surface.blit(text_surface, (x, y))
            y += line_height

    def get_debug_info_copy(self) -> Dict[str, Any]:
        """Get a copy of current instance debug information."""
        return self.debug_data.copy()

    @classmethod
    def get_static_debug_info_copy(cls) -> Dict[str, Any]:
        """Get a copy of current static debug information."""
        return cls._static_debug_data.copy()


# Example usage and helper functions
def example_usage():
    """Example of how to use the DebugRenderer in a Pygame game."""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Debug System Example")
    clock = pygame.time.Clock()

    # Create debug renderer instance
    debug_renderer = DebugRenderer(
        font_size=18,
        background_color=(0, 0, 50, 180),  # Semi-transparent dark blue
        padding=8
    )

    # Add some initial debug info
    debug_renderer.add_debug_info("FPS", 0)
    debug_renderer.add_debug_info("Player Pos", (0, 0))

    # Add static debug info (accessible from anywhere in your code)
    DebugRenderer.add_static_debug_info("Game State", "Playing")
    DebugRenderer.add_static_debug_info("Level", 1)

    player_x, player_y = 400, 300
    running = True

    while running:
        dt = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:  # Toggle debug
                    debug_renderer.set_enabled(not debug_renderer.enabled)
                elif event.key == pygame.K_s:  # Toggle static debug
                    DebugRenderer.set_static_enabled(not DebugRenderer._static_enabled)

        # Simulate player movement
        keys = pygame.key.get_pressed()
        speed = 200 * (dt / 1000.0)  # pixels per second
        if keys[pygame.K_LEFT]:
            player_x -= speed
        if keys[pygame.K_RIGHT]:
            player_x += speed
        if keys[pygame.K_UP]:
            player_y -= speed
        if keys[pygame.K_DOWN]:
            player_y += speed

        # Update debug information
        debug_renderer.add_debug_info("FPS", round(clock.get_fps(), 1))
        debug_renderer.add_debug_info("Player Pos", (round(player_x), round(player_y)))
        debug_renderer.add_debug_info("Keys Pressed", sum(keys))

        # Update static debug info from anywhere in your code
        DebugRenderer.add_static_debug_info("Mouse Pos", pygame.mouse.get_pos())
        DebugRenderer.add_static_debug_info("Mouse Pos1", pygame.mouse.get_pos())
        DebugRenderer.add_static_debug_info("Mouse Pos12", pygame.mouse.get_pos())
        DebugRenderer.add_static_debug_info("Mouse Pos121", pygame.mouse.get_pos())
        DebugRenderer.add_static_debug_info("Mouse Pos1211", pygame.mouse.get_pos())

        # Render everything
        screen.fill((20, 20, 20))

        # Draw a simple player representation
        pygame.draw.circle(screen, (255, 100, 100), (int(player_x), int(player_y)), 20)

        # Render debug information
        debug_renderer.render(screen, (10, 10))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    example_usage()