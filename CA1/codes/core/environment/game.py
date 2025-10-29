from copy import deepcopy
from .ghost import Ghost
from .snack import Snack

TIME_MOD = 24
class PacmanGame:
    def __init__(self, player : tuple[int, int], ghosts : list[Ghost], snacks : list[Snack], is_wall, move_direction = None):
        self.player = player
        self.ghosts = deepcopy(ghosts)
        self.snacks = deepcopy(snacks)
        self.is_wall = is_wall
        self.move_direction = move_direction if move_direction is not None else ""
        self.height = len(is_wall)
        self.width = len(is_wall[0]) if self.height > 0 else 0
        self.time = 0
        self.time_mod = TIME_MOD

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
    def get_next_states(self):
        next_states = []

        moves = {
            "U": (-1, 0),
            "L": (0, -1),
            "D": (1, 0),
            "R": (0, 1)
        }

        px, py = self.player
        
        for direction, (dx, dy) in moves.items():
            nx, ny = px + dx, py + dy
            
            if not self.is_valid(nx, ny):
                continue
            
            # Create new game state
            new_game = PacmanGame(player=(nx, ny), ghosts=self.ghosts, snacks=self.snacks, is_wall=self.is_wall, move_direction=direction)
            
            # Move ghosts
            new_game.move_ghosts()
            
            # Check if we're eating a snack
            target_snack = None
            for snack in new_game.snacks:
                if snack.x == nx and snack.y == ny and snack.exists:
                    target_snack = snack
                    break
            
            if target_snack:
                target_snack.update_state(new_game.snacks)
            
            next_states.append((direction, new_game))
        
        return next_states
    
    def move_ghosts(self):
        """Move all ghosts according to their oscillation pattern"""
        for ghost in self.ghosts:
            next_x, next_y = ghost.get_next_position()
            
            # Check if ghost hits wall or goes out of bounds, or reached radius limit
            center_x, center_y = ghost.center
            
            # Calculate distance from center
            if ghost.is_horizontal():
                distance_from_center = abs(next_y - center_y)
            else:
                distance_from_center = abs(next_x - center_x)
            
            # Check if the next position is valid and within radius
            if not self.is_valid(next_x, next_y) or distance_from_center >= ghost.radius:
                # Reverse direction
                ghost.direction *= -1
                # Get the position after reversing direction
                next_x, next_y = ghost.get_next_position()
            
            ghost.x = next_x
            ghost.y = next_y
    
    def get_ghost_positions(self):
        """Return a set of all ghost positions"""
        return {(ghost.x, ghost.y) for ghost in self.ghosts}
    
    """
        Use this method (or any defined method by yourself) to represent current state of the game.
    """
    def get_state(self):
        # Player position
        px, py = self.player
        # Non-eaten snacks positions (sorted for determinism)
        remaining_snacks = sorted((snack.x, snack.y) for snack in self.snacks if snack.exists)
        snacks_str = ";".join(f"{x},{y}" for x, y in remaining_snacks)
        # Time modulo time_mod uniquely determines ghost positions
        t = self.time % self.time_mod

        return f"P:{px},{py}|S:[{snacks_str}]|T:{t}"

    """
        It returns the list of snacks which are not eaten yet.
    """
    def get_none_eaten_snacks(self):
        return [snack for snack in self.snacks if snack.exists]

    def set_time(self, time):
        self.time = time % self.time_mod

    def get_time(self):
        return self.time
    
    def increment_time(self):
        self.time += 1
        self.time %= self.time_mod
