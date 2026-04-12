"""Sprite sheet loader and placeholder sprite generator."""
import json
import os
import math
import pygame
from engine.settings import ASSETS_DIR, COLORKEY_MAGENTA, PLAYER_SPRITE_SCALE, COMPANION_SPRITE_SCALE, PLACEHOLDER_SCALE


def remove_magenta(surf):
    """Replace magenta and near-magenta fringe pixels with transparency."""
    surf = surf.convert_alpha()
    pixels = pygame.PixelArray(surf)
    for x in range(surf.get_width()):
        for y in range(surf.get_height()):
            r, g, b, a = surf.get_at((x, y))
            if r > 180 and b > 180 and g < 80:
                pixels[x, y] = (0, 0, 0, 0)
    pixels.close()
    return surf


class SpriteSheet:
    """Loads a sprite sheet image and extracts frames using a JSON frame map.

    Also supports placeholder mode for development without real sprite assets.
    """

    def __init__(self, image_path=None, frame_map_path=None, colorkey=None):
        self.sheet = None
        self.frames = {}  # name -> list of pygame.Surface
        self.colorkey = colorkey

        if image_path and os.path.exists(os.path.join(ASSETS_DIR, image_path)):
            full_path = os.path.join(ASSETS_DIR, image_path)
            self.sheet = pygame.image.load(full_path).convert()
            if self.colorkey:
                self.sheet.set_colorkey(self.colorkey)

        if frame_map_path:
            full_map = os.path.join(ASSETS_DIR, frame_map_path)
            if os.path.exists(full_map):
                self._load_frame_map(full_map)

    def _load_frame_map(self, path):
        with open(path, "r") as f:
            data = json.load(f)

        for anim_name, frame_list in data.get("animations", {}).items():
            surfaces = []
            for fr in frame_list:
                x, y, w, h = fr["x"], fr["y"], fr["w"], fr["h"]
                surf = pygame.Surface((w, h), pygame.SRCALPHA)
                surf.blit(self.sheet, (0, 0), (x, y, w, h))
                if self.colorkey:
                    surf.set_colorkey(self.colorkey)
                surfaces.append(surf)
            self.frames[anim_name] = surfaces

    def get_frames(self, animation_name):
        return self.frames.get(animation_name, [])


class PlaceholderSprites:
    """Generates simple placeholder character sprites for development."""

    @staticmethod
    def load_player_walk_frames():
        """Load real player walk sprites from assets/sprites/player_walk/.

        Returns dict mapping animation name -> list of pygame.Surface,
        or None if sprite files are not found.
        """
        sprites_dir = os.path.join(ASSETS_DIR, "sprites", "player_walk")
        if not os.path.isdir(sprites_dir):
            return None

        right_frames = []
        # Load numbered frames starting from 1
        i = 1
        while True:
            path = os.path.join(sprites_dir, f"{i}.png")
            if not os.path.exists(path):
                break
            img = pygame.image.load(path).convert_alpha()
            # Check if magenta removal is needed
            corner = img.get_at((0, 0))
            if corner.r > 180 and corner.b > 180 and corner.g < 80:
                img = remove_magenta(img)
            w = int(img.get_width() * PLAYER_SPRITE_SCALE)
            h = int(img.get_height() * PLAYER_SPRITE_SCALE)
            img = pygame.transform.smoothscale(img, (w, h))
            right_frames.append(img)
            i += 1

        if not right_frames:
            return None

        left_frames = [pygame.transform.flip(f, True, False) for f in right_frames]

        frames = {}
        frames["walk_right"] = right_frames
        frames["walk_left"] = left_frames
        frames["idle_right"] = [right_frames[0]]
        frames["idle_left"] = [left_frames[0]]
        frames["run_right"] = right_frames
        frames["run_left"] = left_frames
        return frames

    @staticmethod
    def load_companion_walk_frames():
        """Load real companion walk sprites from assets/sprites/companion_walk/.

        Returns dict mapping animation name -> list of pygame.Surface,
        or None if sprite files are not found.
        """
        sprites_dir = os.path.join(ASSETS_DIR, "sprites", "companion_walk")
        if not os.path.isdir(sprites_dir):
            return None

        right_frames = []
        i = 1
        while True:
            path = os.path.join(sprites_dir, f"{i}.png")
            if not os.path.exists(path):
                break
            img = pygame.image.load(path).convert_alpha()
            w = int(img.get_width() * COMPANION_SPRITE_SCALE)
            h = int(img.get_height() * COMPANION_SPRITE_SCALE)
            img = pygame.transform.smoothscale(img, (w, h))
            right_frames.append(img)
            i += 1

        if not right_frames:
            return None

        left_frames = [pygame.transform.flip(f, True, False) for f in right_frames]

        frames = {}
        frames["walk_right"] = right_frames
        frames["walk_left"] = left_frames
        frames["idle_right"] = [right_frames[0]]
        frames["idle_left"] = [left_frames[0]]
        return frames

    @staticmethod
    def load_standing_frames(sprite_dir, scale=0.63):
        """Load a single standing sprite from a directory and create idle/walk frames.

        Returns dict mapping animation name -> list of pygame.Surface,
        or None if sprite files are not found.
        """
        full_dir = os.path.join(ASSETS_DIR, sprite_dir)
        if not os.path.isdir(full_dir):
            return None

        path = os.path.join(full_dir, "1.png")
        if not os.path.exists(path):
            return None

        img = pygame.image.load(path).convert_alpha()
        # Check if magenta removal is needed
        corner = img.get_at((0, 0))
        if corner.r > 180 and corner.b > 180 and corner.g < 80:
            img = remove_magenta(img)

        w = int(img.get_width() * scale)
        h = int(img.get_height() * scale)
        img = pygame.transform.smoothscale(img, (w, h))

        flipped = pygame.transform.flip(img, True, False)

        frames = {
            "idle_right": [img],
            "idle_left": [flipped],
            "walk_right": [img],
            "walk_left": [flipped],
        }
        return frames

    @staticmethod
    def create_player_frames():
        """Create placeholder player character frames for all animation states.

        Returns dict mapping animation name -> list of pygame.Surface.
        """
        frames = {}
        # Character dimensions (scaled up for visibility)
        w, h = 32 * PLACEHOLDER_SCALE, 56 * PLACEHOLDER_SCALE

        def make_frame(leg_offset=0, arm_swing=0):
            s = PLACEHOLDER_SCALE
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            # Head (skin tone)
            pygame.draw.circle(surf, (255, 210, 170), (w // 2, 10 * s), 8 * s)
            # Hair
            pygame.draw.polygon(surf, (100, 60, 20), [
                (w // 2 - 2 * s, 2 * s), (w // 2 + 6 * s, 0), (w // 2 + 3 * s, 8 * s)
            ])
            # Eyes
            pygame.draw.circle(surf, (0, 0, 0), (w // 2 - 3 * s, 9 * s), max(1, 1 * s))
            pygame.draw.circle(surf, (0, 0, 0), (w // 2 + 3 * s, 9 * s), max(1, 1 * s))
            # Shirt (green)
            pygame.draw.rect(surf, (30, 130, 80), (w // 2 - 7 * s, 18 * s, 14 * s, 16 * s))
            # Arms
            arm_y = (20 + arm_swing) * s
            pygame.draw.rect(surf, (30, 130, 80), (w // 2 - 10 * s, arm_y, 4 * s, 10 * s))
            pygame.draw.rect(surf, (30, 130, 80), (w // 2 + 6 * s, arm_y - arm_swing * s, 4 * s, 10 * s))
            # Trousers (dark)
            leg_l_x = w // 2 - 6 * s - leg_offset * s
            leg_r_x = w // 2 + 1 * s + leg_offset * s
            pygame.draw.rect(surf, (60, 60, 80), (leg_l_x, 34 * s, 6 * s, 14 * s))
            pygame.draw.rect(surf, (60, 60, 80), (leg_r_x, 34 * s, 6 * s, 14 * s))
            # Shoes
            pygame.draw.rect(surf, (80, 40, 20), (leg_l_x - 1 * s, 48 * s, 8 * s, 4 * s))
            pygame.draw.rect(surf, (80, 40, 20), (leg_r_x - 1 * s, 48 * s, 8 * s, 4 * s))
            return surf

        # Idle frames (slight breathing motion)
        idle = [make_frame(0, 0), make_frame(0, 0)]
        frames["idle_right"] = idle
        frames["idle_left"] = [pygame.transform.flip(f, True, False) for f in idle]

        # Walk frames (4 frame cycle with leg movement)
        walk = [
            make_frame(0, 0),
            make_frame(2, 1),
            make_frame(0, 0),
            make_frame(-2, -1),
        ]
        frames["walk_right"] = walk
        frames["walk_left"] = [pygame.transform.flip(f, True, False) for f in walk]

        # Run frames (wider stride)
        run = [
            make_frame(0, 0),
            make_frame(3, 2),
            make_frame(0, 0),
            make_frame(-3, -2),
        ]
        frames["run_right"] = run
        frames["run_left"] = [pygame.transform.flip(f, True, False) for f in run]

        return frames

    @staticmethod
    def create_companion_frames():
        """Create placeholder companion character frames (small animal/sidekick)."""
        frames = {}
        s = PLACEHOLDER_SCALE
        w, h = 24 * s, 18 * s

        def make_frame(leg_offset=0):
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            # Body
            pygame.draw.ellipse(surf, (200, 180, 160), (4 * s, 4 * s, 16 * s, 10 * s))
            # Head
            pygame.draw.circle(surf, (200, 180, 160), (20 * s, 5 * s), 5 * s)
            # Eye
            pygame.draw.circle(surf, (0, 0, 0), (21 * s, 4 * s), max(1, 1 * s))
            # Nose
            pygame.draw.circle(surf, (0, 0, 0), (24 * s, 6 * s), max(1, 1 * s))
            # Ears
            pygame.draw.ellipse(surf, (180, 160, 140), (17 * s, 0, 4 * s, 4 * s))
            # Legs
            pygame.draw.rect(surf, (190, 170, 150), ((6 - leg_offset) * s, 13 * s, 3 * s, 5 * s))
            pygame.draw.rect(surf, (190, 170, 150), ((14 + leg_offset) * s, 13 * s, 3 * s, 5 * s))
            # Tail
            pygame.draw.line(surf, (200, 180, 160), (2 * s, 5 * s), (0, 2 * s), 2 * s)
            return surf

        idle = [make_frame(0)]
        frames["idle_right"] = idle
        frames["idle_left"] = [pygame.transform.flip(f, True, False) for f in idle]

        walk = [make_frame(0), make_frame(1), make_frame(0), make_frame(-1)]
        frames["walk_right"] = walk
        frames["walk_left"] = [pygame.transform.flip(f, True, False) for f in walk]

        return frames
