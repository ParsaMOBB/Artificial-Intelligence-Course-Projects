from ..environment.game import PacmanGame

"""
    Place your heuristic functions here.
"""

def manhattan_distance(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


def snack_priority_heuristic(game: PacmanGame) -> int:
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
