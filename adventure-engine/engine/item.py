"""Item definitions and management."""
import os
import pygame
from engine.settings import ASSETS_DIR, INVENTORY_SLOT_SIZE


class Item:
    """Represents an inventory item."""

    def __init__(self, data):
        self.id = data["id"]
        self.name = data.get("name", self.id)
        self.examine_text = data.get("examine_text", f"It's a {self.name}.")
        self.combinable_with = data.get("combinable_with", {})
        self.use_on = data.get("use_on", {})

        # Load or create icon
        self.icon = None
        icon_path = data.get("icon")
        if icon_path:
            full_path = os.path.join(ASSETS_DIR, icon_path)
            if os.path.exists(full_path):
                self.icon = pygame.image.load(full_path).convert_alpha()
                self.icon = pygame.transform.scale(
                    self.icon, (INVENTORY_SLOT_SIZE - 8, INVENTORY_SLOT_SIZE - 8)
                )

        if self.icon is None:
            self._create_placeholder_icon()

    def _create_placeholder_icon(self):
        size = INVENTORY_SLOT_SIZE - 8
        self.icon = pygame.Surface((size, size), pygame.SRCALPHA)
        # Simple colored square with first letter
        pygame.draw.rect(self.icon, (180, 140, 80), (0, 0, size, size), border_radius=4)
        pygame.draw.rect(self.icon, (120, 90, 40), (0, 0, size, size), 2, border_radius=4)
        font = pygame.font.Font(None, 28)
        letter = font.render(self.name[0].upper(), True, (255, 255, 255))
        lx = (size - letter.get_width()) // 2
        ly = (size - letter.get_height()) // 2
        self.icon.blit(letter, (lx, ly))


class ItemRegistry:
    """Loads and stores all item definitions."""

    def __init__(self):
        self.items = {}

    def load_from_data(self, items_data):
        for item_data in items_data.get("items", []):
            item = Item(item_data)
            self.items[item.id] = item

    def get(self, item_id):
        return self.items.get(item_id)
