"""Script runner: executes JSON action sequences (the heart of the engine)."""
from engine.settings import PLAYER_ID


class ScriptRunner:
    """Executes action lists from JSON data. Bridges data and engine behavior."""

    def __init__(self, engine):
        self.engine = engine
        self.action_queue = []
        self.running = False
        self.waiting = False
        self._on_complete = None

    def run(self, actions, callback=None):
        """Execute a list of action dicts sequentially."""
        if not actions:
            if callback:
                callback()
            return

        self.action_queue = list(actions)
        self.running = True
        self.waiting = False
        self._on_complete = callback
        self._execute_next()

    def _execute_next(self):
        if not self.action_queue:
            self.running = False
            self.waiting = False
            if self._on_complete:
                cb = self._on_complete
                self._on_complete = None
                cb()
            return

        action = self.action_queue.pop(0)
        action_type = action.get("type", "")

        handler = self._get_handler(action_type)
        if handler:
            handler(action)
        else:
            # Unknown action, skip
            self._execute_next()

    def _get_handler(self, action_type):
        handlers = {
            "say": self._action_say,
            "walk_to": self._action_walk_to,
            "face": self._action_face,
            "wait": self._action_wait,
            "set_flag": self._action_set_flag,
            "give_item": self._action_give_item,
            "remove_item": self._action_remove_item,
            "play_sfx": self._action_play_sfx,
            "enable_hotspot": self._action_enable_hotspot,
            "disable_hotspot": self._action_disable_hotspot,
            "check_flag": self._action_check_flag,
            "change_scene": self._action_change_scene,
            "start_dialogue": self._action_start_dialogue,
            "fade_in": self._action_fade_in,
            "fade_out": self._action_fade_out,
        }
        return handlers.get(action_type)

    # --- Blocking actions (wait for completion before continuing) ---

    def _action_say(self, action):
        speaker = action.get("speaker", PLAYER_ID)
        text = action.get("text", "...")
        style = action.get("style", "normal")

        # Get speaker head position
        if speaker == PLAYER_ID:
            pos = self.engine.player.get_head_pos()
        else:
            char = self.engine.characters.get(speaker)
            if char:
                pos = char.get_head_pos()
            else:
                pos = (640, 300)

        self.waiting = True
        self.engine.speech.say(text, pos, style=style, callback=self._on_blocking_done)

    def _action_walk_to(self, action):
        target = action.get("target")
        who = action.get("who", PLAYER_ID)

        if not target:
            self._execute_next()
            return

        self.waiting = True

        if who == PLAYER_ID:
            scene = self.engine.current_scene
            if scene:
                path = scene.walkable_area.get_path(
                    (self.engine.player.x, self.engine.player.y), tuple(target)
                )
                self.engine.player.walk_to(path, callback=self._on_blocking_done)
            else:
                self._on_blocking_done()
        else:
            char = self.engine.characters.get(who)
            if char and self.engine.current_scene:
                path = self.engine.current_scene.walkable_area.get_path(
                    (char.x, char.y), tuple(target)
                )
                char.walk_to(path, callback=self._on_blocking_done)
            else:
                self._on_blocking_done()

    def _action_face(self, action):
        direction = action.get("direction", "right")
        who = action.get("who", PLAYER_ID)

        if who == PLAYER_ID:
            self.engine.player.face(direction)
        else:
            char = self.engine.characters.get(who)
            if char:
                char.face(direction)

        self._execute_next()

    def _action_wait(self, action):
        duration = action.get("duration", 1.0)
        self.waiting = True
        self._wait_timer = duration
        # Wait is handled in update()

    def _action_change_scene(self, action):
        scene_id = action.get("scene_id")
        entry = action.get("entry", "default")
        if scene_id:
            self.waiting = True
            self.engine.change_scene(scene_id, entry, callback=self._on_blocking_done)
        else:
            self._execute_next()

    def _action_start_dialogue(self, action):
        dialogue_id = action.get("dialogue_id")
        start_node = action.get("start_node", "start")
        if dialogue_id:
            self.engine.dialogue.start_dialogue(dialogue_id, start_node)
        self._execute_next()

    def _action_fade_in(self, action):
        duration = action.get("duration", 0.5)
        self.waiting = True
        self.engine.transitions.fade_in(on_complete=self._on_blocking_done, duration=duration)

    def _action_fade_out(self, action):
        duration = action.get("duration", 0.5)
        self.waiting = True
        self.engine.transitions.fade_out(on_complete=self._on_blocking_done, duration=duration)

    # --- Immediate actions (execute and continue immediately) ---

    def _action_set_flag(self, action):
        flag = action.get("flag")
        value = action.get("value", True)
        if flag:
            self.engine.state.set_flag(flag, value)
        self._execute_next()

    def _action_give_item(self, action):
        item_id = action.get("item_id")
        if item_id:
            self.engine.state.add_item(item_id)
            self.engine.inventory.add_item(item_id)
            self.engine.inventory.show()
        self._execute_next()

    def _action_remove_item(self, action):
        item_id = action.get("item_id")
        if item_id:
            self.engine.state.remove_item(item_id)
            self.engine.inventory.remove_item(item_id)
        self._execute_next()

    def _action_play_sfx(self, action):
        sfx = action.get("sfx")
        if sfx:
            self.engine.sound.play_sfx(sfx)
        self._execute_next()

    def _action_enable_hotspot(self, action):
        hotspot_id = action.get("hotspot_id")
        if hotspot_id and self.engine.current_scene:
            hs = self.engine.current_scene.get_hotspot_by_id(hotspot_id)
            if hs:
                hs.enabled = True
        self._execute_next()

    def _action_disable_hotspot(self, action):
        hotspot_id = action.get("hotspot_id")
        if hotspot_id and self.engine.current_scene:
            hs = self.engine.current_scene.get_hotspot_by_id(hotspot_id)
            if hs:
                hs.enabled = False
        self._execute_next()

    def _action_check_flag(self, action):
        condition = action.get("condition", {})
        then_actions = action.get("then", [])
        else_actions = action.get("else", [])

        if self.engine.state.check_condition(condition):
            if then_actions:
                # Prepend then actions to queue
                self.action_queue = then_actions + self.action_queue
        else:
            if else_actions:
                self.action_queue = else_actions + self.action_queue

        self._execute_next()

    def _on_blocking_done(self):
        self.waiting = False
        self._execute_next()

    def update(self, dt):
        # Handle wait timer
        if self.waiting and hasattr(self, "_wait_timer"):
            self._wait_timer -= dt
            if self._wait_timer <= 0:
                del self._wait_timer
                self._on_blocking_done()

    @property
    def is_running(self):
        return self.running
