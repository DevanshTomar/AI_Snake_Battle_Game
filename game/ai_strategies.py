"""
AI Strategies Module

This module contains different AI strategy implementations for snake behavior:
- BalancedAI: Balanced approach between food pursuit and safety
- AggressiveAI: Prioritizes blocking opponent and taking risks
- DefensiveAI: Prioritizes survival and avoiding risks

Author: Devansh Tomar
Version: 1.0.0
"""

import logging
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass

from game.ai_controller import AIController, AIError
from utils.pathfinding import (
    calculate_distance, get_all_obstacles, 
    bfs_pathfind, get_direction_to_target
)
from config import GRID_WIDTH, GRID_HEIGHT
from enums import Direction
from models.snake import Snake

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class DecisionMetrics:
    """Metrics for AI decision making"""
    my_distance_to_food: int
    opponent_distance_to_food: int
    path_length: int
    is_path_safe: bool
    blocking_opportunity: bool


class BalancedAI(AIController):
    """
    Balanced AI Strategy
    
    This AI maintains a balance between aggressive food pursuit and safe play.
    It will pursue food when it has a clear advantage or safe path, but will
    prioritize survival when the opponent is closer to food.
    
    Decision Priority:
    1. Follow safe path to food if available
    2. Avoid opponent if they're closer to food
    3. Move toward food directly if safe
    4. Take any safe direction if no food path
    """
    
    # Strategy constants
    PATH_TOLERANCE = 2  # Accept paths up to this much longer than Manhattan distance
    BLOCKING_DISTANCE = 3  # Consider blocking when opponent is this close to food
    
    def make_decision(self, snake: Snake, food_pos: Tuple[int, int]) -> None:
        """
        Make a balanced decision for snake movement.
        
        Args:
            snake: The snake to control
            food_pos: Current food position
        """
        try:
            # Validate inputs
            if not snake or not snake.alive:
                logger.debug(f"Snake {snake.name if snake else 'None'} is not alive")
                return
            
            if not self.validate_food_position(food_pos):
                logger.error(f"Invalid food position: {food_pos}")
                snake.direction = self.get_safe_direction(snake)
                return
            
            # Get current state
            head = snake.get_head()
            other_snake = self.get_other_snake(snake)
            
            if not other_snake:
                logger.error("Could not find other snake reference")
                snake.direction = self.get_safe_direction(snake)
                return
            
            # Calculate metrics for decision making
            metrics = self._calculate_decision_metrics(snake, other_snake, head, food_pos)
            
            # Make decision based on metrics
            self._execute_decision(snake, head, food_pos, metrics)
            
        except Exception as e:
            logger.error(f"Error in BalancedAI.make_decision: {e}")
            # Fall back to safe movement
            snake.direction = self.get_safe_direction(snake)
    
    def _calculate_decision_metrics(self, snake: Snake, other_snake: Snake,
                                  head: Tuple[int, int], food_pos: Tuple[int, int]) -> DecisionMetrics:
        """Calculate metrics for decision making"""
        my_distance = calculate_distance(head, food_pos)
        opponent_distance = calculate_distance(other_snake.get_head(), food_pos) if other_snake.alive else float('inf')
        
        # Find path to food
        path_to_food = bfs_pathfind(head, food_pos, self.snake1, self.snake2, snake)
        path_length = len(path_to_food) if path_to_food else float('inf')
        
        # Check if path is reasonably efficient
        is_path_safe = bool(path_to_food) and path_length <= my_distance + self.PATH_TOLERANCE
        
        # Check for blocking opportunity
        blocking_opportunity = (other_snake.alive and 
                              opponent_distance < my_distance and 
                              opponent_distance <= self.BLOCKING_DISTANCE)
        
        return DecisionMetrics(
            my_distance_to_food=my_distance,
            opponent_distance_to_food=opponent_distance,
            path_length=path_length,
            is_path_safe=is_path_safe,
            blocking_opportunity=blocking_opportunity
        )
    
    def _execute_decision(self, snake: Snake, head: Tuple[int, int], 
                         food_pos: Tuple[int, int], metrics: DecisionMetrics) -> None:
        """Execute decision based on calculated metrics"""
        
        # Priority 1: Follow safe path to food
        if metrics.is_path_safe:
            path = bfs_pathfind(head, food_pos, self.snake1, self.snake2, snake)
            if path:
                next_pos = path[0]
                snake.direction = get_direction_to_target(head, next_pos)
                logger.debug(f"{snake.name} following safe path to food")
                return
        
        # Priority 2: Defensive play if opponent is closer
        if metrics.blocking_opportunity:
            safe_dir = self.get_safe_direction(snake)
            snake.direction = safe_dir
            logger.debug(f"{snake.name} playing defensively, opponent closer to food")
            return
        
        # Priority 3: Direct movement toward food if safe
        food_direction = get_direction_to_target(head, food_pos)
        if self._is_direction_safe(snake, food_direction):
            snake.direction = food_direction
            logger.debug(f"{snake.name} moving directly toward food")
            return
        
        # Priority 4: Any safe direction
        snake.direction = self.get_safe_direction(snake)
        logger.debug(f"{snake.name} taking safe direction")
    
    def _is_direction_safe(self, snake: Snake, direction: Direction) -> bool:
        """Check if moving in a direction is safe"""
        try:
            head = snake.get_head()
            dx, dy = direction.value
            new_x, new_y = head[0] + dx, head[1] + dy
            
            # Check bounds
            if not (0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT):
                return False
            
            # Check obstacles
            obstacles = get_all_obstacles(self.snake1, self.snake2, snake)
            return (new_x, new_y) not in obstacles
            
        except Exception:
            return False


class AggressiveAI(AIController):
    """
    Aggressive AI Strategy
    
    This AI actively tries to block opponents and takes calculated risks
    to gain competitive advantage. It prioritizes cutting off opponent's
    path to food and will take direct routes even without clear paths.
    
    Decision Priority:
    1. Block opponent's path to food when possible
    2. Take direct path to food if available
    3. Move aggressively toward food even without clear path
    4. Avoid head-on collisions as last resort
    """
    
    # Strategy constants
    BLOCKING_RANGE = 5  # Consider blocking when opponent is within this distance
    BLOCKING_EFFICIENCY = 0.8  # Block if we can reach blocking point this much faster
    
    def make_decision(self, snake: Snake, food_pos: Tuple[int, int]) -> None:
        """
        Make an aggressive decision for snake movement.
        
        Args:
            snake: The snake to control
            food_pos: Current food position
        """
        try:
            # Validate inputs
            if not snake or not snake.alive:
                return
            
            if not self.validate_food_position(food_pos):
                logger.error(f"Invalid food position: {food_pos}")
                snake.direction = self.get_safe_direction(snake)
                return
            
            # Get current state
            head = snake.get_head()
            other_snake = self.get_other_snake(snake)
            
            if not other_snake:
                snake.direction = self.get_safe_direction(snake)
                return
            
            # Try blocking strategy first
            if self._attempt_blocking_strategy(snake, other_snake, head, food_pos):
                return
            
            # Try direct path to food
            if self._attempt_direct_path(snake, head, food_pos):
                return
            
            # Aggressive movement toward food
            self._aggressive_food_pursuit(snake, head, food_pos, other_snake)
            
        except Exception as e:
            logger.error(f"Error in AggressiveAI.make_decision: {e}")
            snake.direction = self.get_safe_direction(snake)
    
    def _attempt_blocking_strategy(self, snake: Snake, other_snake: Snake,
                                  head: Tuple[int, int], food_pos: Tuple[int, int]) -> bool:
        """
        Attempt to block opponent's path to food.
        
        Returns:
            bool: True if blocking move was made, False otherwise
        """
        if not other_snake.alive:
            return False
        
        # Calculate distances
        my_distance = calculate_distance(head, food_pos)
        opponent_distance = calculate_distance(other_snake.get_head(), food_pos)
        
        # Only consider blocking if opponent is close to food
        if opponent_distance > self.BLOCKING_RANGE:
            return False
        
        # Calculate optimal blocking position
        blocking_pos = self._calculate_blocking_position(other_snake.get_head(), food_pos)
        
        if not blocking_pos:
            return False
        
        # Check if we can reach blocking position effectively
        path_to_block = bfs_pathfind(head, blocking_pos, self.snake1, self.snake2, snake)
        
        if path_to_block and len(path_to_block) < opponent_distance * self.BLOCKING_EFFICIENCY:
            next_pos = path_to_block[0]
            snake.direction = get_direction_to_target(head, next_pos)
            logger.debug(f"{snake.name} attempting to block opponent")
            return True
        
        return False
    
    def _calculate_blocking_position(self, opponent_head: Tuple[int, int], 
                                   food_pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Calculate optimal position to block opponent's path to food"""
        # Find midpoint between opponent and food
        mid_x = (opponent_head[0] + food_pos[0]) // 2
        mid_y = (opponent_head[1] + food_pos[1]) // 2
        
        # Validate blocking position
        if 0 <= mid_x < GRID_WIDTH and 0 <= mid_y < GRID_HEIGHT:
            return (mid_x, mid_y)
        
        # Try positions adjacent to food
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            block_x, block_y = food_pos[0] + dx, food_pos[1] + dy
            if 0 <= block_x < GRID_WIDTH and 0 <= block_y < GRID_HEIGHT:
                return (block_x, block_y)
        
        return None
    
    def _attempt_direct_path(self, snake: Snake, head: Tuple[int, int], 
                           food_pos: Tuple[int, int]) -> bool:
        """
        Attempt to take direct path to food.
        
        Returns:
            bool: True if direct path was taken, False otherwise
        """
        path_to_food = bfs_pathfind(head, food_pos, self.snake1, self.snake2, snake)
        
        if path_to_food:
            next_pos = path_to_food[0]
            snake.direction = get_direction_to_target(head, next_pos)
            logger.debug(f"{snake.name} taking direct path to food")
            return True
        
        return False
    
    def _aggressive_food_pursuit(self, snake: Snake, head: Tuple[int, int],
                               food_pos: Tuple[int, int], other_snake: Snake) -> None:
        """Pursue food aggressively even without clear path"""
        food_direction = get_direction_to_target(head, food_pos)
        dx, dy = food_direction.value
        new_x, new_y = head[0] + dx, head[1] + dy
        
        # Check basic validity
        if 0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT:
            # Special check for head-on collision
            if other_snake.alive and (new_x, new_y) == other_snake.get_head():
                # Avoid certain death from head-on collision
                snake.direction = self.get_safe_direction(snake)
                logger.debug(f"{snake.name} avoiding head-on collision")
            else:
                # Take the aggressive move
                snake.direction = food_direction
                logger.debug(f"{snake.name} aggressively pursuing food")
        else:
            # Out of bounds, take safe direction
            snake.direction = self.get_safe_direction(snake)


class DefensiveAI(AIController):
    """
    Defensive AI Strategy
    
    This AI prioritizes survival above all else. It carefully evaluates
    each move for safety, maintains distance from opponents and walls,
    and only pursues food when the path is completely safe.
    
    Decision Priority:
    1. Ensure multiple escape routes
    2. Maintain distance from walls and opponent
    3. Only pursue food with safe, verified paths
    4. Choose positions with maximum safety score
    """
    
    # Strategy constants
    MIN_WALL_DISTANCE = 2  # Preferred minimum distance from walls
    MIN_OPPONENT_DISTANCE = 3  # Preferred minimum distance from opponent
    PATH_SAFETY_CHECK = 3  # Check this many moves ahead for path safety
    
    # Scoring weights
    WALL_DISTANCE_WEIGHT = 2.0
    OPPONENT_DISTANCE_WEIGHT = 3.0
    ESCAPE_ROUTES_WEIGHT = 2.0
    FOOD_DISTANCE_WEIGHT = 0.1
    
    def make_decision(self, snake: Snake, food_pos: Tuple[int, int]) -> None:
        """
        Make a defensive decision for snake movement.
        
        Args:
            snake: The snake to control
            food_pos: Current food position
        """
        try:
            # Validate inputs
            if not snake or not snake.alive:
                return
            
            if not self.validate_food_position(food_pos):
                logger.error(f"Invalid food position: {food_pos}")
                snake.direction = self.get_safe_direction(snake)
                return
            
            # Get current state
            head = snake.get_head()
            other_snake = self.get_other_snake(snake)
            
            # Find all safe directions
            safe_directions = self._find_safe_directions(snake, head)
            
            if not safe_directions:
                # No safe directions - take any direction as last resort
                snake.direction = self.get_safe_direction(snake)
                logger.warning(f"{snake.name} has no safe directions")
                return
            
            # Try safe path to food first
            if self._attempt_safe_food_path(snake, head, food_pos, safe_directions, other_snake):
                return
            
            # Choose safest direction based on scoring
            best_direction = self._choose_safest_direction(snake, head, food_pos, 
                                                          safe_directions, other_snake)
            snake.direction = best_direction
            
        except Exception as e:
            logger.error(f"Error in DefensiveAI.make_decision: {e}")
            snake.direction = self.get_safe_direction(snake)
    
    def _find_safe_directions(self, snake: Snake, head: Tuple[int, int]) -> List[Direction]:
        """Find all directions that don't lead to immediate collision"""
        obstacles = get_all_obstacles(self.snake1, self.snake2, snake)
        safe_directions = []
        
        for direction in Direction:
            dx, dy = direction.value
            new_x, new_y = head[0] + dx, head[1] + dy
            
            # Check bounds and obstacles
            if (0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT and
                (new_x, new_y) not in obstacles):
                safe_directions.append(direction)
        
        return safe_directions
    
    def _attempt_safe_food_path(self, snake: Snake, head: Tuple[int, int],
                               food_pos: Tuple[int, int], safe_directions: List[Direction],
                               other_snake: Optional[Snake]) -> bool:
        """
        Attempt to follow a safe path to food.
        
        Returns:
            bool: True if safe path was taken, False otherwise
        """
        path_to_food = bfs_pathfind(head, food_pos, self.snake1, self.snake2, snake)
        
        if not path_to_food:
            return False
        
        # Verify path safety
        if not self._is_path_safe(path_to_food, other_snake):
            return False
        
        # Check if first move is in safe directions
        next_pos = path_to_food[0]
        next_dir = get_direction_to_target(head, next_pos)
        
        if next_dir in safe_directions:
            snake.direction = next_dir
            logger.debug(f"{snake.name} following safe path to food")
            return True
        
        return False
    
    def _is_path_safe(self, path: List[Tuple[int, int]], 
                     other_snake: Optional[Snake]) -> bool:
        """Check if a path is safe from opponent interference"""
        if not other_snake or not other_snake.alive:
            return True
        
        opponent_head = other_snake.get_head()
        
        # Check first few positions in path
        for i, pos in enumerate(path[:min(self.PATH_SAFETY_CHECK, len(path))]):
            # Check distance from opponent
            if calculate_distance(pos, opponent_head) < self.MIN_OPPONENT_DISTANCE - i:
                return False
        
        return True
    
    def _choose_safest_direction(self, snake: Snake, head: Tuple[int, int],
                               food_pos: Tuple[int, int], safe_directions: List[Direction],
                               other_snake: Optional[Snake]) -> Direction:
        """Choose the safest direction based on multiple factors"""
        best_direction = safe_directions[0]
        max_safety_score = float('-inf')
        
        obstacles = get_all_obstacles(self.snake1, self.snake2, snake)
        
        for direction in safe_directions:
            dx, dy = direction.value
            new_x, new_y = head[0] + dx, head[1] + dy
            
            # Calculate safety score
            safety_score = self._calculate_safety_score(
                (new_x, new_y), food_pos, obstacles, other_snake
            )
            
            logger.debug(f"{snake.name} - Direction {direction}: safety score = {safety_score:.2f}")
            
            if safety_score > max_safety_score:
                max_safety_score = safety_score
                best_direction = direction
        
        logger.debug(f"{snake.name} chose {best_direction} with score {max_safety_score:.2f}")
        return best_direction
    
    def _calculate_safety_score(self, position: Tuple[int, int], food_pos: Tuple[int, int],
                               obstacles: set, other_snake: Optional[Snake]) -> float:
        """Calculate safety score for a position"""
        x, y = position
        score = 0.0
        
        # Factor 1: Distance from walls
        wall_distance = min(x, y, GRID_WIDTH - x - 1, GRID_HEIGHT - y - 1)
        score += wall_distance * self.WALL_DISTANCE_WEIGHT
        
        # Factor 2: Distance from opponent
        if other_snake and other_snake.alive:
            opponent_distance = calculate_distance(position, other_snake.get_head())
            score += opponent_distance * self.OPPONENT_DISTANCE_WEIGHT
        
        # Factor 3: Number of escape routes
        escape_routes = self._count_escape_routes(position, obstacles)
        score += escape_routes * self.ESCAPE_ROUTES_WEIGHT
        
        # Factor 4: Distance to food (small weight)
        food_distance = calculate_distance(position, food_pos)
        max_distance = GRID_WIDTH + GRID_HEIGHT
        score += (max_distance - food_distance) * self.FOOD_DISTANCE_WEIGHT
        
        return score
    
    def _count_escape_routes(self, position: Tuple[int, int], obstacles: set) -> int:
        """Count available escape routes from a position"""
        x, y = position
        escape_count = 0
        
        for direction in Direction:
            dx, dy = direction.value
            new_x, new_y = x + dx, y + dy
            
            if (0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT and
                (new_x, new_y) not in obstacles):
                escape_count += 1
        
        return escape_count