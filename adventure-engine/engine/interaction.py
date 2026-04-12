"""Interaction system: cursor management, radial menu, input dispatch."""
import math
import time
import pygame
from engine.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    RADIAL_RADIUS, RADIAL_ICON_SIZE, DOUBLE_CLICK_TIME,
    COLOR_MENU_BG, COLOR_MENU_TEXT, COLOR_MENU_HIGHLIGHT, COLOR_WHITE,
    INVENTORY_HEIGHT,
)


class CursorManager:
    """Changes cursor appearance based on context."""

    def __init__(self):
        self.current = "default"
        self.cursors = {}
        self._create_cursors()

    def _create_cursors(self):
        # Default arrow
        self.cursors["default"] = pygame.SYSTEM_CURSOR_ARROW
        self.cursors["hand"] = pygame.SYSTEM_CURSOR_HAND
        self.cursors["crosshair"] = pygame.SYSTEM_CURSOR_CROSSHAIR

    def set(self, cursor_name):
        if cursor_name != self.current and cursor_name in self.cursors:
            self.current = cursor_name
            pygame.mouse.set_cursor(self.cursors[cursor_name])

    def reset(self):
        self.set("default")


class RadialMenu:
    """Right-click popup menu showing available actions for a hotspot."""

    def __init__(self):
        self.visible = False
        self.position = (0, 0)
        self.items = []  # List of {"label": str, "action": str}
        self.hotspot = None
        self.hover_index = -1
        self.font = pygame.font.Font(None, 20)

        # Action labels/icons
        self.action_labels = {
            "look": "Look at",
            "use": "Use",
            "pickup": "Pick up",
            "talk": "Talk to",
        }

    def show(self, screen_pos, hotspot):
        """Show the radial menu for a hotspot."""
        self.visible = True
        self.position = screen_pos
        self.hotspot = hotspot
        self.hover_index = -1

        # Build menu items from hotspot's available actions
        self.items = []
        for action_key in hotspot.get_available_actions():
            label = self.action_labels.get(action_key, action_key.replace("_", " ").title())
            self.items.append({"label": label, "action": action_key})

    def hide(self):
        self.visible = False
        self.items = []
        self.hotspot = None
        self.hover_index = -1

    def handle_mouse_move(self, pos):
        if not self.visible:
            return
        self.hover_index = self._get_item_at(pos)

    def handle_click(self, pos):
        """Handle click on menu. Returns (hotspot, action_key) or None."""
        if not self.visible:
            return None

        idx = self._get_item_at(pos)
        if 0 <= idx < len(self.items):
            result = (self.hotspot, self.items[idx]["action"])
            self.hide()
            return result

        # Clicked outside menu
        self.hide()
        return None

    def _get_item_at(self, pos):
        if not self.items:
            return -1

        n = len(self.items)
        for i in range(n):
            angle = (2 * math.pi * i) / n - math.pi / 2
            ix = self.position[0] + int(RADIAL_RADIUS * math.cos(angle))
            iy = self.position[1] + int(RADIAL_RADIUS * math.sin(angle))

            label = self.items[i]["label"]
            text_surf = self.font.render(label, True, COLOR_WHITE)
            tw, th = text_surf.get_width() + 16, text_surf.get_height() + 8
            rect = pygame.Rect(ix - tw // 2, iy - th // 2, tw, th)

            if rect.collidepoint(pos):
                return i
        return -1

    def draw(self, surface):
        if not self.visible or not self.items:
            return

        n = len(self.items)
        for i in range(n):
            angle = (2 * math.pi * i) / n - math.pi / 2
            ix = self.position[0] + int(RADIAL_RADIUS * math.cos(angle))
            iy = self.position[1] + int(RADIAL_RADIUS * math.sin(angle))

            label = self.items[i]["label"]
            is_hover = (i == self.hover_index)

            text_color = COLOR_MENU_HIGHLIGHT if is_hover else COLOR_MENU_TEXT
            text_surf = self.font.render(label, True, text_color)
            tw, th = text_surf.get_width() + 16, text_surf.get_height() + 8

            # Background pill
            bg = pygame.Surface((tw, th), pygame.SRCALPHA)
            bg.fill(COLOR_MENU_BG)
            pygame.draw.rect(bg, (80, 65, 50), (0, 0, tw, th), 1, border_radius=4)

            bx = ix - tw // 2
            by = iy - th // 2
            surface.blit(bg, (bx, by))
            surface.blit(text_surf, (bx + 8, by + 4))

        # Hotspot name in center
        if self.hotspot:
            name_surf = self.font.render(self.hotspot.name, True, COLOR_WHITE)
            nx = self.position[0] - name_surf.get_width() // 2
            ny = self.position[1] - name_surf.get_height() // 2
            surface.blit(name_surf, (nx, ny))


class InteractionManager:
    """Central input dispatcher during gameplay."""

    def __init__(self, engine):
        self.engine = engine
        self.cursor = CursorManager()
        self.radial_menu = RadialMenu()
        self.last_click_time = 0
        self.last_click_pos = (0, 0)

    def handle_event(self, event):
        """Process input events. Returns True if event was consumed."""
        if event.type == pygame.MOUSEMOTION:
            return self._handle_mouse_move(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                return self._handle_left_click(event.pos)
            elif event.button == 3:
                return self._handle_right_click(event.pos)

        return False

    def _handle_mouse_move(self, pos):
        # Update radial menu hover
        if self.radial_menu.visible:
            self.radial_menu.handle_mouse_move(pos)
            return True

        # Update cursor based on what's under it
        world_pos = self.engine.camera.screen_to_world(pos[0], pos[1])
        scene = self.engine.current_scene
        if scene:
            hotspot = scene.get_hotspot_at(world_pos)
            exit_ = scene.get_exit_at(world_pos)
            if hotspot:
                self.cursor.set("hand")
            elif exit_:
                self.cursor.set("crosshair")
            else:
                self.cursor.reset()

        # Update inventory hover
        self.engine.inventory.handle_mouse_move(pos)

        return False

    def _handle_left_click(self, pos):
        # Check radial menu first
        if self.radial_menu.visible:
            result = self.radial_menu.handle_click(pos)
            if result:
                hotspot, action_key = result
                self._execute_hotspot_action(hotspot, action_key)
            return True

        # Check inventory
        if self.engine.inventory.handle_click(pos):
            return True

        # Check if click is in inventory trigger zone (top of screen)
        if pos[1] < 10:
            self.engine.inventory.show()
            return True

        # Convert to world coords
        world_pos = self.engine.camera.screen_to_world(pos[0], pos[1])
        scene = self.engine.current_scene
        if not scene:
            return False

        # Detect double-click
        now = time.time()
        is_double = (now - self.last_click_time < DOUBLE_CLICK_TIME and
                     abs(pos[0] - self.last_click_pos[0]) < 10 and
                     abs(pos[1] - self.last_click_pos[1]) < 10)
        self.last_click_time = now
        self.last_click_pos = pos

        # Check exits
        exit_ = scene.get_exit_at(world_pos)
        if exit_:
            self._trigger_exit(exit_)
            return True

        # Check hotspots (left click = walk to + default action)
        hotspot = scene.get_hotspot_at(world_pos)
        if hotspot:
            # If player has selected inventory item, try use-on
            if self.engine.inventory.selected_item:
                self._use_item_on_hotspot(self.engine.inventory.selected_item, hotspot)
                return True
            # Otherwise walk to hotspot
            walk_to = hotspot.walk_to
            path = scene.walkable_area.get_path(
                (self.engine.player.x, self.engine.player.y), walk_to
            )
            self.engine.player.walk_to(path, running=is_double)
            return True

        # Click on walkable area = move
        if scene.walkable_area.contains_point(world_pos):
            path = scene.walkable_area.get_path(
                (self.engine.player.x, self.engine.player.y), world_pos
            )
            self.engine.player.walk_to(path, running=is_double)
        else:
            # Find nearest walkable point
            nearest = scene.walkable_area.find_nearest_walkable(world_pos)
            path = scene.walkable_area.get_path(
                (self.engine.player.x, self.engine.player.y), nearest
            )
            self.engine.player.walk_to(path, running=is_double)

        return True

    def _handle_right_click(self, pos):
        # Check inventory right-click (examine)
        consumed, text = self.engine.inventory.handle_right_click(pos)
        if consumed and text:
            head_pos = self.engine.player.get_head_pos()
            self.engine.speech.say(text, head_pos)
            return True

        # Hide radial menu if visible
        if self.radial_menu.visible:
            self.radial_menu.hide()
            return True

        world_pos = self.engine.camera.screen_to_world(pos[0], pos[1])
        scene = self.engine.current_scene
        if not scene:
            return False

        # Right-click on hotspot = show radial menu
        hotspot = scene.get_hotspot_at(world_pos)
        if hotspot and hotspot.get_available_actions():
            self.radial_menu.show(pos, hotspot)
            return True

        return False

    def _execute_hotspot_action(self, hotspot, action_key):
        """Walk to hotspot then run the action's script."""
        actions = hotspot.actions.get(action_key, [])
        if not actions:
            return

        walk_to = hotspot.walk_to

        def on_arrive():
            # Face the hotspot
            self.engine.player.face(hotspot.look_at_dir)
            # Run the script
            self.engine.script_runner.run(actions)

        path = self.engine.current_scene.walkable_area.get_path(
            (self.engine.player.x, self.engine.player.y), walk_to
        )
        self.engine.player.walk_to(path, callback=on_arrive)

    def _trigger_exit(self, exit_):
        """Walk to exit then change scene."""
        walk_to = exit_.walk_to
        if walk_to:
            target = tuple(walk_to)
        elif exit_.is_edge_exit():
            # Walk toward the edge
            target = (exit_.rect.centerx, exit_.rect.centery)
        else:
            target = (exit_.rect.centerx, exit_.rect.centery)

        def on_arrive():
            self.engine.change_scene(exit_.target_scene, exit_.target_entry)

        scene = self.engine.current_scene
        if scene:
            nearest = scene.walkable_area.find_nearest_walkable(target)
            path = scene.walkable_area.get_path(
                (self.engine.player.x, self.engine.player.y), nearest
            )
            self.engine.player.walk_to(path, callback=on_arrive)
        else:
            on_arrive()

    def _use_item_on_hotspot(self, item_id, hotspot):
        """Use selected inventory item on a hotspot."""
        item = self.engine.item_registry.get(item_id)
        if not item:
            return

        # Check if item has a use_on script for this hotspot
        use_scripts = item.use_on.get(hotspot.id)
        if use_scripts:
            def on_arrive():
                self.engine.player.face(hotspot.look_at_dir)
                self.engine.inventory.selected_item = None
                self.engine.script_runner.run(use_scripts)

            path = self.engine.current_scene.walkable_area.get_path(
                (self.engine.player.x, self.engine.player.y), hotspot.walk_to
            )
            self.engine.player.walk_to(path, callback=on_arrive)
        else:
            # Default "can't use that" response
            head_pos = self.engine.player.get_head_pos()
            self.engine.speech.say("I can't use that here.", head_pos)
            self.engine.inventory.selected_item = None

    def update(self, dt):
        pass

    def draw(self, surface):
        self.radial_menu.draw(surface)
