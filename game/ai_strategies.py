from game.ai_controller import AIController
from utils.pathfinding import (
    calculate_distance, get_all_obstacles, 
    bfs_pathfind, get_direction_to_target
)
from config import GRID_WIDTH, GRID_HEIGHT
from enums import Direction

class BalancedAI(AIController):
    
    def make_decision(self, snake, food_pos):
        if not snake.alive:
            return
            
        head = snake.get_head()
        

        my_distance_to_food = calculate_distance(head, food_pos)
        other_snake = self.snake2 if snake == self.snake1 else self.snake1
        other_distance_to_food = calculate_distance(other_snake.get_head(), food_pos)
        

        path_to_food = bfs_pathfind(head, food_pos, self.snake1, self.snake2, snake)
        
        if path_to_food and len(path_to_food) <= my_distance_to_food + 2:

            next_pos = path_to_food[0]
            snake.direction = get_direction_to_target(head, next_pos)
        else:

            if other_distance_to_food < my_distance_to_food and other_distance_to_food <= 3:

                safe_dir = self.get_safe_direction(snake)
                snake.direction = safe_dir
            else:

                food_direction = get_direction_to_target(head, food_pos)
                

                dx, dy = food_direction.value
                new_x, new_y = head[0] + dx, head[1] + dy
                obstacles = get_all_obstacles(self.snake1, self.snake2, snake)
                
                if (0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT and
                    (new_x, new_y) not in obstacles):
                    snake.direction = food_direction
                else:
                    snake.direction = self.get_safe_direction(snake)


class AggressiveAI(AIController):
    
    def make_decision(self, snake, food_pos):
        if not snake.alive:
            return
            
        head = snake.get_head()
        other_snake = self.snake2 if snake == self.snake1 else self.snake1
        

        my_distance_to_food = calculate_distance(head, food_pos)
        other_distance_to_food = calculate_distance(other_snake.get_head(), food_pos)
        

        path_to_food = bfs_pathfind(head, food_pos, self.snake1, self.snake2, snake)
        

        if other_snake.alive and other_distance_to_food <= 5:

            opponent_head = other_snake.get_head()
            

            mid_x = (opponent_head[0] + food_pos[0]) // 2
            mid_y = (opponent_head[1] + food_pos[1]) // 2
            blocking_pos = (mid_x, mid_y)
            

            path_to_block = bfs_pathfind(head, blocking_pos, self.snake1, self.snake2, snake)
            
            if path_to_block and len(path_to_block) < other_distance_to_food:

                next_pos = path_to_block[0]
                snake.direction = get_direction_to_target(head, next_pos)
                return
        

        if path_to_food:

            next_pos = path_to_food[0]
            snake.direction = get_direction_to_target(head, next_pos)
        else:

            food_direction = get_direction_to_target(head, food_pos)
            dx, dy = food_direction.value
            new_x, new_y = head[0] + dx, head[1] + dy
            

            if (0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT):

                if other_snake.alive and (new_x, new_y) == other_snake.get_head():
                    snake.direction = self.get_safe_direction(snake)
                else:
                    snake.direction = food_direction
            else:
                snake.direction = self.get_safe_direction(snake)


class DefensiveAI(AIController):
    
    def make_decision(self, snake, food_pos):
        if not snake.alive:
            return
            
        head = snake.get_head()
        other_snake = self.snake2 if snake == self.snake1 else self.snake1
        

        obstacles = get_all_obstacles(self.snake1, self.snake2, snake)
        

        safe_directions = []
        for direction in Direction:
            dx, dy = direction.value
            new_x, new_y = head[0] + dx, head[1] + dy
            

            if (0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT and
                (new_x, new_y) not in obstacles):
                safe_directions.append(direction)
        

        if not safe_directions:
            snake.direction = self.get_safe_direction(snake)
            return
        
        path_to_food = bfs_pathfind(head, food_pos, self.snake1, self.snake2, snake)
        

        if path_to_food and len(path_to_food) > 0:

            path_is_safe = True
            if other_snake.alive:
                opponent_head = other_snake.get_head()

                for pos in path_to_food[:min(3, len(path_to_food))]:
                    if calculate_distance(pos, opponent_head) < 2:
                        path_is_safe = False
                        break
            
            if path_is_safe:
                next_pos = path_to_food[0]
                next_dir = get_direction_to_target(head, next_pos)

                if next_dir in safe_directions:
                    snake.direction = next_dir
                    return
        

        best_direction = None
        max_safety_score = -1
        
        for direction in safe_directions:
            dx, dy = direction.value
            new_x, new_y = head[0] + dx, head[1] + dy
            

            safety_score = 0
            

            wall_distance = min(new_x, new_y, GRID_WIDTH - new_x - 1, GRID_HEIGHT - new_y - 1)
            safety_score += wall_distance * 2
            

            if other_snake.alive:
                opponent_distance = calculate_distance((new_x, new_y), other_snake.get_head())
                safety_score += opponent_distance * 3
            

            escape_routes = 0
            for esc_dir in Direction:
                esc_dx, esc_dy = esc_dir.value
                esc_x, esc_y = new_x + esc_dx, new_y + esc_dy
                if (0 <= esc_x < GRID_WIDTH and 0 <= esc_y < GRID_HEIGHT and
                    (esc_x, esc_y) not in obstacles):
                    escape_routes += 1
            safety_score += escape_routes * 2
            

            food_distance = calculate_distance((new_x, new_y), food_pos)
            safety_score += (GRID_WIDTH + GRID_HEIGHT - food_distance) * 0.1
            
            if safety_score > max_safety_score:
                max_safety_score = safety_score
                best_direction = direction
        

        if best_direction:
            snake.direction = best_direction
        else:

            snake.direction = safe_directions[0] if safe_directions else snake.direction