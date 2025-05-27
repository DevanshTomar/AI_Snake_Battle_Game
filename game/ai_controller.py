from enums import Direction
from config import GRID_WIDTH, GRID_HEIGHT
from utils.pathfinding import (
    bfs_pathfind, get_direction_to_target, 
    calculate_distance, get_all_obstacles
)

class AIController:
    def __init__(self, snake1, snake2):
        self.snake1 = snake1
        self.snake2 = snake2
    
    def get_safe_direction(self, snake):
        head_x, head_y = snake.get_head()
        obstacles = get_all_obstacles(self.snake1, self.snake2, snake)
        
        for direction in Direction:
            dx, dy = direction.value
            new_x, new_y = head_x + dx, head_y + dy
            

            if (0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT and
                (new_x, new_y) not in obstacles):
                return direction
        
        return snake.direction
    
    def make_decision(self, snake, food_pos):

        snake.direction = self.get_safe_direction(snake)