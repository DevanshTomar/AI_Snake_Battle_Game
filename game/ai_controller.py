"""
AI Controller Module

Base AI controller class that provides fundamental snake control logic
and safety mechanisms for AI decision making.

Classes:
    AIController: Base class for AI snake control
    AIError: Base exception for AI-related errors

Author: Devansh Tomar
Version: 1.0.0
"""

import logging
from typing import Optional, Tuple, Set
from abc import ABC, abstractmethod

from enums import Direction
from config import GRID_WIDTH, GRID_HEIGHT
from utils.pathfinding import (
    bfs_pathfind, get_direction_to_target, 
    calculate_distance, get_all_obstacles
)
from models.snake import Snake

# Configure logging
logger = logging.getLogger(__name__)


class AIError(Exception):
    """Base exception for AI-related errors"""
    pass


class AIController(ABC):
    """
    Base AI Controller for snake movement decisions.
    
    This abstract base class provides common functionality for all AI strategies
    including safe direction finding and basic decision making framework.
    
    Attributes:
        snake1 (Snake): Reference to the first snake
        snake2 (Snake): Reference to the second snake
        
    Methods:
        get_safe_direction: Find a safe direction that avoids immediate collision
        make_decision: Abstract method to be implemented by subclasses
    """
    
    def __init__(self, snake1: Snake, snake2: Snake) -> None:
        """
        Initialize the AI controller with references to both snakes.
        
        Args:
            snake1: First snake in the game
            snake2: Second snake in the game
            
        Raises:
            TypeError: If snakes are not Snake instances
            ValueError: If snakes are None
        """
        # Validate inputs
        if snake1 is None or snake2 is None:
            raise ValueError("Both snake references must be provided")
        
        if not isinstance(snake1, Snake) or not isinstance(snake2, Snake):
            raise TypeError("Both arguments must be Snake instances")
        
        self.snake1 = snake1
        self.snake2 = snake2
        
        # Cache for performance optimization
        self._last_safe_directions: dict = {}
        
        logger.debug(f"AIController initialized for {snake1.name} and {snake2.name}")
    
    def get_safe_direction(self, snake: Snake) -> Direction:
        """
        Find a safe direction for the snake to move that avoids immediate collision.
        
        This method checks all four directions and returns the first safe one found.
        If no safe direction exists, it returns the current direction (snake will die).
        
        Args:
            snake: The snake to find a safe direction for
            
        Returns:
            Direction: A safe direction to move, or current direction if none found
            
        Raises:
            AIError: If snake reference is invalid
        """
        try:
            # Validate snake
            if not isinstance(snake, Snake):
                raise AIError(f"Invalid snake reference: {type(snake)}")
            
            if not snake.alive:
                logger.warning(f"Getting safe direction for dead snake {snake.name}")
                return snake.direction
            
            # Get current position
            try:
                head_x, head_y = snake.get_head()
            except Exception as e:
                logger.error(f"Failed to get snake head position: {e}")
                return snake.direction
            
            # Get all obstacles (both snakes' bodies minus requesting snake's tail)
            try:
                obstacles = get_all_obstacles(self.snake1, self.snake2, snake)
            except Exception as e:
                logger.error(f"Failed to get obstacles: {e}")
                obstacles = set()
            
            # Store valid directions for debugging
            valid_directions = []
            
            # Check each direction in order of preference
            # Prioritize: current direction, perpendicular directions, opposite direction
            directions_to_check = self._get_prioritized_directions(snake.direction)
            
            for direction in directions_to_check:
                dx, dy = direction.value
                new_x, new_y = head_x + dx, head_y + dy
                
                # Check if the new position is safe
                if self._is_position_safe(new_x, new_y, obstacles):
                    valid_directions.append(direction)
                    
                    # Return the first safe direction found
                    logger.debug(f"Safe direction found for {snake.name}: {direction}")
                    return direction
            
            # No safe direction found - snake is trapped
            logger.warning(f"No safe direction for {snake.name} at ({head_x}, {head_y})")
            logger.debug(f"Obstacles near snake: {self._get_nearby_obstacles(head_x, head_y, obstacles)}")
            
            # Return current direction as last resort
            return snake.direction
            
        except Exception as e:
            logger.error(f"Error in get_safe_direction: {e}")
            # Return current direction on any error
            return snake.direction if snake else Direction.RIGHT
    
    def _get_prioritized_directions(self, current_direction: Direction) -> list:
        """
        Get directions in order of preference based on current direction.
        
        Args:
            current_direction: The snake's current direction
            
        Returns:
            List of directions ordered by preference
        """
        # Create a priority order: current, perpendicular, opposite
        all_directions = list(Direction)
        
        # Remove current direction to add it first
        all_directions.remove(current_direction)
        
        # Get opposite direction
        dx, dy = current_direction.value
        opposite = None
        for d in Direction:
            if d.value == (-dx, -dy):
                opposite = d
                break
        
        # Build priority list
        priority_dirs = [current_direction]
        
        # Add perpendicular directions
        for d in all_directions:
            if d != opposite:
                priority_dirs.append(d)
        
        # Add opposite direction last
        if opposite:
            priority_dirs.append(opposite)
        
        return priority_dirs
    
    def _is_position_safe(self, x: int, y: int, obstacles: Set[Tuple[int, int]]) -> bool:
        """
        Check if a position is safe (within bounds and not occupied).
        
        Args:
            x: X coordinate to check
            y: Y coordinate to check
            obstacles: Set of positions that are occupied
            
        Returns:
            bool: True if position is safe, False otherwise
        """
        # Check bounds
        if not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT):
            return False
        
        # Check obstacles
        if (x, y) in obstacles:
            return False
        
        return True
    
    def _get_nearby_obstacles(self, x: int, y: int, obstacles: Set[Tuple[int, int]], 
                            radius: int = 2) -> Set[Tuple[int, int]]:
        """
        Get obstacles within a certain radius of a position (for debugging).
        
        Args:
            x: Center X coordinate
            y: Center Y coordinate
            obstacles: All obstacles
            radius: Search radius
            
        Returns:
            Set of nearby obstacle positions
        """
        nearby = set()
        for ox, oy in obstacles:
            if abs(ox - x) <= radius and abs(oy - y) <= radius:
                nearby.add((ox, oy))
        return nearby
    
    @abstractmethod
    def make_decision(self, snake: Snake, food_pos: Tuple[int, int]) -> None:
        """
        Make a movement decision for the snake based on game state.
        
        This method should be implemented by subclasses to define specific
        AI behavior strategies.
        
        Args:
            snake: The snake to make a decision for
            food_pos: Current position of the food
            
        Note:
            This method should update snake.direction directly
        """
        pass
    
    def validate_food_position(self, food_pos: Tuple[int, int]) -> bool:
        """
        Validate that food position is valid.
        
        Args:
            food_pos: Position to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not isinstance(food_pos, tuple) or len(food_pos) != 2:
            return False
        
        x, y = food_pos
        if not isinstance(x, int) or not isinstance(y, int):
            return False
        
        return 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT
    
    def get_other_snake(self, snake: Snake) -> Optional[Snake]:
        """
        Get reference to the other snake.
        
        Args:
            snake: The current snake
            
        Returns:
            The other snake, or None if not found
        """
        if snake == self.snake1:
            return self.snake2
        elif snake == self.snake2:
            return self.snake1
        else:
            logger.error(f"Unknown snake reference: {snake}")
            return None