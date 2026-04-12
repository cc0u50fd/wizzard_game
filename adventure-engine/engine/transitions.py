"""Screen transitions between scenes."""
import pygame
from engine.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FADE_DURATION, COLOR_BLACK


class TransitionManager:
    """Manages fade-in and fade-out transitions."""

    def __init__(self):
        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.overlay.fill(COLOR_BLACK)
        self.alpha = 0
        self.active = False
        self.fading_in = False
        self.fading_out = False
        self.duration = FADE_DURATION
        self.timer = 0.0
        self.on_midpoint = None  # Callback when fade-out completes
        self.on_complete = None  # Callback when entire transition completes

    def start_transition(self, on_midpoint=None, on_complete=None, duration=None):
        """Start a fade-out -> callback -> fade-in transition."""
        self.active = True
        self.fading_out = True
        self.fading_in = False
        self.timer = 0.0
        self.alpha = 0
        self.duration = duration or FADE_DURATION
        self.on_midpoint = on_midpoint
        self.on_complete = on_complete

    def fade_in(self, on_complete=None, duration=None):
        """Just fade in from black."""
        self.active = True
        self.fading_in = True
        self.fading_out = False
        self.timer = 0.0
        self.alpha = 255
        self.duration = duration or FADE_DURATION
        self.on_midpoint = None
        self.on_complete = on_complete

    def fade_out(self, on_complete=None, duration=None):
        """Just fade out to black."""
        self.active = True
        self.fading_out = True
        self.fading_in = False
        self.timer = 0.0
        self.alpha = 0
        self.duration = duration or FADE_DURATION
        self.on_midpoint = None
        self.on_complete = on_complete

    def update(self, dt):
        if not self.active:
            return

        self.timer += dt

        if self.fading_out:
            progress = min(1.0, self.timer / self.duration)
            self.alpha = int(255 * progress)

            if progress >= 1.0:
                self.alpha = 255
                self.fading_out = False

                if self.on_midpoint:
                    callback = self.on_midpoint
                    self.on_midpoint = None
                    callback()
                    # Start fade-in
                    self.fading_in = True
                    self.timer = 0.0
                else:
                    # Just a fade-out with no midpoint
                    self.active = False
                    if self.on_complete:
                        self.on_complete()
                        self.on_complete = None

        elif self.fading_in:
            progress = min(1.0, self.timer / self.duration)
            self.alpha = int(255 * (1.0 - progress))

            if progress >= 1.0:
                self.alpha = 0
                self.fading_in = False
                self.active = False
                if self.on_complete:
                    self.on_complete()
                    self.on_complete = None

    def draw(self, surface):
        if self.active and self.alpha > 0:
            self.overlay.set_alpha(self.alpha)
            surface.blit(self.overlay, (0, 0))

    @property
    def is_active(self):
        return self.active
