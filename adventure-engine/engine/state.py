"""Game state: flags, save/load, condition checking."""
import json
import os
from engine.settings import SAVES_DIR, DATA_DIR


class GameState:
    """Tracks all story state through flags and provides save/load."""

    def __init__(self):
        self.flags = {}
        self.current_scene = "example_scene"
        self.player_pos = (200, 600)
        self.inventory_items = []
        self.visited_scenes = set()
        self.dialogue_states = {}  # dialogue_id -> last visited node
        self._load_initial_flags()

    def _load_initial_flags(self):
        flags_path = os.path.join(DATA_DIR, "story_flags.json")
        if os.path.exists(flags_path):
            with open(flags_path, "r") as f:
                data = json.load(f)
            self.flags = data.get("initial_flags", {})
            self.current_scene = data.get("starting_scene", "example_scene")

    def get_flag(self, key, default=None):
        return self.flags.get(key, default)

    def set_flag(self, key, value):
        self.flags[key] = value

    def has_item(self, item_id):
        return item_id in self.inventory_items

    def add_item(self, item_id):
        if item_id not in self.inventory_items:
            self.inventory_items.append(item_id)

    def remove_item(self, item_id):
        if item_id in self.inventory_items:
            self.inventory_items.remove(item_id)

    def mark_visited(self, scene_id):
        self.visited_scenes.add(scene_id)

    def has_visited(self, scene_id):
        return scene_id in self.visited_scenes

    def check_condition(self, condition):
        """Evaluate a condition dict. Returns True/False.

        Supports:
        - {"flag": "key", "equals": value}
        - {"flag": "key", "gte": value}
        - {"flag": "key", "lt": value}
        - {"has_item": "item_id"}
        - {"visited": "scene_id"}
        - {"and": [condition, ...]}
        - {"or": [condition, ...]}
        - {"not": condition}
        """
        if condition is None:
            return True

        if "and" in condition:
            return all(self.check_condition(c) for c in condition["and"])
        if "or" in condition:
            return any(self.check_condition(c) for c in condition["or"])
        if "not" in condition:
            return not self.check_condition(condition["not"])

        if "flag" in condition:
            val = self.flags.get(condition["flag"])
            if "equals" in condition:
                return val == condition["equals"]
            if "gte" in condition:
                return val is not None and val >= condition["gte"]
            if "lt" in condition:
                return val is not None and val < condition["lt"]
            # Just check if flag is truthy
            return bool(val)

        if "has_item" in condition:
            return self.has_item(condition["has_item"])

        if "visited" in condition:
            return self.has_visited(condition["visited"])

        return True

    def save(self, slot=1):
        os.makedirs(SAVES_DIR, exist_ok=True)
        save_data = {
            "flags": self.flags,
            "current_scene": self.current_scene,
            "player_pos": list(self.player_pos),
            "inventory_items": self.inventory_items,
            "visited_scenes": list(self.visited_scenes),
            "dialogue_states": self.dialogue_states,
        }
        path = os.path.join(SAVES_DIR, f"save_{slot}.json")
        with open(path, "w") as f:
            json.dump(save_data, f, indent=2)

    def load(self, slot=1):
        path = os.path.join(SAVES_DIR, f"save_{slot}.json")
        if not os.path.exists(path):
            return False
        with open(path, "r") as f:
            data = json.load(f)
        self.flags = data.get("flags", {})
        self.current_scene = data.get("current_scene", "example_scene")
        self.player_pos = tuple(data.get("player_pos", [200, 600]))
        self.inventory_items = data.get("inventory_items", [])
        self.visited_scenes = set(data.get("visited_scenes", []))
        self.dialogue_states = data.get("dialogue_states", {})
        return True
