"""Dialogue tree traversal and choice UI."""
import json
import os
import pygame
from engine.settings import (
    DATA_DIR, SCREEN_WIDTH, SCREEN_HEIGHT, PLAYER_ID,
    COLOR_DIALOGUE_BG, COLOR_DIALOGUE_CHOICE, COLOR_DIALOGUE_HOVER,
    COLOR_WHITE,
)


class DialogueTree:
    """A dialogue tree loaded from JSON."""

    def __init__(self, data):
        self.id = data["id"]
        self.nodes = data.get("nodes", {})

    def get_node(self, node_id):
        return self.nodes.get(node_id)


class DialogueManager:
    """Manages dialogue tree traversal and UI."""

    def __init__(self, engine):
        self.engine = engine
        self.active = False
        self.current_tree = None
        self.current_node_id = None
        self.current_node = None

        # Choice UI
        self.choices = []
        self.choice_rects = []
        self.hover_choice = -1
        self.waiting_for_speech = False

        self.font = pygame.font.Font(None, 24)
        self.choice_font = pygame.font.Font(None, 22)

        # Cache loaded dialogues
        self.dialogue_cache = {}

    def start_dialogue(self, dialogue_id, start_node="start"):
        """Begin a dialogue tree."""
        tree = self._load_dialogue(dialogue_id)
        if not tree:
            return

        self.active = True
        self.current_tree = tree
        self._process_node(start_node)

    def _load_dialogue(self, dialogue_id):
        if dialogue_id in self.dialogue_cache:
            return self.dialogue_cache[dialogue_id]

        path = os.path.join(DATA_DIR, "dialogues", f"{dialogue_id}.json")
        if not os.path.exists(path):
            return None

        with open(path, "r") as f:
            data = json.load(f)

        tree = DialogueTree(data)
        self.dialogue_cache[dialogue_id] = tree
        return tree

    def _process_node(self, node_id):
        if not node_id or not self.current_tree:
            self._end_dialogue()
            return

        node = self.current_tree.get_node(node_id)
        if not node:
            self._end_dialogue()
            return

        self.current_node_id = node_id
        self.current_node = node
        node_type = node.get("type", "end")

        if node_type == "say":
            self._handle_say(node)
        elif node_type == "player_say":
            self._handle_player_say(node)
        elif node_type == "choice":
            self._handle_choice(node)
        elif node_type == "conditional":
            self._handle_conditional(node)
        elif node_type == "action":
            self._handle_action(node)
        elif node_type == "end":
            self._end_dialogue()

    def _handle_say(self, node):
        speaker_id = node.get("speaker", "unknown")
        text = node.get("text", "...")
        style = node.get("style", "normal")

        # Find speaker position
        speaker_pos = self._get_speaker_pos(speaker_id)

        self.waiting_for_speech = True
        self.engine.speech.say(
            text, speaker_pos, style=style,
            callback=lambda: self._on_speech_done(node.get("next"))
        )

    def _handle_player_say(self, node):
        text = node.get("text", "...")
        style = node.get("style", "normal")
        speaker_pos = self.engine.player.get_head_pos()

        self.waiting_for_speech = True
        self.engine.speech.say(
            text, speaker_pos, style=style,
            callback=lambda: self._on_speech_done(node.get("next"))
        )

    def _handle_choice(self, node):
        self.choices = []
        self.choice_rects = []
        self.waiting_for_speech = False

        for choice in node.get("choices", []):
            # Check conditions
            condition = choice.get("condition")
            if condition and not self.engine.state.check_condition(condition):
                continue
            self.choices.append(choice)

        if not self.choices:
            # No valid choices, go to default or end
            self._process_node(node.get("default", None))

    def _handle_conditional(self, node):
        for branch in node.get("branches", []):
            condition = branch.get("condition")
            if self.engine.state.check_condition(condition):
                self._process_node(branch.get("next"))
                return
        # No branch matched, use default
        self._process_node(node.get("default"))

    def _handle_action(self, node):
        actions = node.get("actions", [])
        next_node = node.get("next")

        if actions:
            self.engine.script_runner.run(actions, callback=lambda: self._process_node(next_node))
        else:
            self._process_node(next_node)

    def _on_speech_done(self, next_node_id):
        self.waiting_for_speech = False
        self._process_node(next_node_id)

    def _end_dialogue(self):
        self.active = False
        self.current_tree = None
        self.current_node = None
        self.choices = []
        self.choice_rects = []

    def _get_speaker_pos(self, speaker_id):
        if speaker_id == PLAYER_ID:
            return self.engine.player.get_head_pos()
        char = self.engine.characters.get(speaker_id)
        if char:
            return char.get_head_pos()
        # Default position
        return (SCREEN_WIDTH // 2, 200)

    def handle_event(self, event):
        """Handle input during dialogue mode."""
        if not self.active:
            return False

        if event.type == pygame.MOUSEMOTION:
            if self.choices:
                self._update_choice_hover(event.pos)
            return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # If speech is playing, advance it
            if self.waiting_for_speech:
                self.engine.speech.handle_click()
                return True

            # If choices are showing, select one
            if self.choices:
                idx = self._get_choice_at(event.pos)
                if 0 <= idx < len(self.choices):
                    choice = self.choices[idx]
                    self.choices = []
                    self.choice_rects = []
                    self._process_node(choice.get("next"))
                    return True

            return True

        return True  # Consume all events during dialogue

    def _update_choice_hover(self, pos):
        self.hover_choice = self._get_choice_at(pos)

    def _get_choice_at(self, pos):
        for i, rect in enumerate(self.choice_rects):
            if rect.collidepoint(pos):
                return i
        return -1

    def update(self, dt):
        pass

    def draw(self, surface):
        if not self.active:
            return

        if self.choices:
            self._draw_choices(surface)

    def _draw_choices(self, surface):
        # Semi-transparent background at bottom
        overlay = pygame.Surface((SCREEN_WIDTH, 200), pygame.SRCALPHA)
        overlay.fill(COLOR_DIALOGUE_BG)
        y_start = SCREEN_HEIGHT - 200
        surface.blit(overlay, (0, y_start))

        # Draw choice items
        self.choice_rects = []
        y = y_start + 20

        for i, choice in enumerate(self.choices):
            text = choice.get("text", "...")
            is_hover = (i == self.hover_choice)
            color = COLOR_DIALOGUE_HOVER if is_hover else COLOR_DIALOGUE_CHOICE

            prefix = "> " if is_hover else "  "
            rendered = self.choice_font.render(prefix + text, True, color)
            rect = pygame.Rect(40, y, rendered.get_width() + 20, rendered.get_height() + 8)
            self.choice_rects.append(rect)
            surface.blit(rendered, (50, y + 4))
            y += rendered.get_height() + 14
