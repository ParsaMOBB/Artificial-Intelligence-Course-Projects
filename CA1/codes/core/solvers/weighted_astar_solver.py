import heapq
import itertools
import time
from typing import Dict, Optional, Tuple, List
from ..environment.game import PacmanGame
from .heuristics import snack_priority_heuristic

"""
    Use this method (or any defined method by yourself) to run Weighted A* algorithm on a given 'game' with a given 'heuristic and an weight.
    At the end, you must return the walked path represented as a list of moves by using use PacmanGame.get_info()
"""
def weighted_astar_solver(game: PacmanGame, heuristic_func=snack_priority_heuristic, weight: int = 10, timeout=10):
    start_time = time.time()
    game.set_time(0)
    initial_state = game.get_state()

    parents: Dict[str, Optional[Tuple[str, str]]] = {initial_state: None}
    state_to_game: Dict[str, PacmanGame] = {initial_state: game}
    g_cost: Dict[str, int] = {initial_state: 0}

    counter = itertools.count()
    open_heap: List[Tuple[float, int, str]] = []
    initial_priority = weight * heuristic_func(game)
    heapq.heappush(open_heap, (initial_priority, next(counter), initial_state))

    goal_state = None
    last_state = initial_state

    def is_in_trace(current_key: str, candidate: str,
                    parents_map: Dict[str, Optional[Tuple[str, str]]]) -> bool:
        cursor = current_key
        while cursor is not None:
            if cursor == candidate:
                return True
            parent_entry = parents_map[cursor]
            cursor = parent_entry[0] if parent_entry else None
        return False

    def reconstruct(target_state: str) -> List:
        path_states: List[str] = []
        cursor = target_state
        while cursor is not None:
            path_states.append(cursor)
            parent_entry = parents[cursor]
            cursor = parent_entry[0] if parent_entry else None
        path_states.reverse()
        return [state_to_game[state_key].get_info() for state_key in path_states]

    while open_heap:
        if time.time() - start_time > timeout:
            break

        _, _, current_state = heapq.heappop(open_heap)
        current_game = state_to_game[current_state]
        last_state = current_state

        if current_game.is_goal():
            goal_state = current_state
            break

        ghosts_now_seq = [(ghost.x, ghost.y) for ghost in current_game.ghosts]

        for move_direction, next_game in current_game.get_next_states():
            next_game.set_time((current_game.get_time() + 1) % next_game.time_mod)
            next_state = next_game.get_state()

            if is_in_trace(current_state, next_state, parents):
                continue

            ghosts_next_set = next_game.get_ghost_positions()
            ghosts_next_seq = [(ghost.x, ghost.y) for ghost in next_game.ghosts]
            next_player_pos = next_game.player
            current_player_pos = current_game.player

            if next_player_pos in ghosts_next_set:
                continue

            swap_collision = False
            for prev_pos, new_pos in zip(ghosts_now_seq, ghosts_next_seq):
                if prev_pos == next_player_pos and new_pos == current_player_pos:
                    swap_collision = True
                    break

            if swap_collision:
                continue

            tentative_g = g_cost[current_state] + 1
            best_known = g_cost.get(next_state)
            if best_known is not None and tentative_g >= best_known:
                continue

            parents[next_state] = (current_state, move_direction)
            state_to_game[next_state] = next_game
            g_cost[next_state] = tentative_g

            priority = tentative_g + weight * heuristic_func(next_game)
            heapq.heappush(open_heap, (priority, next(counter), next_state))

    if goal_state is None:
        goal_state = last_state

    return reconstruct(goal_state)
