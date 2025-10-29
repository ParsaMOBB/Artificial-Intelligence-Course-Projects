from typing import Dict, Optional, Tuple, List
from ..environment.game import PacmanGame
import time

"""
    Use this method (or any defined method by yourself) to run IDS algorithm on a given 'game' with a given 'max_limit'.
    At the end, you must return the walked path represented as a list of moves by using use PacmanGame.get_info()
    It's recommended to use the earlier defined DFS function here.
"""
def ids_solver(game: PacmanGame, max_limit: int = 100000, timeout=10):
    start_time = time.time()
    game.set_time(0)
    initial_state = game.get_state()
    initial_info = game.get_info()

    def reconstruct(target_state: str, parents: Dict[str, Optional[Tuple[str, str]]],
                    state_map: Dict[str, PacmanGame]) -> List:
        path_states: List[str] = []
        cursor = target_state
        while cursor is not None:
            path_states.append(cursor)
            parent_entry = parents[cursor]
            cursor = parent_entry[0] if parent_entry else None
        path_states.reverse()
        return [state_map[state_key].get_info() for state_key in path_states]

    def is_in_trace(current_key: str, candidate: str,
                    parents_map: Dict[str, Optional[Tuple[str, str]]]) -> bool:
        cursor = current_key
        while cursor is not None:
            if cursor == candidate:
                return True
            parent_entry = parents_map[cursor]
            cursor = parent_entry[0] if parent_entry else None
        return False

    best_trace = [initial_info]

    for depth_limit in range(max_limit + 1):
        if time.time() - start_time > timeout:
            return [initial_info]

        game.set_time(0)
        parents: Dict[str, Optional[Tuple[str, str]]] = {initial_state: None}
        state_to_game: Dict[str, PacmanGame] = {initial_state: game}
        stack: List[Tuple[str, int]] = [(initial_state, 0)]

        goal_state = None
        last_state = initial_state
        timeout_hit = False

        while stack:
            if time.time() - start_time > timeout:
                timeout_hit = True
                break

            current_state, depth = stack.pop()
            current_game = state_to_game[current_state]
            last_state = current_state

            if current_game.is_goal():
                goal_state = current_state
                break

            if depth == depth_limit:
                continue

            ghosts_now_set = current_game.get_ghost_positions()
            ghosts_now_seq = [(ghost.x, ghost.y) for ghost in current_game.ghosts]
            children = current_game.get_next_states()

            for move_direction, next_game in reversed(children):
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

                parents[next_state] = (current_state, move_direction)
                state_to_game[next_state] = next_game
                stack.append((next_state, depth + 1))

        if goal_state is not None:
            return reconstruct(goal_state, parents, state_to_game)

        best_trace = reconstruct(last_state, parents, state_to_game)

        if timeout_hit:
            return [initial_info]

    return best_trace
