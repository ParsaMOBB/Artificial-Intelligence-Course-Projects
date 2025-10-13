from copy import deepcopy
from .ghost import Ghost
from .snack import Snack

class PacmanGame:
    def __init__(self, player : tuple[int, int], ghosts : list[Ghost], snacks : list[Snack], is_wall, move_direction = None):
        self.player = player
        self.ghosts = deepcopy(ghosts)
        self.snacks = deepcopy(snacks)
        self.is_wall = is_wall

    """
        It returns a pair of move_direction and information for dynamic objects of the game.
        Store this information and return it in solvers. It's used on the GUI feature.
    """    
    def get_info(self):
        return (self.move_direction, [self.player] + [ghost.get_info() for ghost in self.ghosts] + [snack.get_info() for snack in self.snacks])

    """
        It returns the snack which is supposed to get eaten to on current state of the game.
    """
    def determine_goal(self):
        remaining_snacks = [s.type for s in self.snacks if s.exists]
        if len(remaining_snacks) == 0:
            return None
        return min(remaining_snacks)

    """
        Determines if (x, y) is in bounds of map or not.
    """
    def in_bounds(self, x, y):
        return 0 <= x < self.height and 0 <= y < self.width

    """
        Determines if player/ghost can go to (x, y) without hitting a wall or getting out of bounds
    """
    def is_valid(self, x, y):
        return self.in_bounds(x, y) and not self.is_wall[x][y]

    """
        It determines if the game is finished or not.
    """
    def is_goal(self):
        return all(not b for b in [snack.exists for snack in self.snacks])
    
    """
        It returns a string form of the map at current state.
    """    
    def get_map(self) -> str:
        height = len(self.is_wall)
        width = len(self.is_wall[0])
        display_grid = [[' ' for _ in range(width)] for _ in range(height)]

        for x in range(height):
            for y in range(width):
                if self.is_wall[x][y]:
                    display_grid[x][y] = 'W'

        for snack in self.snacks:
            if snack.exists:
                display_grid[snack.x][snack.y] = f'{snack.type}'

        for g in self.ghosts:
            gx, gy = g.x, g.y
            display_grid[gx][gy] = f'{g.axis}'

        px, py = self.player
        display_grid[px][py] = 'P'

        map_string = "╔" + "═" * width + "╗" + "\n"
        for row in display_grid:
            map_string += "║" + "".join(row) + "║" + "\n"
        return map_string + "╚" + "═" * width + "╝" + "\n"
    

    """
        Use this method (or any defined method by yourself) to explore next possible states of the game.
    """
    # TODO
    def get_next_states(self):
        next_states = []

        moves = {
            "U": (-1, 0),
            "L": (0, -1),
            "D": (1, 0),
            "R": (0, 1)
        }

        return next_states
    
    """
        Use this method (or any defined method by yourself) to represent current state of the game.
    """
    # TODO
    def get_state(self):
        pass
