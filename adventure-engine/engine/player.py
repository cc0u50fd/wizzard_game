"""Player character - movement, animation, depth scaling."""
import math
import pygame
from engine.settings import (
    WALK_SPEED, RUN_SPEED, ANIM_FPS,
    DEFAULT_HORIZON_Y, DEFAULT_GROUND_Y,
    DEFAULT_MIN_SCALE, DEFAULT_MAX_SCALE,
)
from engine.sprite_sheet import PlaceholderSprites


class Player:
    """The player character."""

    def __init__(self):
        # Position (float, foot anchor point)
        self.x = 400.0
        self.y = 550.0
        self.facing = "right"

        # Movement
        self.path = []  # List of waypoints to follow
        self.moving = False
        self.running = False
        self.speed = WALK_SPEED
        self.on_arrive_callback = None

        # Animation — try real sprites, fall back to placeholder
        self.frames = PlaceholderSprites.load_player_walk_frames()
        if self.frames is None:
            self.frames = PlaceholderSprites.create_player_frames()
        self.current_anim = "idle_right"
        self.anim_timer = 0.0
        self.anim_index = 0

        # Depth scaling config (set by scene)
        self.horizon_y = DEFAULT_HORIZON_Y
        self.ground_y = DEFAULT_GROUND_Y
        self.min_scale = DEFAULT_MIN_SCALE
        self.max_scale = DEFAULT_MAX_SCALE

        # Scaled dimensions (updated each frame)
        self.scale = 1.0
        self._update_scale()

    def set_depth_config(self, horizon_y, ground_y, min_scale, max_scale):
        self.horizon_y = horizon_y
        self.ground_y = ground_y
        self.min_scale = min_scale
        self.max_scale = max_scale
        self._update_scale()

    def set_position(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.path = []
        self.moving = False
        self._update_scale()

    def walk_to(self, path, running=False, callback=None):
        """Start walking along a path (list of (x, y) waypoints)."""
        if not path:
            if callback:
                callback()
            return
        self.path = list(path)
        self.moving = True
        self.running = running
        self.speed = RUN_SPEED if running else WALK_SPEED
        self.on_arrive_callback = callback

        # Face toward first waypoint
        dx = self.path[0][0] - self.x
        if dx > 0:
            self.facing = "right"
        elif dx < 0:
            self.facing = "left"

    def stop(self):
        self.path = []
        self.moving = False
        self.running = False
        self.on_arrive_callback = None

    def face(self, direction):
        if direction in ("left", "right"):
            self.facing = direction

    def update(self, dt):
        if self.moving and self.path:
            target = self.path[0]
            dx = target[0] - self.x
            dy = target[1] - self.y
            dist = math.sqrt(dx * dx + dy * dy)

            move_dist = self.speed * dt

            if dist <= move_dist:
                # Reached waypoint
                self.x = target[0]
                self.y = target[1]
                self.path.pop(0)

                if not self.path:
                    # Reached final destination
                    self.moving = False
                    self.running = False
                    callback = self.on_arrive_callback
                    self.on_arrive_callback = None
                    if callback:
                        callback()
                else:
                    # Face next waypoint
                    next_dx = self.path[0][0] - self.x
                    if next_dx > 0:
                        self.facing = "right"
                    elif next_dx < 0:
                        self.facing = "left"
            else:
                # Move toward waypoint
                self.x += (dx / dist) * move_dist
                self.y += (dy / dist) * move_dist

                # Update facing
                if dx > 0:
                    self.facing = "right"
                elif dx < 0:
                    self.facing = "left"

        # Update animation
        self._update_animation(dt)
        self._update_scale()

    def _update_animation(self, dt):
        if self.moving:
            if self.running:
                anim_name = f"run_{self.facing}"
            else:
                anim_name = f"walk_{self.facing}"
        else:
            anim_name = f"idle_{self.facing}"

        # Reset index if animation changed
        if anim_name != self.current_anim:
            self.current_anim = anim_name
            self.anim_index = 0
            self.anim_timer = 0.0

        # Advance frame
        anim_frames = self.frames.get(self.current_anim, [])
        if len(anim_frames) > 1:
            self.anim_timer += dt
            frame_duration = 1.0 / ANIM_FPS
            if self.anim_timer >= frame_duration:
                self.anim_timer -= frame_duration
                self.anim_index = (self.anim_index + 1) % len(anim_frames)

    def _update_scale(self):
        range_y = self.ground_y - self.horizon_y
        if range_y <= 0:
            self.scale = self.max_scale
        else:
            t = max(0.0, min(1.0, (self.y - self.horizon_y) / range_y))
            self.scale = self.min_scale + (self.max_scale - self.min_scale) * t

    def get_current_frame(self):
        """Return the current animation frame, scaled for depth."""
        anim_frames = self.frames.get(self.current_anim, [])
        if not anim_frames:
            # Fallback: return a tiny placeholder
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            pygame.draw.rect(s, (255, 0, 0), (0, 0, 16, 16))
            return s

        frame = anim_frames[self.anim_index % len(anim_frames)]

        if abs(self.scale - 1.0) > 0.01:
            new_w = max(1, int(frame.get_width() * self.scale))
            new_h = max(1, int(frame.get_height() * self.scale))
            frame = pygame.transform.scale(frame, (new_w, new_h))

        return frame

    def get_draw_pos(self):
        """Get the top-left position for drawing (anchor is at feet)."""
        frame = self.get_current_frame()
        return (int(self.x - frame.get_width() // 2),
                int(self.y - frame.get_height()))

    def get_head_pos(self):
        """Get approximate head position for speech bubbles."""
        frame = self.get_current_frame()
        return (int(self.x), int(self.y - frame.get_height() - 5))

    def get_rect(self):
        """Get the bounding rect for the player sprite."""
        frame = self.get_current_frame()
        pos = self.get_draw_pos()
        return pygame.Rect(pos[0], pos[1], frame.get_width(), frame.get_height())

    @property
    def foot_pos(self):
        return (self.x, self.y)
