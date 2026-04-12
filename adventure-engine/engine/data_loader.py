"""Loads and validates all JSON data files."""
import json
import os
from engine.settings import DATA_DIR


class DataLoader:
    """Loads game data from JSON files."""

    def __init__(self):
        self.scenes = {}
        self.items_data = {"items": []}
        self.characters_data = {"characters": []}
        self.story_flags_data = {}
        self.puzzles_data = {}

    def load_all(self):
        """Load all game data files."""
        self._load_scenes()
        self._load_items()
        self._load_characters()
        self._load_story_flags()
        self._load_puzzles()

    def _load_scenes(self):
        scenes_dir = os.path.join(DATA_DIR, "scenes")
        if not os.path.exists(scenes_dir):
            return
        for filename in os.listdir(scenes_dir):
            if filename.endswith(".json"):
                path = os.path.join(scenes_dir, filename)
                with open(path, "r") as f:
                    data = json.load(f)
                scene_id = data.get("id", filename.replace(".json", ""))
                self.scenes[scene_id] = data

    def _load_items(self):
        path = os.path.join(DATA_DIR, "items.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                self.items_data = json.load(f)

    def _load_characters(self):
        path = os.path.join(DATA_DIR, "characters.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                self.characters_data = json.load(f)

    def _load_story_flags(self):
        path = os.path.join(DATA_DIR, "story_flags.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                self.story_flags_data = json.load(f)

    def _load_puzzles(self):
        path = os.path.join(DATA_DIR, "puzzles.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                self.puzzles_data = json.load(f)

    def get_scene_data(self, scene_id):
        return self.scenes.get(scene_id)
