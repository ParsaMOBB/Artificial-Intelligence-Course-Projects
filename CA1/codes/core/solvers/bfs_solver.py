from collections import deque
from typing import Dict, Optional, Tuple, List
from ..environment.game import PacmanGame
import time

"""
    Use this method (or any defined method by yourself) to run BFS algorithm on a given 'game'.
    At the end, you must return the walked path represented as a list of moves by using use PacmanGame.get_info()
"""
def bfs_solver(game: PacmanGame, timeout=10):
    start_time = time.time()
    game.set_time(0)
    initial_state = game.get_state()

    visited: Dict[str, PacmanGame] = {initial_state: game}
    parents: Dict[str, Optional[Tuple[str, str]]] = {initial_state: None}
    queue: deque[str] = deque([initial_state])

    goal_state = None
    last_state = initial_state

    while queue:
        if time.time() - start_time > timeout:
            break

        current_state = queue.popleft()
        current_game = visited[current_state]
        last_state = current_state

        if current_game.is_goal():
            goal_state = current_state
            break

        ghosts_now_set = current_game.get_ghost_positions()
        ghosts_now_seq = [(ghost.x, ghost.y) for ghost in current_game.ghosts]
        for move_direction, next_game in current_game.get_next_states():
            next_game.set_time((current_game.get_time() + 1) % next_game.time_mod)
            next_state = next_game.get_state()

            if next_state in visited:
                continue

            ghosts_next_set = next_game.get_ghost_positions()
            ghosts_next_seq = [(ghost.x, ghost.y) for ghost in next_game.ghosts]
            next_player_pos = next_game.player
            current_player_pos = current_game.player

            if next_player_pos in ghosts_next_set:
                continue

            swap_collision = False
            for (prev_pos, new_pos) in zip(ghosts_now_seq, ghosts_next_seq):
                if prev_pos == next_player_pos and new_pos == current_player_pos:
                    swap_collision = True
                    break

            if swap_collision:
                continue

            visited[next_state] = next_game
            parents[next_state] = (current_state, move_direction)
            queue.append(next_state)

    if goal_state is None:
        goal_state = last_state

    traversal: List[str] = []
    cursor = goal_state
    while cursor is not None:
        traversal.append(cursor)
        parent_entry = parents[cursor]
        cursor = parent_entry[0] if parent_entry else None

    traversal.reverse()
    return [visited[state_key].get_info() for state_key in traversal]
