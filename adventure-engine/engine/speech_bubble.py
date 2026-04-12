"""Comic-style speech bubbles with typewriter effect."""
import os
import math
import pygame
from engine.settings import (
    ASSETS_DIR, SCREEN_WIDTH, SCREEN_HEIGHT,
    SPEECH_FONT_SIZE, SPEECH_SHOUT_FONT_SIZE,
    SPEECH_TYPEWRITER_SPEED, SPEECH_PADDING, SPEECH_MAX_WIDTH,
    SPEECH_POINTER_SIZE, FONT_NORMAL, FONT_SHOUT,
    COLOR_SPEECH_BG, COLOR_SPEECH_BORDER, COLOR_BLACK, COLOR_WHITE,
)


class SpeechBubble:
    """A single speech bubble with typewriter text reveal."""

    def __init__(self, text, speaker_pos, style="normal", font=None, shout_font=None):
        self.full_text = text
        self.speaker_pos = speaker_pos  # (x, y) world position of speaker's head
        self.style = style  # "normal", "shout", "thought", "whisper"

        # Choose font based on style
        if style == "shout" and shout_font:
            self.font = shout_font
        elif font:
            self.font = font
        else:
            self.font = pygame.font.Font(None, SPEECH_FONT_SIZE)

        # Typewriter state
        self.chars_revealed = 0
        self.char_timer = 0.0
        self.speed = SPEECH_TYPEWRITER_SPEED
        self.finished_typing = False
        self.dismissed = False

        # Pre-render word-wrapped text to figure out bubble size
        self.lines = self._wrap_text(text, SPEECH_MAX_WIDTH - SPEECH_PADDING * 2)
        line_height = self.font.get_linesize()
        text_width = max(self.font.size(line)[0] for line in self.lines) if self.lines else 50
        text_height = line_height * len(self.lines)

        self.bubble_width = text_width + SPEECH_PADDING * 2
        self.bubble_height = text_height + SPEECH_PADDING * 2

    def _wrap_text(self, text, max_width):
        words = text.split(" ")
        lines = []
        current = ""
        for word in words:
            test = (current + " " + word).strip()
            if self.font.size(test)[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines or [""]

    def update(self, dt):
        if self.dismissed:
            return
        if not self.finished_typing:
            self.char_timer += dt * self.speed
            total_chars = sum(len(line) for line in self.lines)
            self.chars_revealed = min(int(self.char_timer), total_chars)
            if self.chars_revealed >= total_chars:
                self.finished_typing = True
                self.chars_revealed = total_chars

    def skip_typing(self):
        if not self.finished_typing:
            self.finished_typing = True
            self.chars_revealed = sum(len(line) for line in self.lines)
        else:
            self.dismissed = True

    def dismiss(self):
        self.dismissed = True

    def draw(self, surface, camera_offset=(0, 0)):
        if self.dismissed:
            return

        # Calculate bubble position (above speaker, centered)
        sx = self.speaker_pos[0] - camera_offset[0]
        sy = self.speaker_pos[1] - camera_offset[1]

        bx = sx - self.bubble_width // 2
        by = sy - self.bubble_height - SPEECH_POINTER_SIZE - 10

        # Keep on screen
        bx = max(5, min(SCREEN_WIDTH - self.bubble_width - 5, bx))
        by = max(5, by)

        bubble_rect = pygame.Rect(bx, by, self.bubble_width, self.bubble_height)

        # Draw bubble background
        if self.style == "thought":
            self._draw_thought_bubble(surface, bubble_rect, sx, sy)
        elif self.style == "shout":
            self._draw_shout_bubble(surface, bubble_rect, sx, sy)
        elif self.style == "whisper":
            self._draw_whisper_bubble(surface, bubble_rect, sx, sy)
        else:
            self._draw_normal_bubble(surface, bubble_rect, sx, sy)

        # Draw text with typewriter effect
        self._draw_text(surface, bubble_rect)

    def _draw_normal_bubble(self, surface, rect, sx, sy):
        # Rounded rectangle
        radius = 8
        pygame.draw.rect(surface, COLOR_SPEECH_BG, rect, border_radius=radius)
        pygame.draw.rect(surface, COLOR_SPEECH_BORDER, rect, 2, border_radius=radius)

        # Pointer triangle
        pointer_x = max(rect.left + 15, min(rect.right - 15, sx))
        points = [
            (pointer_x - 6, rect.bottom),
            (pointer_x + 6, rect.bottom),
            (sx, sy - 5),
        ]
        pygame.draw.polygon(surface, COLOR_SPEECH_BG, points)
        pygame.draw.line(surface, COLOR_SPEECH_BORDER, points[0], points[2], 2)
        pygame.draw.line(surface, COLOR_SPEECH_BORDER, points[1], points[2], 2)

    def _draw_shout_bubble(self, surface, rect, sx, sy):
        # Spiky border
        cx, cy = rect.centerx, rect.centery
        hw, hh = rect.width // 2 + 8, rect.height // 2 + 8
        points = []
        spikes = 16
        for i in range(spikes):
            angle = (2 * math.pi * i) / spikes
            r = hw if i % 2 == 0 else hw - 10
            ry = hh if i % 2 == 0 else hh - 8
            px = cx + int(r * math.cos(angle))
            py = cy + int(ry * math.sin(angle))
            points.append((px, py))

        pygame.draw.polygon(surface, COLOR_SPEECH_BG, points)
        pygame.draw.polygon(surface, COLOR_SPEECH_BORDER, points, 2)

        # Pointer
        pointer_x = max(rect.left + 15, min(rect.right - 15, sx))
        tri = [
            (pointer_x - 8, rect.bottom + 4),
            (pointer_x + 8, rect.bottom + 4),
            (sx, sy - 5),
        ]
        pygame.draw.polygon(surface, COLOR_SPEECH_BG, tri)
        pygame.draw.line(surface, COLOR_SPEECH_BORDER, tri[0], tri[2], 2)
        pygame.draw.line(surface, COLOR_SPEECH_BORDER, tri[1], tri[2], 2)

    def _draw_thought_bubble(self, surface, rect, sx, sy):
        # Cloud-like with ellipses
        radius = 10
        pygame.draw.rect(surface, COLOR_SPEECH_BG, rect, border_radius=radius)
        pygame.draw.rect(surface, COLOR_SPEECH_BORDER, rect, 2, border_radius=radius)

        # Thought circles instead of pointer
        cx = max(rect.left + 15, min(rect.right - 15, sx))
        dy = rect.bottom
        for i, r in enumerate([6, 4, 3]):
            t = (i + 1) / 4
            py = dy + int(t * (sy - dy))
            px = cx + int(t * (sx - cx))
            pygame.draw.circle(surface, COLOR_SPEECH_BG, (px, py), r)
            pygame.draw.circle(surface, COLOR_SPEECH_BORDER, (px, py), r, 1)

    def _draw_whisper_bubble(self, surface, rect, sx, sy):
        # Dashed border
        pygame.draw.rect(surface, COLOR_SPEECH_BG, rect, border_radius=6)
        # Draw dashed rect
        for i in range(0, rect.width, 8):
            if (i // 8) % 2 == 0:
                pygame.draw.line(surface, COLOR_SPEECH_BORDER,
                                 (rect.left + i, rect.top),
                                 (rect.left + min(i + 4, rect.width), rect.top), 1)
                pygame.draw.line(surface, COLOR_SPEECH_BORDER,
                                 (rect.left + i, rect.bottom),
                                 (rect.left + min(i + 4, rect.width), rect.bottom), 1)
        for i in range(0, rect.height, 8):
            if (i // 8) % 2 == 0:
                pygame.draw.line(surface, COLOR_SPEECH_BORDER,
                                 (rect.left, rect.top + i),
                                 (rect.left, rect.top + min(i + 4, rect.height)), 1)
                pygame.draw.line(surface, COLOR_SPEECH_BORDER,
                                 (rect.right, rect.top + i),
                                 (rect.right, rect.top + min(i + 4, rect.height)), 1)

        # Pointer
        pointer_x = max(rect.left + 15, min(rect.right - 15, sx))
        points = [
            (pointer_x - 4, rect.bottom),
            (pointer_x + 4, rect.bottom),
            (sx, sy - 5),
        ]
        pygame.draw.polygon(surface, COLOR_SPEECH_BG, points)
        pygame.draw.line(surface, COLOR_SPEECH_BORDER, points[0], points[2], 1)
        pygame.draw.line(surface, COLOR_SPEECH_BORDER, points[1], points[2], 1)

    def _draw_text(self, surface, rect):
        line_height = self.font.get_linesize()
        chars_left = self.chars_revealed
        y = rect.top + SPEECH_PADDING

        for line in self.lines:
            if chars_left <= 0:
                break
            visible = line[:chars_left]
            chars_left -= len(line)

            text_color = COLOR_BLACK
            rendered = self.font.render(visible, True, text_color)
            surface.blit(rendered, (rect.left + SPEECH_PADDING, y))
            y += line_height


class SpeechManager:
    """Manages a queue of speech bubbles."""

    def __init__(self):
        self.current_bubble = None
        self.queue = []
        self.font = None
        self.shout_font = None
        self._load_fonts()

    def _load_fonts(self):
        font_path = os.path.join(ASSETS_DIR, "fonts", FONT_NORMAL)
        shout_path = os.path.join(ASSETS_DIR, "fonts", FONT_SHOUT)

        if os.path.exists(font_path):
            self.font = pygame.font.Font(font_path, SPEECH_FONT_SIZE)
        else:
            self.font = pygame.font.Font(None, SPEECH_FONT_SIZE)

        if os.path.exists(shout_path):
            self.shout_font = pygame.font.Font(shout_path, SPEECH_SHOUT_FONT_SIZE)
        else:
            self.shout_font = self.font

    def say(self, text, speaker_pos, style="normal", callback=None):
        """Queue a speech bubble. callback fires when dismissed."""
        bubble_data = {
            "text": text,
            "speaker_pos": speaker_pos,
            "style": style,
            "callback": callback,
        }
        if self.current_bubble is None:
            self._create_bubble(bubble_data)
        else:
            self.queue.append(bubble_data)

    def _create_bubble(self, data):
        self.current_bubble = SpeechBubble(
            data["text"], data["speaker_pos"], data["style"],
            self.font, self.shout_font
        )
        self._current_callback = data.get("callback")

    def handle_click(self):
        """Handle a click to advance/dismiss speech."""
        if self.current_bubble:
            self.current_bubble.skip_typing()
            if self.current_bubble.dismissed:
                callback = self._current_callback
                self._current_callback = None
                self.current_bubble = None
                # Show next queued bubble
                if self.queue:
                    self._create_bubble(self.queue.pop(0))
                if callback:
                    callback()
                return True
            return True
        return False

    def update(self, dt):
        if self.current_bubble:
            self.current_bubble.update(dt)

    def draw(self, surface, camera_offset=(0, 0)):
        if self.current_bubble:
            self.current_bubble.draw(surface, camera_offset)

    @property
    def is_active(self):
        return self.current_bubble is not None

    def clear(self):
        self.current_bubble = None
        self.queue.clear()
        self._current_callback = None
