"""
Snake Model Module

This module defines the Snake class, which represents a snake entity in the game.
It handles snake movement, collision detection, and state management.

Classes:
    Snake: Main snake entity with movement and collision detection capabilities
    SnakeError: Base exception for snake-related errors
    InvalidPositionError: Raised when invalid position is provided
    InvalidDirectionError: Raised when invalid direction is provided

Author: Devansh Tomar
Version: 1.0.0
"""

import logging
from typing import Tuple, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

from enums import Direction
from config import GRID_WIDTH, GRID_HEIGHT

# Configure logging
logger = logging.getLogger(__name__)


class SnakeError(Exception):
    """Base exception for snake-related errors"""
    pass


class InvalidPositionError(SnakeError):
    """Raised when an invalid position is provided"""
    pass


class InvalidDirectionError(SnakeError):
    """Raised when an invalid direction is provided"""
    pass


@dataclass
class SnakeStats:
    """Statistics tracking for snake performance"""
    moves_made: int = 0
    food_eaten: int = 0
    collisions: int = 0
    time_alive: float = 0.0


class Snake:
    """
    Represents a snake in the game with movement and collision detection.
    
    The snake consists of a body (list of positions) where the first element
    is the head. The snake can move in four directions and grow when eating food.
    
    Attributes:
        body (List[Tuple[int, int]]): List of (x, y) positions forming the snake
        direction (Direction): Current movement direction
        color (Tuple[int, int, int]): RGB color for rendering
        name (str): Display name of the snake
        score (int): Current score
        alive (bool): Whether the snake is still alive
        stats (SnakeStats): Performance statistics
        
    Raises:
        InvalidPositionError: If invalid starting position is provided
        InvalidDirectionError: If invalid direction is set
    """
    
    # Class constants
    MIN_POSITION = 0
    INITIAL_SCORE = 0
    INITIAL_LENGTH = 1
    
    def __init__(self, start_pos: Tuple[int, int], 
                 color: Tuple[int, int, int], 
                 name: str) -> None:
        """
        Initialize a new snake.
        
        Args:
            start_pos: Starting position (x, y) on the grid
            color: RGB color tuple for rendering
            name: Display name for the snake
            
        Raises:
            InvalidPositionError: If start_pos is invalid
            ValueError: If color values are invalid
            TypeError: If arguments are of wrong type
        """
        try:
            # Validate inputs
            self._validate_position(start_pos)
            self._validate_color(color)
            self._validate_name(name)
            
            # Initialize snake attributes
            self.body: List[Tuple[int, int]] = [start_pos]
            self.direction: Direction = Direction.RIGHT
            self.color: Tuple[int, int, int] = color
            self.name: str = name
            self.score: int = self.INITIAL_SCORE
            self.alive: bool = True
            self.stats: SnakeStats = SnakeStats()
            
            # Store initial state for potential reset
            self._initial_position = start_pos
            self._initial_direction = Direction.RIGHT
            
            logger.debug(f"Snake '{name}' initialized at position {start_pos}")
            
        except Exception as e:
            logger.error(f"Failed to initialize snake: {e}")
            raise
    
    @staticmethod
    def _validate_position(position: Tuple[int, int]) -> None:
        """
        Validate a grid position.
        
        Args:
            position: (x, y) tuple to validate
            
        Raises:
            InvalidPositionError: If position is invalid
            TypeError: If position is not a tuple of integers
        """
        if not isinstance(position, tuple):
            raise TypeError(f"Position must be a tuple, got {type(position)}")
        
        if len(position) != 2:
            raise InvalidPositionError(f"Position must have 2 elements, got {len(position)}")
        
        x, y = position
        if not isinstance(x, int) or not isinstance(y, int):
            raise TypeError("Position coordinates must be integers")
        
        if not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT):
            raise InvalidPositionError(
                f"Position ({x}, {y}) out of bounds. "
                f"Valid range: x=[0, {GRID_WIDTH-1}], y=[0, {GRID_HEIGHT-1}]"
            )
    
    @staticmethod
    def _validate_color(color: Tuple[int, int, int]) -> None:
        """
        Validate RGB color tuple.
        
        Args:
            color: RGB color tuple to validate
            
        Raises:
            ValueError: If color values are invalid
            TypeError: If color is not a tuple of integers
        """
        if not isinstance(color, tuple):
            raise TypeError(f"Color must be a tuple, got {type(color)}")
        
        if len(color) != 3:
            raise ValueError(f"Color must have 3 elements (RGB), got {len(color)}")
        
        for i, value in enumerate(color):
            if not isinstance(value, int):
                raise TypeError(f"Color component {i} must be an integer")
            if not (0 <= value <= 255):
                raise ValueError(f"Color component {i} must be in range [0, 255], got {value}")
    
    @staticmethod
    def _validate_name(name: str) -> None:
        """
        Validate snake name.
        
        Args:
            name: Name to validate
            
        Raises:
            ValueError: If name is invalid
            TypeError: If name is not a string
        """
        if not isinstance(name, str):
            raise TypeError(f"Name must be a string, got {type(name)}")
        
        if not name or name.isspace():
            raise ValueError("Name cannot be empty or only whitespace")
        
        if len(name) > 50:
            raise ValueError(f"Name too long (max 50 characters), got {len(name)}")
    
    def get_head(self) -> Tuple[int, int]:
        """
        Get the current position of the snake's head.
        
        Returns:
            Tuple of (x, y) coordinates of the head
            
        Raises:
            RuntimeError: If snake body is empty (should never happen)
        """
        if not self.body:
            raise RuntimeError("Snake body is empty - this should never happen!")
        
        return self.body[0]
    
    def set_direction(self, new_direction: Direction) -> bool:
        """
        Safely set a new direction for the snake.
        
        Prevents the snake from moving directly backwards into itself.
        
        Args:
            new_direction: The desired new direction
            
        Returns:
            bool: True if direction was changed, False if invalid
            
        Raises:
            InvalidDirectionError: If new_direction is not a Direction enum
        """
        if not isinstance(new_direction, Direction):
            raise InvalidDirectionError(
                f"Direction must be a Direction enum, got {type(new_direction)}"
            )
        
        # Prevent moving backwards into self
        if len(self.body) > 1:
            current_dx, current_dy = self.direction.value
            new_dx, new_dy = new_direction.value
            
            # Check if new direction is opposite to current
            if (current_dx + new_dx == 0 and current_dy + new_dy == 0):
                logger.debug(f"Prevented backward movement from {self.direction} to {new_direction}")
                return False
        
        self.direction = new_direction
        return True
    
    def move(self, grow: bool = False) -> Optional[Tuple[int, int]]:
        """
        Move the snake one step in its current direction.
        
        Args:
            grow: If True, the snake grows by one segment (doesn't remove tail)
            
        Returns:
            The new head position if move was successful, None if snake is dead
            
        Raises:
            RuntimeError: If snake state is corrupted
        """
        if not self.alive:
            logger.warning(f"Attempted to move dead snake '{self.name}'")
            return None
        
        try:
            # Get current head position
            head_x, head_y = self.get_head()
            
            # Calculate new head position
            dx, dy = self.direction.value
            new_head = (head_x + dx, head_y + dy)
            
            # Add new head
            self.body.insert(0, new_head)
            
            # Remove tail if not growing
            if not grow:
                self.body.pop()
            else:
                self.stats.food_eaten += 1
                logger.debug(f"Snake '{self.name}' grew to length {len(self.body)}")
            
            # Update statistics
            self.stats.moves_made += 1
            
            return new_head
            
        except Exception as e:
            logger.error(f"Error during snake movement: {e}")
            raise RuntimeError(f"Failed to move snake: {e}")
    
    def check_wall_collision(self) -> bool:
        """
        Check if the snake's head has collided with a wall.
        
        Returns:
            bool: True if collision detected, False otherwise
        """
        try:
            head_x, head_y = self.get_head()
            collision = (head_x < 0 or head_x >= GRID_WIDTH or 
                        head_y < 0 or head_y >= GRID_HEIGHT)
            
            if collision:
                self.stats.collisions += 1
                logger.info(f"Snake '{self.name}' hit wall at ({head_x}, {head_y})")
            
            return collision
            
        except Exception as e:
            logger.error(f"Error checking wall collision: {e}")
            # In case of error, consider it a collision for safety
            return True
    
    def check_self_collision(self) -> bool:
        """
        Check if the snake's head has collided with its own body.
        
        Returns:
            bool: True if self-collision detected, False otherwise
        """
        try:
            if len(self.body) < 4:  # Snake too short to collide with itself
                return False
            
            head = self.get_head()
            # Check if head position exists in the rest of the body
            collision = head in self.body[1:]
            
            if collision:
                self.stats.collisions += 1
                logger.info(f"Snake '{self.name}' collided with itself at {head}")
            
            return collision
            
        except Exception as e:
            logger.error(f"Error checking self collision: {e}")
            # In case of error, consider it a collision for safety
            return True
    
    def check_collision_with_snake(self, other_snake: 'Snake') -> bool:
        """
        Check if this snake's head has collided with another snake's body.
        
        Args:
            other_snake: The other snake to check collision against
            
        Returns:
            bool: True if collision detected, False otherwise
            
        Raises:
            TypeError: If other_snake is not a Snake instance
        """
        if not isinstance(other_snake, Snake):
            raise TypeError(f"Expected Snake instance, got {type(other_snake)}")
        
        try:
            # Dead snakes don't collide
            if not self.alive or not other_snake.alive:
                return False
            
            head = self.get_head()
            collision = head in other_snake.body
            
            if collision:
                self.stats.collisions += 1
                logger.info(
                    f"Snake '{self.name}' collided with '{other_snake.name}' at {head}"
                )
            
            return collision
            
        except Exception as e:
            logger.error(f"Error checking collision with other snake: {e}")
            # In case of error, consider it a collision for safety
            return True
    
    def get_length(self) -> int:
        """
        Get the current length of the snake.
        
        Returns:
            int: Number of body segments
        """
        return len(self.body)
    
    def get_tail(self) -> Optional[Tuple[int, int]]:
        """
        Get the position of the snake's tail.
        
        Returns:
            Tuple of (x, y) coordinates of the tail, or None if body is empty
        """
        if not self.body:
            return None
        return self.body[-1]
    
    def reset(self) -> None:
        """
        Reset the snake to its initial state.
        
        Useful for restarting the game without creating new instances.
        """
        try:
            self.body = [self._initial_position]
            self.direction = self._initial_direction
            self.score = self.INITIAL_SCORE
            self.alive = True
            self.stats = SnakeStats()
            
            logger.info(f"Snake '{self.name}' reset to initial state")
            
        except Exception as e:
            logger.error(f"Error resetting snake: {e}")
            raise RuntimeError(f"Failed to reset snake: {e}")
    
    def __str__(self) -> str:
        """String representation of the snake."""
        return (f"Snake(name='{self.name}', alive={self.alive}, "
                f"length={len(self.body)}, score={self.score})")
    
    def __repr__(self) -> str:
        """Detailed representation of the snake."""
        return (f"Snake(name='{self.name}', start_pos={self._initial_position}, "
                f"color={self.color}, alive={self.alive}, length={len(self.body)}, "
                f"score={self.score}, direction={self.direction})")