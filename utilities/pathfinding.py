# pathfinding.py - Pathfinding and line of sight algorithms
import heapq
import math


def heuristic(a, b):
    # Manhattan distance
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def a_star_pathfinding(start_x, start_y, goal_x, goal_y, game_map):
    """
    A* pathfinding algorithm to find path from start to goal
    """
    start = (int(start_x), int(start_y))
    goal = (int(goal_x), int(goal_y))

    # If the target is a wall, find the closest non-wall tile
    if game_map.is_wall(goal[0], goal[1]):
        return []

    # Priority queue for open nodes
    open_set = []
    heapq.heappush(open_set, (0, start))

    # For node n, came_from[n] is the node immediately preceding it on the path
    came_from = {}

    # For node n, g_score[n] is the cost of the cheapest path from start to n
    g_score = {start: 0}

    # For node n, f_score[n] = g_score[n] + heuristic(n, goal)
    f_score = {start: heuristic(start, goal)}

    # The set of nodes already evaluated
    closed_set = set()

    while open_set:
        # Get the node with the lowest f_score
        current_f, current = heapq.heappop(open_set)

        if current == goal:
            # Path found, reconstruct and return
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        closed_set.add(current)

        # Check all adjacent tiles
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            neighbor = (current[0] + dx, current[1] + dy)

            # Skip if out of bounds or wall
            if game_map.is_wall(neighbor[0], neighbor[1]):
                continue

            if neighbor in closed_set:
                continue

            # Distance from start to neighbor through current
            tentative_g_score = g_score[current] + 1

            # If this path to neighbor is better than any previous one, record it
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                if neighbor not in [i[1] for i in open_set]:
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

    # No path found
    return []


def has_line_of_sight(x0, y0, x1, y1, game_map):
    """
    Bresenham's line algorithm for line of sight checking
    """
    x0, y0 = int(x0), int(y0)
    x1, y1 = int(x1), int(y1)

    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while x0 != x1 or y0 != y1:
        if game_map.is_wall(x0, y0):
            return False

        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy

    return True