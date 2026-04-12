"""A* pathfinding within a walkable polygon using a visibility graph."""
import heapq
import math


def point_in_polygon(point, polygon):
    """Ray-casting algorithm to test if a point is inside a polygon."""
    x, y = point
    n = len(polygon)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def segments_intersect(p1, p2, p3, p4):
    """Check if line segment p1-p2 intersects p3-p4 (proper intersection only)."""
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    d1 = cross(p3, p4, p1)
    d2 = cross(p3, p4, p2)
    d3 = cross(p1, p2, p3)
    d4 = cross(p1, p2, p4)

    if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and \
       ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
        return True
    return False


def line_clear(p1, p2, polygon):
    """Check if the line segment from p1 to p2 stays inside the walkable polygon.

    Tests that the segment doesn't cross any polygon edge (proper intersection)
    and that the midpoint is inside the polygon.
    """
    n = len(polygon)
    for i in range(n):
        j = (i + 1) % n
        edge_start = polygon[i]
        edge_end = polygon[j]
        # Skip edges that share an endpoint with our segment
        if edge_start == p1 or edge_start == p2 or edge_end == p1 or edge_end == p2:
            continue
        if segments_intersect(p1, p2, edge_start, edge_end):
            return False

    # Also check midpoint is inside polygon
    mid = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
    return point_in_polygon(mid, polygon)


def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def find_nearest_point_in_polygon(point, polygon):
    """Find the nearest point inside the polygon to the given point."""
    if point_in_polygon(point, polygon):
        return point

    # Find nearest point on each edge
    best = None
    best_dist = float("inf")

    n = len(polygon)
    for i in range(n):
        j = (i + 1) % n
        nearest = nearest_point_on_segment(point, polygon[i], polygon[j])
        d = distance(point, nearest)
        if d < best_dist:
            best_dist = d
            best = nearest

    if best:
        # Nudge slightly inward
        cx = sum(p[0] for p in polygon) / len(polygon)
        cy = sum(p[1] for p in polygon) / len(polygon)
        dx = cx - best[0]
        dy = cy - best[1]
        mag = math.sqrt(dx * dx + dy * dy)
        if mag > 0:
            best = (best[0] + dx / mag * 2, best[1] + dy / mag * 2)

    return best or point


def nearest_point_on_segment(point, seg_a, seg_b):
    """Find the nearest point on segment seg_a-seg_b to point."""
    ax, ay = seg_a
    bx, by = seg_b
    px, py = point

    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return seg_a

    t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return (ax + t * dx, ay + t * dy)


def find_path(start, end, polygon):
    """Find a path from start to end within the walkable polygon using A*.

    Uses a visibility graph built from polygon vertices plus start/end points.
    Returns a list of waypoints (tuples), or [end] if direct path exists,
    or [start] if no path found.
    """
    start = (float(start[0]), float(start[1]))
    end = (float(end[0]), float(end[1]))

    # Make sure start and end are inside the polygon
    if not point_in_polygon(start, polygon):
        start = find_nearest_point_in_polygon(start, polygon)
    if not point_in_polygon(end, polygon):
        end = find_nearest_point_in_polygon(end, polygon)

    # Direct line of sight?
    if line_clear(start, end, polygon):
        return [end]

    # Build visibility graph with polygon vertices + start + end
    vertices = [tuple(v) for v in polygon]
    # Only include vertices that are inside the polygon (concave corners)
    # For simple convex/concave polygons, all vertices are candidates
    nodes = [start, end]
    for v in vertices:
        # Offset vertex slightly inward to avoid edge cases
        cx = sum(p[0] for p in polygon) / len(polygon)
        cy = sum(p[1] for p in polygon) / len(polygon)
        dx = cx - v[0]
        dy = cy - v[1]
        mag = math.sqrt(dx * dx + dy * dy)
        if mag > 0:
            inset = (v[0] + dx / mag * 3, v[1] + dy / mag * 3)
            if point_in_polygon(inset, polygon):
                nodes.append(inset)

    # Build adjacency: connect nodes that can see each other
    graph = {i: [] for i in range(len(nodes))}
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            if line_clear(nodes[i], nodes[j], polygon):
                d = distance(nodes[i], nodes[j])
                graph[i].append((j, d))
                graph[j].append((i, d))

    # A* search from node 0 (start) to node 1 (end)
    open_set = [(0, 0)]  # (f_score, node_index)
    g_score = {0: 0}
    came_from = {}
    closed = set()

    while open_set:
        _, current = heapq.heappop(open_set)
        if current == 1:
            # Reconstruct path
            path = [nodes[1]]
            while current in came_from:
                current = came_from[current]
                if current != 0:
                    path.append(nodes[current])
            path.reverse()
            return path

        if current in closed:
            continue
        closed.add(current)

        for neighbor, cost in graph[current]:
            if neighbor in closed:
                continue
            tentative_g = g_score[current] + cost
            if tentative_g < g_score.get(neighbor, float("inf")):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score = tentative_g + distance(nodes[neighbor], nodes[1])
                heapq.heappush(open_set, (f_score, neighbor))

    # No path found, just go to end directly
    return [end]
