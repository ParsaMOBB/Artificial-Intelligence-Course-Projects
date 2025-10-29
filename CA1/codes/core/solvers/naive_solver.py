from numpy import gcd
from ..environment.game import PacmanGame
from copy import deepcopy
import time
from collections import deque

"""
    This solver is just for testing purposes.
    It just selects the first available fruit in the list,
    and goes straight to it.
"""
def naive_solver(game: PacmanGame, timeout=10):
    t0 = time.time()
    path = []

    # Ensure the initial state is captured
    try:
        path.append(game.get_info())
    except Exception:
        pass

    while not game.is_goal():
        if time.time() - t0 > timeout:
            return [path[0]] if path[0] else [game.get_info()]
        goal = game.determine_goal()
        non_eaten_snacks = game.get_none_eaten_snacks()
        target_snacks = [snack for snack in non_eaten_snacks if snack.type == goal]
        target_snack = target_snacks[0] if target_snacks else None

        if target_snack is None:
            break

        # Find path to target using BFS
        path_sequence = find_path_to_target(game, target_snack)
        
        if not path_sequence:
            break
        
        # Execute the path
        for move_dir in path_sequence:
            move_towards_target(game, move_dir)
            path.append(game.get_info())
            
            if game.is_goal():
                break

    return path if path else [game.get_info()]

def find_path_to_target(game: PacmanGame, target_snack):
    """Use BFS with time-aware state space to find a path avoiding ghosts"""
    px, py = game.player
    tx, ty = target_snack.x, target_snack.y
    
    moves = {
        "U": (-1, 0),
        "L": (0, -1),
        "D": (1, 0),
        "R": (0, 1)
    }
    
    # A conservative period to bound visited states; fallback to fixed cap
    # Note: exact period isn't critical for correctness here
    max_period = max([2 * ghost.radius + 1 for ghost in game.ghosts], default=8)
    try:
        period = int(__import__("math").lcm(*range(1, max_period + 1)))
    except Exception:
        period = 24
    
    queue = deque()
    queue.append((px, py, 0, []))  # (x, y, time, path)
    visited = set()
    
    while queue:
        x, y, t, path = queue.popleft()
        
        # Check if we reached the target
        if x == tx and y == ty:
            return path
        
        state_key = (x, y, t % period)
        if state_key in visited:
            continue
        visited.add(state_key)
        
        # Try all four directions
        for direction, (dx, dy) in moves.items():
            nx, ny = x + dx, y + dy
            next_time = t + 1
            
            # Check if valid cell
            if not game.is_valid(nx, ny):
                continue
            
            # Simulate ghosts at time t and t+1 to prevent pass-through/swap collisions
            sim_game = PacmanGame(player=(x, y), ghosts=game.ghosts,
                                  snacks=game.snacks, is_wall=game.is_wall,
                                  move_direction=direction)
            # advance to time t
            for _ in range(t):
                sim_game.move_ghosts()
            ghosts_t = sim_game.get_ghost_positions()
            # advance to time t+1
            sim_game.move_ghosts()
            ghosts_t1 = sim_game.get_ghost_positions()

            # Collision rules:
            # 1) Direct collision: player's next cell occupied at t+1 by any ghost
            if (nx, ny) in ghosts_t1:
                continue
            # 2) Swap collision: a ghost at (nx, ny) at t moves to (x, y) at t+1 while player moves x,y->nx,ny
            if (nx, ny) in ghosts_t and (x, y) in ghosts_t1:
                continue

            queue.append((nx, ny, next_time, path + [direction]))
    
    return []  # No path found

def move_towards_target(game, direction):
    """Apply a single move in the given direction"""
    moves = {
        "U": (-1, 0),
        "L": (0, -1),
        "D": (1, 0),
        "R": (0, 1)
    }
    
    px, py = game.player
    dx, dy = moves[direction]
    nx, ny = px + dx, py + dy
    
    if game.is_valid(nx, ny):
        game.player = (nx, ny)
        game.move_direction = direction
        
        # Move ghosts
        game.move_ghosts()
        
        # Check if we're eating a snack
        target_snack = None
        for snack in game.snacks:
            if snack.x == nx and snack.y == ny and snack.exists:
                target_snack = snack
                break
        
        if target_snack:
            target_snack.update_state(game.snacks)
    
    return game.get_info()
