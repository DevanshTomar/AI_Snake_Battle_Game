from collections import deque
from enums import Direction
from config import GRID_WIDTH, GRID_HEIGHT

def get_all_obstacles(snake1, snake2, requesting_snake):
    obstacles = set()
    
    if requesting_snake == snake1:
        obstacles.update(snake1.body[:-1])
        obstacles.update(snake2.body)
    else:
        obstacles.update(snake2.body[:-1])
        obstacles.update(snake1.body)
    
    return obstacles

def get_valid_neighbors(pos, snake1, snake2, requesting_snake):
    x, y = pos
    neighbors = []
    obstacles = get_all_obstacles(snake1, snake2, requesting_snake)
    
    for direction in Direction:
        dx, dy = direction.value
        new_x, new_y = x + dx, y + dy
        

        if 0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT:

            if (new_x, new_y) not in obstacles:
                neighbors.append((new_x, new_y))
    
    return neighbors

def bfs_pathfind(start, target, snake1, snake2, requesting_snake):
    if start == target:
        return []
    
    queue = deque([(start, [])])
    visited = {start}
    
    while queue:
        current_pos, path = queue.popleft()
        
        for neighbor in get_valid_neighbors(current_pos, snake1, snake2, requesting_snake):
            if neighbor == target:
                return path + [neighbor]
            
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    
    return []

def get_direction_to_target(current_pos, target_pos):
    curr_x, curr_y = current_pos
    target_x, target_y = target_pos
    
    dx = target_x - curr_x
    dy = target_y - curr_y
    
    if dx > 0:
        return Direction.RIGHT
    elif dx < 0:
        return Direction.LEFT
    elif dy > 0:
        return Direction.DOWN
    else:
        return Direction.UP

def calculate_distance(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])