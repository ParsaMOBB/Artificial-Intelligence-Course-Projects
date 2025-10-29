from ..environment.game import PacmanGame
from .heuristics import snack_priority_heuristic
from .weighted_astar_solver import weighted_astar_solver

"""
    Use this method (or any defined method by yourself) to run A* algorithm on a given 'game' with a given 'heuristic'.
    At the end, you must return the walked path represented as a list of moves by using use PacmanGame.get_info()
    It's recommended to use the earlier defined weighted A* function here.
"""

def astar_solver(game: PacmanGame, timeout=10):
    return weighted_astar_solver(game, heuristic_func=snack_priority_heuristic, weight=1, timeout=timeout)
