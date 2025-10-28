from core.environment.map_loader import MapLoader
from core.environment.game import PacmanGame
import time
import pandas as pd
from copy import deepcopy
from tabulate import tabulate
from config import *
import os
import glob

"""
    Runs a given 'solver' on a given 'game' and returns output of the 'solver'.
    It sets a time limit on the solver to terminate after reaching it. Change it from config.py
"""
def run_solver(solver, game, timeout=1):
    t1 = time.time()
    moves = solver(deepcopy(game), timeout=timeout)
    t2 = time.time()
    return moves, t2-t1

"""
    Runs each solver on the given map and returns the result in a Pandas.DataFrame.
    If solver_modes is provided, only runs those specific solvers.
"""
def run_test(file_path, solver_modes=None):
    df = pd.DataFrame(columns=['Algorithm', 'Time', 'Numof Moves', "Result"])

    is_wall, player, ghosts, snacks = MapLoader(file_path=file_path).load()
    game = PacmanGame(player=player, ghosts=ghosts, snacks=snacks, is_wall=is_wall, move_direction="")

    # If no specific solvers provided, use all solvers
    solvers_to_test = solver_modes if solver_modes else SOLVER_MODES

    for solver_mode in solvers_to_test:
        try:
            moves, time = run_solver(solver=SOLVERS[solver_mode], game=deepcopy(game), timeout=TIME_LIMITS[solver_mode])
        except:
            algorithm = solver_mode
            df.loc[len(df)] = [algorithm, time, 0, "Error"]
            continue
        algorithm = solver_mode
        if moves is None:
            df.loc[len(df)] = [algorithm, time, 0, "NotFound"]
        elif len(moves) == 1:
            df.loc[len(df)] = [algorithm, time, 0           , "Timeout"]
        else:
            df.loc[len(df)] = [algorithm, time, len(moves)-1, "Success"]

    df['Time'] = df['Time'].apply(lambda x: f"{x:.2f}")
    return df

"""
    Gets all available map files from the maps directory.
"""
def get_available_maps():
    map_files = glob.glob("./maps/*.txt")
    # Sort for consistent ordering
    map_files.sort()
    return [os.path.basename(f) for f in map_files]

"""
    Prompts user to select solvers.
"""
def select_solvers():
    print("\nWhich solver:")
    for idx, solver in enumerate(SOLVER_MODES, 1):
        print(f"{idx}. {solver}")
    print("\nEnter solver number(s) separated by commas (e.g., 1,3,5)")
    print("Leave empty if you want to run tests for all solvers above.")
    
    user_input = input("Your choice: ").strip()
    
    if not user_input:
        return None  # All solvers
    
    try:
        indices = [int(x.strip()) - 1 for x in user_input.split(',')]
        selected_solvers = [SOLVER_MODES[i] for i in indices if 0 <= i < len(SOLVER_MODES)]
        return selected_solvers if selected_solvers else None
    except (ValueError, IndexError):
        print("Invalid input. Running all solvers.")
        return None

"""
    Prompts user to select maps.
"""
def select_maps():
    available_maps = get_available_maps()
    
    print("\nWhich map:")
    for idx, map_file in enumerate(available_maps, 1):
        print(f"{idx}. {map_file}")
    print("\nEnter map number(s) separated by commas (e.g., 1,3,5)")
    print("Leave empty if you want to test all maps above.")
    
    user_input = input("Your choice: ").strip()
    
    if not user_input:
        return None  # All maps
    
    try:
        indices = [int(x.strip()) - 1 for x in user_input.split(',')]
        selected_maps = [available_maps[i] for i in indices if 0 <= i < len(available_maps)]
        return selected_maps if selected_maps else None
    except (ValueError, IndexError):
        print("Invalid input. Testing all maps.")
        return None

"""
    Runs tests based on user selections.
"""
def run_tests_interactive():
    selected_solvers = select_solvers()
    selected_maps = select_maps()
    
    # Get maps to test
    if selected_maps is None:
        maps_to_test = get_available_maps()
    else:
        maps_to_test = selected_maps
    
    # Run tests on each selected map
    for map_file in maps_to_test:
        result_df = run_test(file_path=f"./maps/{map_file}", solver_modes=selected_solvers)
        print(f"\nResults on {map_file}:")
        print(tabulate(result_df, headers='keys', tablefmt='fancy_grid', showindex=False))
        print()

"""
    Calls 'run_test' on every test and prints the result of each one.
    (Legacy function for backward compatibility)
"""
def run_all_tests():
    maps_to_test = get_available_maps()
    for map_file in maps_to_test:
        result_df = run_test(file_path=f"./maps/{map_file}")
        map_name = os.path.splitext(map_file)[0]
        print(f"Results on {map_name}:")
        print(tabulate(result_df, headers='keys', tablefmt='fancy_grid', showindex=False))
        print()

if __name__ == "__main__":
    from multiprocessing import freeze_support
    freeze_support()
    run_tests_interactive()