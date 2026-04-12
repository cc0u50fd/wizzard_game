"""NPC base class and companion character with auto-follow AI."""
import math
import pygame
from engine.settings import (
    WALK_SPEED, ANIM_FPS, COMPANION_FOLLOW_DISTANCE, COMPANION_FOLLOW_SPEED_MULT,
    DEFAULT_HORIZON_Y, DEFAULT_GROUND_Y, DEFAULT_MIN_SCALE, DEFAULT_MAX_SCALE,
    PLACEHOLDER_SCALE,
)
from engine.sprite_sheet import PlaceholderSprites


class Character:
    """Base NPC character."""

    def __init__(self, data, frames=None):
        self.id = data.get("id", "npc")
        self.name = data.get("name", "NPC")
        self.x = float(data.get("x", 400))
        self.y = float(data.get("y", 550))
        self.facing = data.get("facing", "right")
        self.speed = data.get("speed", WALK_SPEED)
        self.dialogue_id = data.get("dialogue_id")

        # Scene placement
        self.scene_id = data.get("scene_id")

        # Movement
        self.path = []
        self.moving = False
        self.on_arrive_callback = None

        # Animation
        self.frames = frames or self._create_placeholder_frames()
        self.current_anim = f"idle_{self.facing}"
        self.anim_timer = 0.0
        self.anim_index = 0

        # Depth scaling (set by scene)
        self.horizon_y = DEFAULT_HORIZON_Y
        self.ground_y = DEFAULT_GROUND_Y
        self.min_scale = DEFAULT_MIN_SCALE
        self.max_scale = DEFAULT_MAX_SCALE
        self.scale = 1.0

    def _create_placeholder_frames(self):
        """Create simple NPC placeholder frames."""
        frames = {}
        s = PLACEHOLDER_SCALE
        w, h = 28 * s, 52 * s

        def make_frame(leg_offset=0):
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            # Head
            pygame.draw.circle(surf, (255, 210, 170), (w // 2, 10 * s), 7 * s)
            # Body (dark blue)
            pygame.draw.rect(surf, (40, 40, 100), (w // 2 - 6 * s, 17 * s, 12 * s, 16 * s))
            # Legs
            pygame.draw.rect(surf, (50, 50, 50), (w // 2 - 5 * s - leg_offset * s, 33 * s, 5 * s, 14 * s))
            pygame.draw.rect(surf, (50, 50, 50), (w // 2 + leg_offset * s, 33 * s, 5 * s, 14 * s))
            # Shoes
            pygame.draw.rect(surf, (30, 30, 30), (w // 2 - 6 * s - leg_offset * s, 47 * s, 7 * s, 3 * s))
            pygame.draw.rect(surf, (30, 30, 30), (w // 2 - 1 * s + leg_offset * s, 47 * s, 7 * s, 3 * s))
            return surf

        idle = [make_frame(0)]
        frames["idle_right"] = idle
        frames["idle_left"] = [pygame.transform.flip(f, True, False) for f in idle]
        walk = [make_frame(0), make_frame(1), make_frame(0), make_frame(-1)]
        frames["walk_right"] = walk
        frames["walk_left"] = [pygame.transform.flip(f, True, False) for f in walk]
        return frames

    def set_depth_config(self, horizon_y, ground_y, min_scale, max_scale):
        self.horizon_y = horizon_y
        self.ground_y = ground_y
        self.min_scale = min_scale
        self.max_scale = max_scale

    def set_position(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def walk_to(self, path, callback=None):
        if not path:
            if callback:
                callback()
            return
        self.path = list(path)
        self.moving = True
        self.on_arrive_callback = callback
        dx = self.path[0][0] - self.x
        if dx > 0:
            self.facing = "right"
        elif dx < 0:
            self.facing = "left"

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
                self.x, self.y = target[0], target[1]
                self.path.pop(0)
                if not self.path:
                    self.moving = False
                    cb = self.on_arrive_callback
                    self.on_arrive_callback = None
                    if cb:
                        cb()
                else:
                    next_dx = self.path[0][0] - self.x
                    if next_dx > 0:
                        self.facing = "right"
                    elif next_dx < 0:
                        self.facing = "left"
            else:
                self.x += (dx / dist) * move_dist
                self.y += (dy / dist) * move_dist
                if dx > 0:
                    self.facing = "right"
                elif dx < 0:
                    self.facing = "left"

        self._update_animation(dt)
        self._update_scale()

    def _update_animation(self, dt):
        if self.moving:
            anim_name = f"walk_{self.facing}"
        else:
            anim_name = f"idle_{self.facing}"

        if anim_name != self.current_anim:
            self.current_anim = anim_name
            self.anim_index = 0
            self.anim_timer = 0.0

        anim_frames = self.frames.get(self.current_anim, [])
        if len(anim_frames) > 1:
            self.anim_timer += dt
            if self.anim_timer >= 1.0 / ANIM_FPS:
                self.anim_timer -= 1.0 / ANIM_FPS
                self.anim_index = (self.anim_index + 1) % len(anim_frames)

    def _update_scale(self):
        range_y = self.ground_y - self.horizon_y
        if range_y <= 0:
            self.scale = self.max_scale
        else:
            t = max(0.0, min(1.0, (self.y - self.horizon_y) / range_y))
            self.scale = self.min_scale + (self.max_scale - self.min_scale) * t

    def get_current_frame(self):
        anim_frames = self.frames.get(self.current_anim, [])
        if not anim_frames:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            pygame.draw.rect(s, (0, 0, 255), (0, 0, 16, 16))
            return s
        frame = anim_frames[self.anim_index % len(anim_frames)]
        if abs(self.scale - 1.0) > 0.01:
            new_w = max(1, int(frame.get_width() * self.scale))
            new_h = max(1, int(frame.get_height() * self.scale))
            frame = pygame.transform.scale(frame, (new_w, new_h))
        return frame

    def get_draw_pos(self):
        frame = self.get_current_frame()
        return (int(self.x - frame.get_width() // 2),
                int(self.y - frame.get_height()))

    def get_head_pos(self):
        frame = self.get_current_frame()
        return (int(self.x), int(self.y - frame.get_height() - 5))

    @property
    def foot_pos(self):
        return (self.x, self.y)


class CompanionCharacter(Character):
    """Auto-following companion character (pet, sidekick, etc.)."""

    def __init__(self, companion_config=None):
        config = companion_config or {}
        data = {
            "id": config.get("id", "companion"),
            "name": config.get("name", "Companion"),
            "x": config.get("x", 340),
            "y": config.get("y", 550),
            "speed": int(WALK_SPEED * config.get("speed_mult", COMPANION_FOLLOW_SPEED_MULT)),
        }
        frames = PlaceholderSprites.load_companion_walk_frames()
        if frames is None:
            frames = PlaceholderSprites.create_companion_frames()
        super().__init__(data, frames)
        self.follow_target = None  # The player
        self.follow_distance = config.get("follow_distance", COMPANION_FOLLOW_DISTANCE)
        self.idle_timer = 0.0

    def set_follow_target(self, player):
        self.follow_target = player

    def update(self, dt, walkable_area=None):
        if self.follow_target and not self.moving:
            tx, ty = self.follow_target.x, self.follow_target.y
            dx = tx - self.x
            dy = ty - self.y
            dist = math.sqrt(dx * dx + dy * dy)

            if dist > self.follow_distance:
                # Calculate target position behind the player
                if dist > 0:
                    behind_x = tx - (dx / dist) * self.follow_distance * 0.7
                    behind_y = ty - (dy / dist) * self.follow_distance * 0.3
                else:
                    behind_x, behind_y = self.x, self.y

                if walkable_area:
                    target = walkable_area.find_nearest_walkable((behind_x, behind_y))
                    path = walkable_area.get_path((self.x, self.y), target)
                else:
                    path = [(behind_x, behind_y)]
                self.walk_to(path)

        super().update(dt)

    def _update_animation(self, dt):
        # Keep walk animation going while the player is moving,
        # even during brief pauses when companion has caught up
        if self.moving or (self.follow_target and self.follow_target.moving):
            anim_name = f"walk_{self.facing}"
        else:
            anim_name = f"idle_{self.facing}"

        if anim_name != self.current_anim:
            self.current_anim = anim_name
            self.anim_index = 0
            self.anim_timer = 0.0

        anim_frames = self.frames.get(self.current_anim, [])
        if len(anim_frames) > 1:
            self.anim_timer += dt
            if self.anim_timer >= 1.0 / ANIM_FPS:
                self.anim_timer -= 1.0 / ANIM_FPS
                self.anim_index = (self.anim_index + 1) % len(anim_frames)


class CharacterRegistry:
    """Manages all NPCs."""

    def __init__(self):
        self.characters = {}
        self.companion = CompanionCharacter()

    def load_from_data(self, char_data):
        for cdata in char_data.get("characters", []):
            # Check if this is the companion character
            if cdata.get("is_companion"):
                self.companion = CompanionCharacter(companion_config=cdata)
                continue
            # Try loading a standing sprite for this character
            frames = None
            sprite_dir = cdata.get("sprite", f"sprites/{cdata['id']}_standing")
            frames = PlaceholderSprites.load_standing_frames(sprite_dir)
            char = Character(cdata, frames=frames)
            self.characters[char.id] = char

    def get(self, char_id):
        if char_id == self.companion.id:
            return self.companion
        return self.characters.get(char_id)

    def get_characters_in_scene(self, scene_id):
        """Get all NPCs in a given scene."""
        result = []
        for char in self.characters.values():
            if char.scene_id == scene_id:
                result.append(char)
        return result
