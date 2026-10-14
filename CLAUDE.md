# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository shape

Course-assignment repo (University of Tehran, AI course, Fall 2025). Each `CA<n>/` is an independent,
self-contained assignment — no shared package, no cross-CA imports, no build system, no test suite.
Each folder also holds the original assignment PDF (`AI*CA<n>.pdf`), which is the spec for what the
code must do.

| Dir | Topic | Entry point |
| --- | --- | --- |
| `CA1` | Pac-Man search (BFS/DFS/IDS/A*/Weighted A*) | `codes/main.py` (pygame GUI), `codes/tester.py` |
| `CA2` | Genetic algorithm (image-jigsaw reassembly) + Minimax/alpha-beta Dots & Boxes | `Report.ipynb` |
| `CA3` | Decision trees (from scratch), Naive Bayes, ensembles, regression | `CA3.ipynb` |
| `CA4` | PyTorch intro + TextCNN sentiment on SnappFood (Persian) | `Introduction_to_PyTorch.ipynb` |
| `CA5` | Amazon review clustering (SentenceTransformer embeddings) | `CA5_project.ipynb` |

CA2–CA5 are single-notebook assignments: implementation *and* the written answers to the assignment
questions live in the same notebook (a "Questions" section at the end). CA1 is the only one with a
real Python package layout; its answers live in `CA1/report.md`. Reports/answers are written in
Persian with RTL HTML blocks — preserve that formatting when editing them.

## Running things

**Everything uses relative paths and must be run with the CWD set to its own CA directory.**
`CA1/codes/core/environment/map_loader.py` does `from config import GHOST_MOVE_LIMIT` (a top-level
import of `CA1/codes/config.py`), and every notebook reads data like `./amazon_reviews.csv`.

```bash
# CA1 — GUI; the in-game menu selects mode (Player / BFS / DFS / IDS / A* / Weighted A* / Naive),
# player speed, map, and mute. Needs pygame + the assets/ dir.
cd CA1/codes && python main.py

# CA1 — benchmark harness; prompts for solver number(s) and map number(s) (comma-separated,
# empty = all). This is the closest thing to a test runner in the repo.
cd CA1/codes && python tester.py

# CA1 — A* vs Weighted A* (w=1,2,10) across both heuristics
cd CA1/codes && python tester_weighted.py

# CA2–CA5 — notebooks
cd CA3 && jupyter lab CA3.ipynb
```

Reference outputs for CA1 are committed under `CA1/outputs/`; regenerate them by redirecting the
tester output there.

Dependencies are not pinned anywhere. CA1 needs `pygame`, `pandas`, `tabulate`; the notebooks
`%pip install` what they need in their first cells (sklearn, xgboost, nltk, torch, fasttext,
sentence-transformers, umap-learn, itables).

Large model artifacts are deliberately untracked: `CA4/cc.fa.300.bin` (fastText Persian vectors,
downloaded by the notebook) and `CA5/models/*` (a local copy of `all-MiniLM-L6-v2`; the notebook
falls back to the hub name if the directory is missing).

## CA1 architecture

Two parallel, deliberately separate worlds — don't try to unify them:

- `entities/` (`Wall`, `Player`, `Fruit`, `Ghost`) — pixel-space pygame sprites, used **only** by
  Player mode in `main.py`.
- `core/` — headless simulation used by the solvers. `MapLoader` parses a map into
  `(is_wall, player, ghosts, snacks)`; `PacmanGame` is the search model.

**Coordinate convention is the most common source of bugs.** `core/` is row-major: `x` is the row,
`y` is the column (`is_wall[x][y]`), so `MapLoader` constructs `Ghost(x=y, y=x)` while reading the
file. `entities/` and all rendering use screen order (`x` = column). `main.py:update_render_state`
is where the two meet.

### Solver contract

A solver is `solver(game: PacmanGame, timeout=10) -> list`, where each element is a
`game.get_info()` tuple `(move_direction, [player_pos, *ghost_positions, *snack_infos])`, ordered
from the initial state to the goal. Callers treat the return value as:

- `None` → no solution found (`tester.py` reports `NotFound`)
- list of length 1 (just the initial info) → hit the time limit (`Timeout`)
- longer list → `Success`, with `len(moves) - 1` moves; `main.py` pops element 0 and replays the rest

To add a solver: drop it in `core/solvers/`, then register it in `config.py` in all three places —
`SOLVER_MODES`, `SOLVERS`, and `TIME_LIMITS`. The GUI menu and testers derive their options from
those lists.

### State encoding

`PacmanGame.get_state()` returns `"P:{x},{y}|S:[{remaining snacks}]|T:{t}"`. Ghosts are omitted
because they oscillate deterministically, so `t = time % TIME_MOD` (24 = lcm of the possible
periods) pins their positions exactly. Any solver that expands states must call
`next_game.set_time(current.get_time() + 1)` before `get_state()`, or distinct states collapse and
search becomes unsound. See `CA1/report.md` Q1 for the reasoning.

Game rules encoded in `core/`: snacks must be eaten in type order — `Snack.update_state` refuses to
clear a `'B'` (strawberry) while any `'A'` (apple) still exists. Collision pruning must cover both
landing on a ghost and swapping places with one (see `bfs_solver.py`). Ghosts reverse at walls or at
`GHOST_MOVE_LIMIT` cells from their center.

Maps (`codes/maps/*.txt`) are plain character grids: `W` wall, `P` pacman, `A`/`B` snacks,
`H`/`V` horizontally/vertically oscillating ghosts, space = empty.

## Notebook conventions (CA3–CA5)

Each notebook reads its inputs and writes its graded outputs as CSVs beside itself, with fixed
filenames that the grader expects — e.g. CA3 writes `s1_part1_predictions.csv`,
`part2/3/4_predictions.csv` from the corresponding `*_dataset.csv` / `*_test.csv`; CA5 writes
`best_labels.csv` (review id + one label column per clustering method). Don't rename these.

## Git conventions

Conventional commits scoped by assignment — `feat(CA5): implement all parts`,
`docs(CA3): add project description and materials`, `fix(CA1): fix timeout issue in solvers`. Work
lands on `feature/CA<n>-<Topic>` branches and merges into `main` via PR.
