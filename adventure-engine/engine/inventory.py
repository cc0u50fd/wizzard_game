"""Inventory model and slide-down UI bar."""
import pygame
from engine.settings import (
    SCREEN_WIDTH, INVENTORY_HEIGHT, INVENTORY_SLOT_SIZE,
    INVENTORY_SLIDE_SPEED,
    COLOR_INVENTORY_BG, COLOR_INVENTORY_SLOT, COLOR_INVENTORY_HIGHLIGHT,
    COLOR_WHITE,
)


class Inventory:
    """Player inventory with slide-down UI."""

    def __init__(self, item_registry):
        self.item_registry = item_registry
        self.items = []  # List of item_id strings
        self.selected_item = None  # item_id of selected item for use-on

        # UI state
        self.visible = False
        self.slide_y = -INVENTORY_HEIGHT  # Current y position (negative = hidden)
        self.hover_slot = -1

        # Build surfaces
        self.bar_surface = pygame.Surface((SCREEN_WIDTH, INVENTORY_HEIGHT), pygame.SRCALPHA)
        self.font = pygame.font.Font(None, 16)

    def add_item(self, item_id):
        if item_id not in self.items:
            self.items.append(item_id)

    def remove_item(self, item_id):
        if item_id in self.items:
            self.items.remove(item_id)
        if self.selected_item == item_id:
            self.selected_item = None

    def has_item(self, item_id):
        return item_id in self.items

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False
        self.selected_item = None

    def toggle(self):
        if self.visible:
            self.hide()
        else:
            self.show()

    def select_item(self, item_id):
        if item_id in self.items:
            self.selected_item = item_id if self.selected_item != item_id else None

    def update(self, dt):
        target_y = 0 if self.visible else -INVENTORY_HEIGHT
        if self.slide_y < target_y:
            self.slide_y = min(target_y, self.slide_y + INVENTORY_SLIDE_SPEED * dt)
        elif self.slide_y > target_y:
            self.slide_y = max(target_y, self.slide_y - INVENTORY_SLIDE_SPEED * dt)

    def handle_click(self, screen_pos):
        """Handle a click on the inventory bar. Returns True if click was consumed."""
        x, y = screen_pos
        bar_y = int(self.slide_y)

        if y < bar_y or y > bar_y + INVENTORY_HEIGHT:
            return False

        # Which slot was clicked?
        slot_idx = self._get_slot_at(x, y - bar_y)
        if slot_idx >= 0 and slot_idx < len(self.items):
            item_id = self.items[slot_idx]
            self.select_item(item_id)
            return True

        return y <= bar_y + INVENTORY_HEIGHT

    def handle_right_click(self, screen_pos):
        """Handle right-click for item examine. Returns (True, examine_text) or (False, None)."""
        x, y = screen_pos
        bar_y = int(self.slide_y)

        if y < bar_y or y > bar_y + INVENTORY_HEIGHT:
            return False, None

        slot_idx = self._get_slot_at(x, y - bar_y)
        if slot_idx >= 0 and slot_idx < len(self.items):
            item = self.item_registry.get(self.items[slot_idx])
            if item:
                return True, item.examine_text
        return False, None

    def handle_mouse_move(self, screen_pos):
        x, y = screen_pos
        bar_y = int(self.slide_y)
        self.hover_slot = self._get_slot_at(x, y - bar_y)

    def _get_slot_at(self, x, local_y):
        if local_y < 0 or local_y > INVENTORY_HEIGHT:
            return -1
        slot_total_w = INVENTORY_SLOT_SIZE + 4
        start_x = (SCREEN_WIDTH - len(self.items) * slot_total_w) // 2
        rel_x = x - start_x
        if rel_x < 0:
            return -1
        idx = int(rel_x // slot_total_w)
        # Check within slot bounds
        if rel_x % slot_total_w < INVENTORY_SLOT_SIZE:
            return idx
        return -1

    def try_combine(self, item_a_id, item_b_id):
        """Try combining two items. Returns script actions or None."""
        item_a = self.item_registry.get(item_a_id)
        if item_a and item_b_id in item_a.combinable_with:
            return item_a.combinable_with[item_b_id]
        item_b = self.item_registry.get(item_b_id)
        if item_b and item_a_id in item_b.combinable_with:
            return item_b.combinable_with[item_a_id]
        return None

    def draw(self, surface):
        bar_y = int(self.slide_y)
        if bar_y <= -INVENTORY_HEIGHT:
            return

        # Draw bar background
        self.bar_surface.fill(COLOR_INVENTORY_BG)

        # Draw slots
        slot_total_w = INVENTORY_SLOT_SIZE + 4
        start_x = (SCREEN_WIDTH - len(self.items) * slot_total_w) // 2

        for i, item_id in enumerate(self.items):
            slot_x = start_x + i * slot_total_w
            slot_y = (INVENTORY_HEIGHT - INVENTORY_SLOT_SIZE) // 2

            # Slot background
            color = COLOR_INVENTORY_HIGHLIGHT if (
                item_id == self.selected_item or i == self.hover_slot
            ) else COLOR_INVENTORY_SLOT
            pygame.draw.rect(self.bar_surface, color,
                             (slot_x, slot_y, INVENTORY_SLOT_SIZE, INVENTORY_SLOT_SIZE),
                             border_radius=4)

            # Item icon
            item = self.item_registry.get(item_id)
            if item and item.icon:
                icon_x = slot_x + 4
                icon_y = slot_y + 4
                self.bar_surface.blit(item.icon, (icon_x, icon_y))

        surface.blit(self.bar_surface, (0, bar_y))

        # Draw tooltip for hovered item
        if 0 <= self.hover_slot < len(self.items):
            item = self.item_registry.get(self.items[self.hover_slot])
            if item:
                tooltip = self.font.render(item.name, True, COLOR_WHITE)
                tx = start_x + self.hover_slot * slot_total_w
                ty = bar_y + INVENTORY_HEIGHT + 4
                bg = pygame.Surface((tooltip.get_width() + 8, tooltip.get_height() + 4), pygame.SRCALPHA)
                bg.fill((0, 0, 0, 180))
                surface.blit(bg, (tx, ty))
                surface.blit(tooltip, (tx + 4, ty + 2))
