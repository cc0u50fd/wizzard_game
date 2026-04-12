"""Viewport scrolling for scenes wider/taller than the screen."""
from engine.settings import SCREEN_WIDTH, SCREEN_HEIGHT, CAMERA_SMOOTHING, CAMERA_DEAD_ZONE


class Camera:
    """Smooth-follow camera that tracks the player for wide scenes."""

    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.scene_width = SCREEN_WIDTH
        self.scene_height = SCREEN_HEIGHT

    def set_scene_bounds(self, width, height):
        self.scene_width = max(width, SCREEN_WIDTH)
        self.scene_height = max(height, SCREEN_HEIGHT)

    def set_position(self, x, y):
        """Snap camera to position immediately."""
        self.x = x - SCREEN_WIDTH // 2
        self.y = y - SCREEN_HEIGHT // 2
        self._clamp()

    def update(self, target_x, target_y, dt):
        """Smoothly follow a target position."""
        desired_x = target_x - SCREEN_WIDTH // 2
        desired_y = target_y - SCREEN_HEIGHT // 2

        # Smooth interpolation
        factor = min(1.0, CAMERA_SMOOTHING * dt)
        self.x += (desired_x - self.x) * factor
        self.y += (desired_y - self.y) * factor
        self._clamp()

    def _clamp(self):
        max_x = self.scene_width - SCREEN_WIDTH
        max_y = self.scene_height - SCREEN_HEIGHT
        self.x = max(0, min(self.x, max_x))
        self.y = max(0, min(self.y, max_y))

    def apply(self, world_x, world_y):
        """Convert world coordinates to screen coordinates."""
        return (world_x - int(self.x), world_y - int(self.y))

    def apply_rect(self, rect):
        """Convert a world-space rect to screen-space."""
        return rect.move(-int(self.x), -int(self.y))

    def screen_to_world(self, screen_x, screen_y):
        """Convert screen coordinates to world coordinates."""
        return (screen_x + int(self.x), screen_y + int(self.y))

    @property
    def offset(self):
        return (int(self.x), int(self.y))
