import glob
import os
import time
from copy import deepcopy

import pandas as pd
from tabulate import tabulate

from config import TIME_LIMITS
from core.environment.game import PacmanGame
from core.environment.map_loader import MapLoader
from core.solvers.heuristics import (
    remaining_fruits_heuristic,
    snack_priority_heuristic,
)
from core.solvers.weighted_astar_solver import weighted_astar_solver


HEURISTICS = [
    ("Type 1", snack_priority_heuristic),
    ("Type 2", remaining_fruits_heuristic),
]

WEIGHT_CONFIGS = [
    ("A*", 1, TIME_LIMITS["A*"]),
    ("Weighted A*", 2, TIME_LIMITS["Weighted A*"]),
    ("Weighted A*", 10, TIME_LIMITS["Weighted A*"]),
]


def run_weighted_solver(game: PacmanGame, heuristic_func, weight: int, timeout: int):
    cloned_game = deepcopy(game)
    start = time.time()
    moves = weighted_astar_solver(
        cloned_game,
        heuristic_func=heuristic_func,
        weight=weight,
        timeout=timeout,
    )
    elapsed = time.time() - start
    return moves, elapsed


def evaluate_map(file_path: str) -> pd.DataFrame:
    df = pd.DataFrame(columns=["Algorithm", "Time", "Numof Moves", "Result"])

    is_wall, player, ghosts, snacks = MapLoader(file_path=file_path).load()
    base_game = PacmanGame(
        player=player,
        ghosts=ghosts,
        snacks=snacks,
        is_wall=is_wall,
        move_direction="",
    )

    for heuristic_label, heuristic_func in HEURISTICS:
        for algorithm_label, weight, timeout in WEIGHT_CONFIGS:
            algo_name = (
                f"{algorithm_label} | Heuristic={heuristic_label} | Weight={weight}"
            )
            try:
                moves, elapsed = run_weighted_solver(
                    base_game,
                    heuristic_func=heuristic_func,
                    weight=weight,
                    timeout=timeout,
                )
            except Exception:
                elapsed = 0.0
                df.loc[len(df)] = [algo_name, elapsed, 0, "Error"]
                continue

            if moves is None:
                df.loc[len(df)] = [algo_name, elapsed, 0, "NotFound"]
            elif len(moves) == 1:
                df.loc[len(df)] = [algo_name, elapsed, 0, "Timeout"]
            else:
                df.loc[len(df)] = [algo_name, elapsed, len(moves) - 1, "Success"]

    df["Time"] = df["Time"].apply(lambda x: f"{x:.2f}")
    return df


def list_maps():
    map_files = glob.glob("./maps/*.txt")
    map_files.sort()
    return map_files


def run_all():
    for map_path in list_maps():
        result_df = evaluate_map(map_path)
        map_name = os.path.splitext(os.path.basename(map_path))[0]
        print(f"Results on {map_name}:")
        print(tabulate(result_df, headers="keys", tablefmt="fancy_grid", showindex=False))
        print()


if __name__ == "__main__":
    run_all()
