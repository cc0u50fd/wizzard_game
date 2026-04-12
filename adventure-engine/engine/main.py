"""GameEngine - main loop and orchestrator."""
import sys
import pygame
from engine.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE,
    COLOR_BLACK, COLOR_WHITE, INVENTORY_HEIGHT,
)
from engine.player import Player
from engine.camera import Camera
from engine.scene import Scene
from engine.interaction import InteractionManager
from engine.speech_bubble import SpeechManager
from engine.transitions import TransitionManager
from engine.inventory import Inventory
from engine.item import ItemRegistry
from engine.sound import SoundManager
from engine.state import GameState
from engine.scripting import ScriptRunner
from engine.dialogue import DialogueManager
from engine.character import CharacterRegistry
from engine.data_loader import DataLoader


class GameEngine:
    """Main game engine - owns all subsystems and runs the game loop."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.debug_mode = False

        # Game state: "playing", "dialogue", "cutscene", "paused"
        self.game_state = "playing"

        # Load all data
        self.data_loader = DataLoader()
        self.data_loader.load_all()

        # Core systems
        self.state = GameState()
        self.camera = Camera()
        self.player = Player()
        self.transitions = TransitionManager()
        self.speech = SpeechManager()
        self.sound = SoundManager()

        # Item and character registries
        self.item_registry = ItemRegistry()
        self.item_registry.load_from_data(self.data_loader.items_data)

        self.characters = CharacterRegistry()
        self.characters.load_from_data(self.data_loader.characters_data)
        self.characters.companion.set_follow_target(self.player)

        # Systems that reference engine
        self.inventory = Inventory(self.item_registry)
        self.script_runner = ScriptRunner(self)
        self.dialogue = DialogueManager(self)
        self.interaction = InteractionManager(self)

        # Scene
        self.current_scene = None
        self.scene_npcs = []

        # Load starting scene
        self._load_initial_scene()

        # Restore inventory from state
        for item_id in self.state.inventory_items:
            self.inventory.add_item(item_id)

        # HUD font
        self.hud_font = pygame.font.Font(None, 18)

    def _load_initial_scene(self):
        scene_id = self.state.current_scene
        scene_data = self.data_loader.get_scene_data(scene_id)
        if scene_data:
            self.current_scene = Scene(scene_data)
            self._apply_scene(self.current_scene, "default")
        else:
            # Create a minimal default scene
            self.current_scene = Scene({
                "id": "default",
                "name": "Default Scene",
                "bounds": [SCREEN_WIDTH, SCREEN_HEIGHT],
            })
            self._apply_scene(self.current_scene, "default")

    def _apply_scene(self, scene, entry_point_name):
        """Configure all systems for a new scene."""
        # Set camera bounds
        self.camera.set_scene_bounds(scene.bounds[0], scene.bounds[1])

        # Set player depth config
        dc = scene.depth_config
        self.player.set_depth_config(
            dc["horizon_y"], dc["ground_y"], dc["min_scale"], dc["max_scale"]
        )

        # Place player at entry point
        entry = scene.get_entry_point(entry_point_name)
        self.player.set_position(entry[0], entry[1])

        # Snap camera to player
        self.camera.set_position(self.player.x, self.player.y)

        # Place companion near player
        self.characters.companion.set_position(
            self.player.x - 50, self.player.y + 5
        )
        self.characters.companion.set_depth_config(
            dc["horizon_y"], dc["ground_y"], dc["min_scale"], dc["max_scale"]
        )

        # Load NPCs for this scene
        self.scene_npcs = self.characters.get_characters_in_scene(scene.id)
        for npc in self.scene_npcs:
            npc.set_depth_config(
                dc["horizon_y"], dc["ground_y"], dc["min_scale"], dc["max_scale"]
            )

        # Update state
        self.state.current_scene = scene.id
        self.state.mark_visited(scene.id)

        # Play music
        if scene.music:
            self.sound.play_music(scene.music)

        # Run on_enter scripts
        if scene.on_enter:
            self.script_runner.run(scene.on_enter)

    def change_scene(self, scene_id, entry_point="default", callback=None):
        """Transition to a new scene with fade effect."""
        def on_midpoint():
            # Run on_exit script for current scene
            if self.current_scene and self.current_scene.on_exit:
                self.script_runner.run(self.current_scene.on_exit)

            # Load new scene
            # Clear speech from previous scene before loading new one
            self.speech.clear()

            scene_data = self.data_loader.get_scene_data(scene_id)
            if scene_data:
                self.current_scene = Scene(scene_data)
                self._apply_scene(self.current_scene, entry_point)
            else:
                print(f"Warning: Scene '{scene_id}' not found")

        def on_complete():
            if callback:
                callback()

        self.transitions.start_transition(
            on_midpoint=on_midpoint,
            on_complete=on_complete
        )

    def run(self):
        """Main game loop."""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            dt = min(dt, 0.05)  # Cap delta time to prevent spiral

            self._process_events()
            self._update(dt)
            self._draw()

        pygame.quit()
        sys.exit()

    def _process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.inventory.visible:
                        self.inventory.hide()
                    elif self.dialogue.active:
                        pass  # Can't escape dialogue
                    else:
                        self.running = False
                elif event.key == pygame.K_F1:
                    self.debug_mode = not self.debug_mode
                elif event.key == pygame.K_i:
                    self.inventory.toggle()
                elif event.key == pygame.K_F5:
                    self.state.player_pos = (self.player.x, self.player.y)
                    self.state.save(1)
                    print("Game saved to slot 1")
                elif event.key == pygame.K_F9:
                    if self.state.load(1):
                        self._load_save_state()
                        print("Game loaded from slot 1")

            # Route events based on game state
            if self.transitions.is_active:
                continue  # Don't process input during transitions

            if self.dialogue.active:
                self.dialogue.handle_event(event)
            elif self.speech.is_active:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.speech.handle_click()
            elif self.script_runner.is_running and self.script_runner.waiting:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.speech.handle_click()
            else:
                self.interaction.handle_event(event)

    def _update(self, dt):
        # Update transitions
        self.transitions.update(dt)

        # Update scripts
        self.script_runner.update(dt)

        # Update player
        self.player.update(dt)

        # Update companion
        walkable = self.current_scene.walkable_area if self.current_scene else None
        self.characters.companion.update(dt, walkable)

        # Update NPCs
        for npc in self.scene_npcs:
            npc.update(dt)

        # Update speech
        self.speech.update(dt)

        # Update dialogue
        self.dialogue.update(dt)

        # Update camera (follow player)
        self.camera.update(self.player.x, self.player.y, dt)

        # Update inventory
        self.inventory.update(dt)

        # Check edge exits while player is walking
        if self.current_scene and self.player.moving:
            for exit_ in self.current_scene.exits:
                if exit_.is_edge_exit() and exit_.rect.collidepoint(self.player.x, self.player.y):
                    # Check conditions
                    if exit_.conditions and not self.state.check_condition(exit_.conditions):
                        continue
                    self.player.stop()
                    self.change_scene(exit_.target_scene, exit_.target_entry)
                    break

        # Update state position
        self.state.player_pos = (self.player.x, self.player.y)

    def _draw(self):
        self.screen.fill(COLOR_BLACK)

        if self.current_scene:
            cam = self.camera.offset

            # Draw background
            self.current_scene.draw_background(self.screen, cam)

            # Y-sort all entities (player, companion, NPCs) and draw in order
            entities = []
            entities.append(("player", self.player.y, self.player))
            entities.append(("companion", self.characters.companion.y, self.characters.companion))
            for npc in self.scene_npcs:
                entities.append(("npc", npc.y, npc))

            entities.sort(key=lambda e: e[1])

            for etype, _, entity in entities:
                frame = entity.get_current_frame()
                draw_pos = entity.get_draw_pos()
                screen_pos = (draw_pos[0] - cam[0], draw_pos[1] - cam[1])
                self.screen.blit(frame, screen_pos)

            # Debug overlays
            if self.debug_mode:
                self.current_scene.draw_debug_walkable(self.screen, cam)
                self._draw_debug_bounds(cam)
                # Player foot marker
                px, py = self.camera.apply(int(self.player.x), int(self.player.y))
                pygame.draw.circle(self.screen, (255, 0, 0), (px, py), 3)

        # Draw speech bubbles (screen space, but need camera offset for positioning)
        self.speech.draw(self.screen, self.camera.offset)

        # Draw dialogue UI
        self.dialogue.draw(self.screen)

        # Draw interaction overlays (radial menu)
        self.interaction.draw(self.screen)

        # Draw inventory bar
        self.inventory.draw(self.screen)

        # Draw transition overlay (last, on top of everything)
        self.transitions.draw(self.screen)

        # Debug HUD
        if self.debug_mode:
            self._draw_debug_hud()

        pygame.display.flip()

    def _draw_debug_bounds(self, cam):
        """Draw thin red boxes around all interactive assets."""
        red = (255, 0, 0)
        scene = self.current_scene

        # Characters (player, companion, NPCs)
        for entity in [self.player, self.characters.companion] + self.scene_npcs:
            frame = entity.get_current_frame()
            dx, dy = entity.get_draw_pos()
            r = pygame.Rect(dx - cam[0], dy - cam[1], frame.get_width(), frame.get_height())
            pygame.draw.rect(self.screen, red, r, 1)

        # Hotspots
        for hs in scene.hotspots:
            if hs.enabled:
                r = hs.rect.move(-cam[0], -cam[1])
                pygame.draw.rect(self.screen, red, r, 1)
                label = self.hud_font.render(hs.name, True, red)
                self.screen.blit(label, (r.x, r.y - 12))

        # Exits
        for ex in scene.exits:
            r = ex.rect.move(-cam[0], -cam[1])
            pygame.draw.rect(self.screen, red, r, 1)
            label = self.hud_font.render(f"-> {ex.target_scene}", True, red)
            self.screen.blit(label, (r.x, r.y - 12))

        # Entry points
        for name, pos in scene.entry_points.items():
            sx = int(pos[0] - cam[0])
            sy = int(pos[1] - cam[1])
            r = pygame.Rect(sx - 6, sy - 6, 12, 12)
            pygame.draw.rect(self.screen, red, r, 1)
            pygame.draw.line(self.screen, red, (sx - 6, sy), (sx + 5, sy), 1)
            pygame.draw.line(self.screen, red, (sx, sy - 6), (sx, sy + 5), 1)
            label = self.hud_font.render(name, True, red)
            self.screen.blit(label, (sx + 8, sy - 6))

    def _draw_debug_hud(self):
        fps = int(self.clock.get_fps())
        # Mouse position in world coordinates
        mx, my = pygame.mouse.get_pos()
        cam = self.camera.offset
        world_mx = mx + cam[0]
        world_my = my + cam[1]

        # Mouse coords at top of screen
        mouse_text = f"Mouse: ({int(world_mx)}, {int(world_my)})  Screen: ({mx}, {my})"
        mouse_surf = self.hud_font.render(mouse_text, True, COLOR_WHITE)
        mouse_bg = pygame.Surface((mouse_surf.get_width() + 4, mouse_surf.get_height()), pygame.SRCALPHA)
        mouse_bg.fill((0, 0, 0, 150))
        self.screen.blit(mouse_bg, (4, 4))
        self.screen.blit(mouse_surf, (6, 4))

        info = [
            f"FPS: {fps}",
            f"Scene: {self.current_scene.id if self.current_scene else 'None'}",
            f"Player: ({int(self.player.x)}, {int(self.player.y)}) scale={self.player.scale:.2f}",
            f"Camera: ({int(self.camera.x)}, {int(self.camera.y)})",
            f"State: {self.game_state}",
            f"Flags: {len(self.state.flags)}",
        ]
        y = SCREEN_HEIGHT - len(info) * 16 - 5
        for line in info:
            surf = self.hud_font.render(line, True, COLOR_WHITE)
            bg = pygame.Surface((surf.get_width() + 4, surf.get_height()), pygame.SRCALPHA)
            bg.fill((0, 0, 0, 150))
            self.screen.blit(bg, (4, y))
            self.screen.blit(surf, (6, y))
            y += 16

    def _load_save_state(self):
        """Apply loaded state to all systems."""
        # Reload scene
        scene_data = self.data_loader.get_scene_data(self.state.current_scene)
        if scene_data:
            self.current_scene = Scene(scene_data)
            dc = self.current_scene.depth_config
            self.player.set_depth_config(
                dc["horizon_y"], dc["ground_y"], dc["min_scale"], dc["max_scale"]
            )
            self.camera.set_scene_bounds(
                self.current_scene.bounds[0], self.current_scene.bounds[1]
            )

        # Restore player position
        self.player.set_position(*self.state.player_pos)
        self.camera.set_position(self.player.x, self.player.y)

        # Restore inventory
        self.inventory.items = list(self.state.inventory_items)

        # Reload NPCs
        self.scene_npcs = self.characters.get_characters_in_scene(self.state.current_scene)
