"""Music and sound effects manager."""
import os
import pygame
from engine.settings import ASSETS_DIR, MUSIC_VOLUME, SFX_VOLUME, MUSIC_FADEOUT_MS


class SoundManager:
    """Manages background music and sound effects."""

    def __init__(self):
        self.music_enabled = True
        self.sfx_enabled = True
        self.current_music = None
        self.sfx_cache = {}

        try:
            pygame.mixer.init()
            self.initialized = True
        except (pygame.error, NotImplementedError):
            self.initialized = False

    def play_music(self, music_path, loops=-1, fade_ms=None):
        """Play background music, crossfading if something is already playing."""
        if not self.initialized or not self.music_enabled:
            return
        if not music_path:
            self.stop_music()
            return

        full_path = os.path.join(ASSETS_DIR, music_path)
        if not os.path.exists(full_path):
            return

        if self.current_music == full_path:
            return  # Already playing

        fade = fade_ms or MUSIC_FADEOUT_MS
        if self.current_music:
            pygame.mixer.music.fadeout(fade)

        try:
            pygame.mixer.music.load(full_path)
            pygame.mixer.music.set_volume(MUSIC_VOLUME)
            pygame.mixer.music.play(loops, fade_ms=fade)
            self.current_music = full_path
        except pygame.error:
            self.current_music = None

    def stop_music(self, fade_ms=None):
        if not self.initialized:
            return
        fade = fade_ms or MUSIC_FADEOUT_MS
        pygame.mixer.music.fadeout(fade)
        self.current_music = None

    def play_sfx(self, sfx_path, volume=None):
        """Play a sound effect."""
        if not self.initialized or not self.sfx_enabled:
            return

        full_path = os.path.join(ASSETS_DIR, sfx_path)
        if not os.path.exists(full_path):
            return

        if full_path not in self.sfx_cache:
            try:
                self.sfx_cache[full_path] = pygame.mixer.Sound(full_path)
            except pygame.error:
                return

        sound = self.sfx_cache[full_path]
        sound.set_volume(volume if volume is not None else SFX_VOLUME)
        sound.play()

    def set_music_volume(self, volume):
        if self.initialized:
            pygame.mixer.music.set_volume(volume)

    def toggle_music(self):
        self.music_enabled = not self.music_enabled
        if not self.music_enabled:
            self.stop_music()

    def toggle_sfx(self):
        self.sfx_enabled = not self.sfx_enabled
