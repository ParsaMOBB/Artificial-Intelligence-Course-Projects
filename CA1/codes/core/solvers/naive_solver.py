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
            return path if path else [game.get_info()]
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
    
    # Each ghost has a period of 2*radius movements
    # Calculate LCM of all ghost periods (for simplicity, use max period * 2)
    max_period = max([2 * ghost.radius + 1 for ghost in game.ghosts], default=4)
    period = int(__import__("math").lcm(*range(1, max_period + 1)))
    
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
            
            # Simulate this move to get ghost positions at time next_time
            test_game = PacmanGame(player=(nx, ny), ghosts=game.ghosts, 
                                  snacks=game.snacks, is_wall=game.is_wall, 
                                  move_direction=direction)
            
            # Simulate ghost movements for next_time steps
            for _ in range(next_time):
                test_game.move_ghosts()
            
            ghost_positions = test_game.get_ghost_positions()
            
            # Don't move to a position where a ghost will be
            if (nx, ny) not in ghost_positions:
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
