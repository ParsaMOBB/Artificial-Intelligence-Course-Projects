from ..environment.game import PacmanGame

"""
Heuristic helper functions for Pacman search agents.
"""

def manhattan_distance(p1, p2):
    """Return the Manhattan distance between two grid coordinates."""
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


def snack_priority_heuristic(game: PacmanGame) -> int:
    """
    The heuristic estimates
    the cost to the farthest apple and then to the farthest strawberry from that
    apple. When no apples remain it falls back to the farthest strawberry. A goal
    state (no snacks left) reports zero.
    """
    if game.is_goal():
        return 0

    px, py = game.player
    apples = [(snack.x, snack.y) for snack in game.snacks if snack.exists and snack.type == 'A']
    strawberries = [(snack.x, snack.y) for snack in game.snacks if snack.exists and snack.type == 'B']

    if apples:
        best = 0
        for apple in apples:
            to_apple = manhattan_distance((px, py), apple)
            if strawberries:
                apple_to_strawberry = max(manhattan_distance(apple, strawberry) for strawberry in strawberries)
            else:
                apple_to_strawberry = 0
            best = max(best, to_apple + apple_to_strawberry)
        return best

    if strawberries:
        return max(manhattan_distance((px, py), strawberry) for strawberry in strawberries)

    return 0


def remaining_fruits_heuristic(game: PacmanGame) -> int:
    """
    Count the number of existing snacks as an optimistic remaining cost.

    Each remaining snack contributes one unit regardless of its position, making
    the heuristic admissible but potentially not very informed.
    """
    if game.is_goal():
        return 0
    return sum(1 for snack in game.snacks if snack.exists)
