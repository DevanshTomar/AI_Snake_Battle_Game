"""
Models Package for AI Snake Battle Game

This package contains all model classes used in the game.
Currently includes:
- Snake: The main snake entity with movement, collision detection, and state management

Author: Devansh Tomar
Version: 1.0.0
"""

from .snake import Snake, SnakeError, InvalidPositionError, InvalidDirectionError

__all__ = ['Snake', 'SnakeError', 'InvalidPositionError', 'InvalidDirectionError']
__version__ = '1.0.0'