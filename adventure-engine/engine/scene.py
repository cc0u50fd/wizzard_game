"""Scene system - rooms, walkable areas, hotspots, exits."""
import os
import heapq
import pygame
from engine.settings import ASSETS_DIR, SCREEN_WIDTH, SCREEN_HEIGHT
from engine.pathfinding import point_in_polygon, find_path, find_nearest_point_in_polygon


class MaskWalkableArea:
    """Defines where the player can walk using a painted mask image."""

    GRID_STEP = 8  # Downsample factor for pathfinding grid

    def __init__(self, mask_surface, bounds):
        self.width, self.height = bounds
        self.polygons = []  # Compatibility — no polygons to draw

        # Build full-res boolean grid from mask pixels
        mw, mh = mask_surface.get_size()
        self.grid = [[False] * mh for _ in range(mw)]
        for x in range(mw):
            for y in range(mh):
                c = mask_surface.get_at((x, y))
                if c.r > 180 and c.g < 80 and c.b > 180 and c.a > 128:
                    self.grid[x][y] = True

        # Build downsampled grid for A* pathfinding
        step = self.GRID_STEP
        self.ds_w = (mw + step - 1) // step
        self.ds_h = (mh + step - 1) // step
        self.ds_grid = [[False] * self.ds_h for _ in range(self.ds_w)]
        for gx in range(self.ds_w):
            for gy in range(self.ds_h):
                # Cell is walkable if its center pixel is walkable
                cx = min(gx * step + step // 2, mw - 1)
                cy = min(gy * step + step // 2, mh - 1)
                self.ds_grid[gx][gy] = self.grid[cx][cy]

        # Cache a debug overlay surface (built lazily)
        self._debug_surface = None

    def contains_point(self, point):
        x, y = int(point[0]), int(point[1])
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[x][y]
        return False

    def find_nearest_walkable(self, point):
        if self.contains_point(point):
            return point
        # BFS on the downsampled grid to find nearest walkable cell
        step = self.GRID_STEP
        sx = max(0, min(int(point[0]) // step, self.ds_w - 1))
        sy = max(0, min(int(point[1]) // step, self.ds_h - 1))
        visited = set()
        queue = [(0, sx, sy)]
        visited.add((sx, sy))
        while queue:
            dist, cx, cy = heapq.heappop(queue)
            if self.ds_grid[cx][cy]:
                # Refine: find exact walkable pixel near this cell
                wx = cx * step + step // 2
                wy = cy * step + step // 2
                wx = max(0, min(wx, self.width - 1))
                wy = max(0, min(wy, self.height - 1))
                if self.grid[wx][wy]:
                    return (wx, wy)
                # Search nearby full-res pixels
                for dx in range(-step, step + 1):
                    for dy in range(-step, step + 1):
                        px, py = wx + dx, wy + dy
                        if 0 <= px < self.width and 0 <= py < self.height and self.grid[px][py]:
                            return (px, py)
                return (wx, wy)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.ds_w and 0 <= ny < self.ds_h and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    d = ((nx - sx) ** 2 + (ny - sy) ** 2) ** 0.5
                    heapq.heappush(queue, (d, nx, ny))
        return point

    def _line_of_sight(self, start, end):
        """Check if a straight line between two points is fully walkable."""
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        dist = max(abs(dx), abs(dy))
        steps = max(1, int(dist) // 4)
        for i in range(steps + 1):
            t = i / steps
            x = int(start[0] + dx * t)
            y = int(start[1] + dy * t)
            x = max(0, min(x, self.width - 1))
            y = max(0, min(y, self.height - 1))
            if not self.grid[x][y]:
                return False
        return True

    def get_path(self, start, end):
        """Find a path from start to end within the walkable mask."""
        # Direct line-of-sight check
        if self._line_of_sight(start, end):
            return [end]

        # A* on the downsampled grid
        step = self.GRID_STEP
        sx = max(0, min(int(start[0]) // step, self.ds_w - 1))
        sy = max(0, min(int(start[1]) // step, self.ds_h - 1))
        ex = max(0, min(int(end[0]) // step, self.ds_w - 1))
        ey = max(0, min(int(end[1]) // step, self.ds_h - 1))

        # Heuristic: Euclidean distance
        def heuristic(a, b):
            return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

        open_set = [(0, sx, sy)]
        came_from = {}
        g_score = {(sx, sy): 0}
        closed = set()

        while open_set:
            _, cx, cy = heapq.heappop(open_set)
            if (cx, cy) in closed:
                continue
            closed.add((cx, cy))

            if cx == ex and cy == ey:
                # Reconstruct path
                path_cells = []
                node = (ex, ey)
                while node in came_from:
                    path_cells.append(node)
                    node = came_from[node]
                path_cells.reverse()
                # Convert grid coords to world coords
                waypoints = [(c[0] * step + step // 2, c[1] * step + step // 2)
                             for c in path_cells]
                # Simplify: remove collinear/redundant waypoints using line-of-sight
                if len(waypoints) > 2:
                    simplified = [waypoints[0]]
                    i = 0
                    while i < len(waypoints) - 1:
                        # Find farthest point with line-of-sight from current
                        farthest = i + 1
                        for j in range(i + 2, len(waypoints)):
                            if self._line_of_sight(simplified[-1], waypoints[j]):
                                farthest = j
                        simplified.append(waypoints[farthest])
                        i = farthest
                    waypoints = simplified
                # Ensure final destination is exact
                if waypoints:
                    waypoints[-1] = (int(end[0]), int(end[1]))
                else:
                    waypoints = [end]
                return waypoints

            # 8-directional neighbors
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1),
                           (-1, -1), (1, -1), (-1, 1), (1, 1)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.ds_w and 0 <= ny < self.ds_h and (nx, ny) not in closed:
                    if self.ds_grid[nx][ny]:
                        cost = 1.414 if dx != 0 and dy != 0 else 1.0
                        ng = g_score[(cx, cy)] + cost
                        if ng < g_score.get((nx, ny), float("inf")):
                            g_score[(nx, ny)] = ng
                            f = ng + heuristic((nx, ny), (ex, ey))
                            came_from[(nx, ny)] = (cx, cy)
                            heapq.heappush(open_set, (f, nx, ny))

        # No path found — just go straight
        return [end]

    def get_debug_surface(self):
        """Build/return a cached semi-transparent overlay of the walkable area."""
        if self._debug_surface is None:
            self._debug_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            for x in range(0, self.width, 2):
                for y in range(0, self.height, 2):
                    if self.grid[x][y]:
                        self._debug_surface.fill((0, 255, 0, 60), (x, y, 2, 2))
        return self._debug_surface


class WalkableArea:
    """Defines where the player can walk using polygon(s)."""

    def __init__(self, polygons):
        # polygons is a list of polygon (each polygon = list of [x, y] points)
        self.polygons = [[(p[0], p[1]) for p in poly] for poly in polygons]

    def contains_point(self, point):
        for poly in self.polygons:
            if point_in_polygon(point, poly):
                return True
        return False

    def find_nearest_walkable(self, point):
        if self.contains_point(point):
            return point
        # Find nearest point in any polygon
        best = None
        best_dist = float("inf")
        for poly in self.polygons:
            candidate = find_nearest_point_in_polygon(point, poly)
            dx = candidate[0] - point[0]
            dy = candidate[1] - point[1]
            d = (dx * dx + dy * dy) ** 0.5
            if d < best_dist:
                best_dist = d
                best = candidate
        return best or point

    def get_path(self, start, end):
        """Find a path from start to end within the walkable area."""
        # Find which polygon contains the start point
        for poly in self.polygons:
            if point_in_polygon(start, poly) or point_in_polygon(end, poly):
                return find_path(start, end, poly)
        # If not in any polygon, try the first one
        if self.polygons:
            return find_path(start, end, self.polygons[0])
        return [end]


class Hotspot:
    """An interactive region in a scene."""

    def __init__(self, data):
        self.id = data["id"]
        self.name = data.get("name", self.id)
        rect = data.get("rect", [0, 0, 50, 50])
        self.rect = pygame.Rect(rect[0], rect[1], rect[2], rect[3])
        wt = data.get("walk_to")
        self.walk_to = tuple(wt) if wt else (self.rect.centerx, self.rect.bottom)
        self.look_at_dir = data.get("look_at_dir", "right")
        self.actions = data.get("actions", {})
        self.conditions = data.get("conditions", None)
        self.enabled = data.get("enabled", True)

    def contains_point(self, point):
        return self.enabled and self.rect.collidepoint(point)

    def get_available_actions(self):
        if not self.enabled:
            return []
        return list(self.actions.keys())


class Exit:
    """A trigger zone that transitions to another scene."""

    def __init__(self, data):
        self.id = data["id"]
        self.exit_type = data.get("exit_type", "hotspot")  # edge_left/right/top/bottom or hotspot
        rect = data.get("rect", [0, 0, 32, 32])
        self.rect = pygame.Rect(rect[0], rect[1], rect[2], rect[3])
        self.target_scene = data["target_scene"]
        self.target_entry = data.get("target_entry", "default")
        self.conditions = data.get("conditions", None)
        self.walk_to = data.get("walk_to", None)

    def contains_point(self, point):
        return self.rect.collidepoint(point)

    def is_edge_exit(self):
        return self.exit_type.startswith("edge_")


class Scene:
    """A game scene (room/location)."""

    def __init__(self, data):
        self.id = data["id"]
        self.name = data.get("name", self.id)
        self.bounds = data.get("bounds", [SCREEN_WIDTH, SCREEN_HEIGHT])

        # Background
        self.background = None
        bg_path = data.get("background")
        if bg_path:
            full_path = os.path.join(ASSETS_DIR, bg_path)
            if os.path.exists(full_path):
                self.background = pygame.image.load(full_path).convert()
                # Scale to scene bounds if dimensions don't match
                bw, bh = self.background.get_size()
                sw, sh = self.bounds
                if bw != sw or bh != sh:
                    self.background = pygame.transform.smoothscale(self.background, (sw, sh))
            else:
                self._create_placeholder_background(data)
        else:
            self._create_placeholder_background(data)

        # Music
        self.music = data.get("music")

        # Depth config
        dc = data.get("depth_config", {})
        self.depth_config = {
            "horizon_y": dc.get("horizon_y", 200),
            "ground_y": dc.get("ground_y", 680),
            "min_scale": dc.get("min_scale", 0.4),
            "max_scale": dc.get("max_scale", 1.0),
        }

        # Walkable area — try mask image first, fall back to polygons
        self.walkable_area = None
        if bg_path:
            base, ext = os.path.splitext(bg_path)
            mask_rel = base + "_walkable" + ext
            mask_full = os.path.join(ASSETS_DIR, mask_rel)
            if os.path.exists(mask_full):
                mask_surf = pygame.image.load(mask_full).convert_alpha()
                mw, mh = mask_surf.get_size()
                sw, sh = self.bounds
                if mw != sw or mh != sh:
                    mask_surf = pygame.transform.scale(mask_surf, (sw, sh))
                self.walkable_area = MaskWalkableArea(mask_surf, self.bounds)
        if self.walkable_area is None:
            wa_data = data.get("walkable_area", {})
            polygons = wa_data.get("polygons", [
                [[0, 400], [self.bounds[0], 400], [self.bounds[0], 700], [0, 700]]
            ])
            self.walkable_area = WalkableArea(polygons)

        # Entry points
        self.entry_points = {}
        for name, pos in data.get("entry_points", {"default": [200, 600]}).items():
            self.entry_points[name] = tuple(pos)

        # Hotspots
        self.hotspots = [Hotspot(h) for h in data.get("hotspots", [])]

        # Exits
        self.exits = [Exit(e) for e in data.get("exits", [])]

        # NPCs present in this scene
        self.npc_ids = data.get("npcs", [])

        # Scripts to run on enter/exit
        self.on_enter = data.get("on_enter", [])
        self.on_exit = data.get("on_exit", [])

    def _create_placeholder_background(self, data):
        """Create a simple gradient placeholder background."""
        w, h = self.bounds
        self.background = pygame.Surface((w, h))

        # Sky gradient
        for y in range(h):
            t = y / h
            r = int(130 + 60 * t)
            g = int(180 - 40 * t)
            b = int(220 - 80 * t)
            pygame.draw.line(self.background, (r, g, b), (0, y), (w, y))

        # Ground
        ground_y = self.depth_config.get("ground_y", 680) if hasattr(self, "depth_config") else 680
        horizon_y = self.depth_config.get("horizon_y", 200) if hasattr(self, "depth_config") else 200
        pygame.draw.rect(self.background, (80, 140, 60),
                         (0, int(h * 0.6), w, int(h * 0.4)))

        # Scene label
        font = pygame.font.Font(None, 36)
        label = font.render(data.get("name", data["id"]), True, (255, 255, 255))
        self.background.blit(label, (20, 20))

    def get_entry_point(self, entry_name="default"):
        return self.entry_points.get(entry_name, self.entry_points.get("default", (200, 600)))

    def get_hotspot_at(self, point):
        for hs in self.hotspots:
            if hs.contains_point(point):
                return hs
        return None

    def get_exit_at(self, point):
        for ex in self.exits:
            if ex.contains_point(point):
                return ex
        return None

    def get_hotspot_by_id(self, hotspot_id):
        for hs in self.hotspots:
            if hs.id == hotspot_id:
                return hs
        return None

    def draw_background(self, surface, camera_offset):
        if self.background:
            surface.blit(self.background, (-camera_offset[0], -camera_offset[1]))

    def draw_debug_walkable(self, surface, camera_offset):
        """Draw walkable area outlines for debugging."""
        if isinstance(self.walkable_area, MaskWalkableArea):
            overlay = self.walkable_area.get_debug_surface()
            surface.blit(overlay, (-camera_offset[0], -camera_offset[1]))
        else:
            for poly in self.walkable_area.polygons:
                points = [(int(p[0] - camera_offset[0]), int(p[1] - camera_offset[1]))
                          for p in poly]
                if len(points) >= 3:
                    pygame.draw.polygon(surface, (0, 255, 0), points, 2)

    def draw_debug_hotspots(self, surface, camera_offset):
        """Draw hotspot rectangles for debugging."""
        for hs in self.hotspots:
            if hs.enabled:
                r = hs.rect.move(-camera_offset[0], -camera_offset[1])
                pygame.draw.rect(surface, (255, 255, 0), r, 2)
                font = pygame.font.Font(None, 18)
                label = font.render(hs.name, True, (255, 255, 0))
                surface.blit(label, (r.x, r.y - 14))

    def draw_debug_exits(self, surface, camera_offset):
        """Draw exit rectangles for debugging."""
        for ex in self.exits:
            r = ex.rect.move(-camera_offset[0], -camera_offset[1])
            pygame.draw.rect(surface, (255, 0, 0), r, 2)
            font = pygame.font.Font(None, 18)
            label = font.render(f"-> {ex.target_scene}", True, (255, 100, 100))
            surface.blit(label, (r.x, r.y - 14))
