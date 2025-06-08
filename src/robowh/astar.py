"""A-star algorithm implementation."""

import heapq
import numpy as np

class Node:
    def __init__(self, position, parent=None, g=0, h=0):
        self.position = position
        self.parent = parent
        self.g = g
        self.h = h
        self.f = g + h

    def __lt__(self, other):
        return self.f < other.f


def find_path(grid, start, goal):
    """Core A* implementation returning list of positions (empty if no path)."""
    if not _valid_pos(grid, start) or not _valid_pos(grid, goal):
        return []

    open_heap = []
    closed_set = set()
    g_costs = {start: 0}
    heapq.heappush(open_heap, Node(start, g=0, h=_heuristic(start, goal)))

    while open_heap:
        current_node = heapq.heappop(open_heap)

        if current_node.position == goal:
            return _reconstruct_path(current_node)

        closed_set.add(current_node.position)

        for dy, dx in [(-1,0), (1,0), (0,-1), (0,1)]:
            y = current_node.position[0] + dy
            x = current_node.position[1] + dx
            neighbor_pos = (y, x)

            if not _valid_pos(grid, neighbor_pos):
                continue

            tentative_g = current_node.g + 1
            if neighbor_pos in g_costs and tentative_g >= g_costs[neighbor_pos]:
                continue

            g_costs[neighbor_pos] = tentative_g
            neighbor_node = Node(
                neighbor_pos,
                parent=current_node,
                g=tentative_g,
                h=_heuristic(neighbor_pos, goal)
            )

            if neighbor_pos not in closed_set:
                heapq.heappush(open_heap, neighbor_node)

    return []

def _heuristic(pos, target):
    return abs(pos[0] - target[0]) + abs(pos[1] - target[1])

def _valid_pos(grid, pos):
    y, x = pos
    return (0 <= y < grid.shape[0] and
            0 <= x < grid.shape[1] and
            grid[y, x] == 0)

def _reconstruct_path(node):
    path = []
    while node:
        path.append(node.position)
        node = node.parent
    return path[::-1]