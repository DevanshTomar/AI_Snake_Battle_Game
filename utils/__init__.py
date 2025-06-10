"""
Utils Package for AI Snake Battle

This package contains utility functions and algorithms including:
- Pathfinding algorithms (BFS)
- Distance calculations
- Obstacle detection
- Direction utilities

Author: Devansh Tomar
Version: 1.0.0
"""

from .pathfinding import (
    bfs_pathfind,
    a_star_pathfind,
    get_direction_to_target,
    calculate_distance,
    calculate_euclidean_distance,
    get_all_obstacles,
    get_valid_neighbors,
    is_position_valid,
    find_safe_positions,
    PathfindingError,
    NoPathFoundError,
    InvalidPositionError
)

__all__ = [
    # Pathfinding functions
    'bfs_pathfind',
    'a_star_pathfind',
    'get_direction_to_target',
    
    # Distance functions
    'calculate_distance',
    'calculate_euclidean_distance',
    
    # Obstacle and validation functions
    'get_all_obstacles',
    'get_valid_neighbors',
    'is_position_valid',
    'find_safe_positions',
    
    # Exceptions
    'PathfindingError',
    'NoPathFoundError',
    'InvalidPositionError'
]

__version__ = '1.0.0'