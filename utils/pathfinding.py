"""
Pathfinding Utilities Module

This module provides pathfinding algorithms and utilities for the AI Snake Battle game.
It includes BFS and A* pathfinding, obstacle detection, direction calculation,
and various helper functions for navigation.

Classes:
    PathfindingError: Base exception for pathfinding errors
    NoPathFoundError: Raised when no path exists
    InvalidPositionError: Raised for invalid positions

Functions:
    bfs_pathfind: Breadth-first search pathfinding
    a_star_pathfind: A* pathfinding algorithm
    get_all_obstacles: Get all obstacle positions
    get_valid_neighbors: Get valid neighboring positions
    get_direction_to_target: Calculate direction to move
    calculate_distance: Manhattan distance calculation
    calculate_euclidean_distance: Euclidean distance calculation
    is_position_valid: Check if position is valid
    find_safe_positions: Find all safe positions on grid

Author: Devansh Tomar
Version: 1.0.0
"""

import logging
from collections import deque
from typing import Tuple, List, Set, Optional, Dict
from dataclasses import dataclass
import heapq
import math

from enums import Direction
from config import GRID_WIDTH, GRID_HEIGHT
from models.snake import Snake

# Configure logging
logger = logging.getLogger(__name__)


# Custom Exceptions
class PathfindingError(Exception):
    """Base exception for pathfinding-related errors"""
    pass


class NoPathFoundError(PathfindingError):
    """Raised when no path can be found between two points"""
    pass


class InvalidPositionError(PathfindingError):
    """Raised when an invalid position is provided"""
    pass


@dataclass
class PathNode:
    """Node for pathfinding algorithms"""
    position: Tuple[int, int]
    g_cost: float = 0  # Cost from start
    h_cost: float = 0  # Heuristic cost to goal
    f_cost: float = 0  # Total cost (g + h)
    parent: Optional['PathNode'] = None
    
    def __lt__(self, other):
        """For heap comparison"""
        return self.f_cost < other.f_cost


def validate_position(position: Tuple[int, int], name: str = "Position") -> None:
    """
    Validate that a position is valid.
    
    Args:
        position: Position to validate
        name: Name for error messages
        
    Raises:
        InvalidPositionError: If position is invalid
    """
    if not isinstance(position, (tuple, list)):
        raise InvalidPositionError(f"{name} must be a tuple or list, got {type(position)}")
    
    if len(position) != 2:
        raise InvalidPositionError(f"{name} must have 2 elements, got {len(position)}")
    
    x, y = position
    if not isinstance(x, int) or not isinstance(y, int):
        raise InvalidPositionError(f"{name} coordinates must be integers, got ({type(x)}, {type(y)})")


def is_position_valid(position: Tuple[int, int]) -> bool:
    """
    Check if a position is within grid bounds.
    
    Args:
        position: (x, y) position to check
        
    Returns:
        bool: True if position is valid, False otherwise
    """
    try:
        validate_position(position)
        x, y = position
        return 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT
    except InvalidPositionError:
        return False


def get_all_obstacles(snake1: Snake, snake2: Snake, 
                     requesting_snake: Snake) -> Set[Tuple[int, int]]:
    """
    Get all obstacle positions for pathfinding.
    
    For the requesting snake, its own tail is not considered an obstacle
    (as it will move by the time the head reaches that position).
    
    Args:
        snake1: First snake in the game
        snake2: Second snake in the game
        requesting_snake: The snake requesting the pathfinding
        
    Returns:
        Set of (x, y) positions that are obstacles
        
    Raises:
        PathfindingError: If snake references are invalid
    """
    try:
        # Validate inputs
        if not all(isinstance(snake, Snake) for snake in [snake1, snake2, requesting_snake]):
            raise PathfindingError("Invalid snake references provided")
        
        if requesting_snake not in [snake1, snake2]:
            raise PathfindingError("Requesting snake must be one of the game snakes")
        
        obstacles = set()
        
        # Add obstacles based on which snake is requesting
        if requesting_snake == snake1:
            # For snake1: its own body (except tail) + all of snake2
            if snake1.body and len(snake1.body) > 1:
                obstacles.update(snake1.body[:-1])  # Exclude tail
            if snake2.body:
                obstacles.update(snake2.body)  # Include all of snake2
        else:
            # For snake2: its own body (except tail) + all of snake1
            if snake2.body and len(snake2.body) > 1:
                obstacles.update(snake2.body[:-1])  # Exclude tail
            if snake1.body:
                obstacles.update(snake1.body)  # Include all of snake1
        
        # Validate all obstacle positions
        valid_obstacles = {pos for pos in obstacles if is_position_valid(pos)}
        
        if len(valid_obstacles) != len(obstacles):
            logger.warning(f"Removed {len(obstacles) - len(valid_obstacles)} invalid obstacle positions")
        
        return valid_obstacles
        
    except Exception as e:
        logger.error(f"Error getting obstacles: {e}")
        # Return empty set on error to allow game to continue
        return set()


def get_valid_neighbors(pos: Tuple[int, int], snake1: Snake, snake2: Snake,
                       requesting_snake: Snake) -> List[Tuple[int, int]]:
    """
    Get all valid neighboring positions from a given position.
    
    Args:
        pos: Current position
        snake1: First snake
        snake2: Second snake
        requesting_snake: Snake requesting the neighbors
        
    Returns:
        List of valid neighboring positions
        
    Raises:
        InvalidPositionError: If position is invalid
    """
    try:
        # Validate position
        validate_position(pos, "Current position")
        
        if not is_position_valid(pos):
            raise InvalidPositionError(f"Position {pos} is out of bounds")
        
        x, y = pos
        neighbors = []
        obstacles = get_all_obstacles(snake1, snake2, requesting_snake)
        
        # Check all four directions
        for direction in Direction:
            dx, dy = direction.value
            new_x, new_y = x + dx, y + dy
            new_pos = (new_x, new_y)
            
            # Check if position is valid and not an obstacle
            if is_position_valid(new_pos) and new_pos not in obstacles:
                neighbors.append(new_pos)
        
        return neighbors
        
    except Exception as e:
        logger.error(f"Error getting valid neighbors: {e}")
        return []


def bfs_pathfind(start: Tuple[int, int], target: Tuple[int, int],
                 snake1: Snake, snake2: Snake, requesting_snake: Snake,
                 max_depth: Optional[int] = None) -> List[Tuple[int, int]]:
    """
    Find shortest path using Breadth-First Search.
    
    BFS guarantees the shortest path in terms of number of moves.
    
    Args:
        start: Starting position
        target: Target position
        snake1: First snake
        snake2: Second snake
        requesting_snake: Snake requesting the path
        max_depth: Optional maximum search depth
        
    Returns:
        List of positions representing the path (excluding start)
        Empty list if no path found
        
    Raises:
        InvalidPositionError: If positions are invalid
        PathfindingError: If other errors occur
    """
    try:
        # Validate positions
        validate_position(start, "Start position")
        validate_position(target, "Target position")
        
        if not is_position_valid(start):
            raise InvalidPositionError(f"Start position {start} is out of bounds")
        
        if not is_position_valid(target):
            raise InvalidPositionError(f"Target position {target} is out of bounds")
        
        # Early exit if start equals target
        if start == target:
            return []
        
        # Initialize BFS
        queue = deque([(start, [])])
        visited = {start}
        nodes_explored = 0
        
        while queue:
            # Check depth limit
            if max_depth and nodes_explored >= max_depth:
                logger.debug(f"BFS reached max depth {max_depth}")
                break
            
            current_pos, path = queue.popleft()
            nodes_explored += 1
            
            # Get valid neighbors
            neighbors = get_valid_neighbors(current_pos, snake1, snake2, requesting_snake)
            
            for neighbor in neighbors:
                # Check if we reached the target
                if neighbor == target:
                    final_path = path + [neighbor]
                    logger.debug(f"BFS found path of length {len(final_path)} after exploring {nodes_explored} nodes")
                    return final_path
                
                # Add unvisited neighbors to queue
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        # No path found
        logger.debug(f"BFS found no path from {start} to {target} after exploring {nodes_explored} nodes")
        return []
        
    except InvalidPositionError:
        raise
    except Exception as e:
        logger.error(f"Error in BFS pathfinding: {e}")
        raise PathfindingError(f"BFS pathfinding failed: {e}")


def calculate_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
    """
    Calculate Manhattan distance between two positions.
    
    Manhattan distance is the sum of absolute differences of coordinates,
    representing the minimum number of moves needed without obstacles.
    
    Args:
        pos1: First position
        pos2: Second position
        
    Returns:
        Manhattan distance between positions
        
    Raises:
        InvalidPositionError: If positions are invalid
    """
    try:
        validate_position(pos1, "Position 1")
        validate_position(pos2, "Position 2")
        
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
        
    except InvalidPositionError:
        raise
    except Exception as e:
        logger.error(f"Error calculating distance: {e}")
        raise PathfindingError(f"Distance calculation failed: {e}")


def calculate_euclidean_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
    """
    Calculate Euclidean distance between two positions.
    
    Args:
        pos1: First position
        pos2: Second position
        
    Returns:
        Euclidean distance between positions
        
    Raises:
        InvalidPositionError: If positions are invalid
    """
    try:
        validate_position(pos1, "Position 1")
        validate_position(pos2, "Position 2")
        
        dx = pos1[0] - pos2[0]
        dy = pos1[1] - pos2[1]
        return math.sqrt(dx * dx + dy * dy)
        
    except InvalidPositionError:
        raise
    except Exception as e:
        logger.error(f"Error calculating Euclidean distance: {e}")
        raise PathfindingError(f"Euclidean distance calculation failed: {e}")


def get_direction_to_target(current_pos: Tuple[int, int], 
                          target_pos: Tuple[int, int]) -> Direction:
    """
    Calculate the direction to move from current position to target.
    
    If positions are diagonal, prioritizes horizontal movement.
    
    Args:
        current_pos: Current position
        target_pos: Target position
        
    Returns:
        Direction to move toward target
        
    Raises:
        InvalidPositionError: If positions are invalid
        PathfindingError: If positions are the same
    """
    try:
        validate_position(current_pos, "Current position")
        validate_position(target_pos, "Target position")
        
        if current_pos == target_pos:
            raise PathfindingError("Current and target positions are the same")
        
        curr_x, curr_y = current_pos
        target_x, target_y = target_pos
        
        dx = target_x - curr_x
        dy = target_y - curr_y
        
        # Prioritize horizontal movement for diagonal positions
        if dx > 0:
            return Direction.RIGHT
        elif dx < 0:
            return Direction.LEFT
        elif dy > 0:
            return Direction.DOWN
        else:
            return Direction.UP
            
    except (InvalidPositionError, PathfindingError):
        raise
    except Exception as e:
        logger.error(f"Error calculating direction: {e}")
        raise PathfindingError(f"Direction calculation failed: {e}")


def a_star_pathfind(start: Tuple[int, int], target: Tuple[int, int],
                    snake1: Snake, snake2: Snake, requesting_snake: Snake,
                    max_nodes: int = 1000) -> List[Tuple[int, int]]:
    """
    Find path using A* algorithm with Manhattan distance heuristic.
    
    A* is more efficient than BFS for longer paths but requires more computation
    per node. Best used when paths are expected to be long.
    
    Args:
        start: Starting position
        target: Target position
        snake1: First snake
        snake2: Second snake
        requesting_snake: Snake requesting the path
        max_nodes: Maximum nodes to explore
        
    Returns:
        List of positions representing the path (excluding start)
        Empty list if no path found
    """
    try:
        # Validate positions
        validate_position(start, "Start position")
        validate_position(target, "Target position")
        
        if start == target:
            return []
        
        # Initialize A*
        start_node = PathNode(start, 0, calculate_distance(start, target))
        start_node.f_cost = start_node.g_cost + start_node.h_cost
        
        open_set = [start_node]
        closed_set: Set[Tuple[int, int]] = set()
        node_map: Dict[Tuple[int, int], PathNode] = {start: start_node}
        nodes_explored = 0
        
        while open_set and nodes_explored < max_nodes:
            # Get node with lowest f_cost
            current_node = heapq.heappop(open_set)
            nodes_explored += 1
            
            # Check if we reached the target
            if current_node.position == target:
                # Reconstruct path
                path = []
                node = current_node
                while node.parent:
                    path.append(node.position)
                    node = node.parent
                path.reverse()
                
                logger.debug(f"A* found path of length {len(path)} after exploring {nodes_explored} nodes")
                return path
            
            closed_set.add(current_node.position)
            
            # Explore neighbors
            neighbors = get_valid_neighbors(current_node.position, snake1, snake2, requesting_snake)
            
            for neighbor_pos in neighbors:
                if neighbor_pos in closed_set:
                    continue
                
                # Calculate costs
                g_cost = current_node.g_cost + 1
                h_cost = calculate_distance(neighbor_pos, target)
                f_cost = g_cost + h_cost
                
                # Check if we have a better path to this neighbor
                if neighbor_pos in node_map:
                    neighbor_node = node_map[neighbor_pos]
                    if g_cost < neighbor_node.g_cost:
                        neighbor_node.g_cost = g_cost
                        neighbor_node.f_cost = f_cost
                        neighbor_node.parent = current_node
                else:
                    # Create new node
                    neighbor_node = PathNode(neighbor_pos, g_cost, h_cost, f_cost, current_node)
                    node_map[neighbor_pos] = neighbor_node
                    heapq.heappush(open_set, neighbor_node)
        
        # No path found
        logger.debug(f"A* found no path after exploring {nodes_explored} nodes")
        return []
        
    except Exception as e:
        logger.error(f"Error in A* pathfinding: {e}")
        return []


def find_safe_positions(snake1: Snake, snake2: Snake, requesting_snake: Snake,
                       radius: int = 5) -> List[Tuple[int, int]]:
    """
    Find all safe positions within a radius from the requesting snake's head.
    
    Useful for finding escape routes or safe areas.
    
    Args:
        snake1: First snake
        snake2: Second snake
        requesting_snake: Snake requesting safe positions
        radius: Search radius from snake's head
        
    Returns:
        List of safe positions sorted by distance from head
    """
    try:
        if not requesting_snake or not requesting_snake.body:
            return []
        
        head = requesting_snake.get_head()
        obstacles = get_all_obstacles(snake1, snake2, requesting_snake)
        safe_positions = []
        
        # Search within radius
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if abs(dx) + abs(dy) > radius:  # Manhattan distance check
                    continue
                
                pos = (head[0] + dx, head[1] + dy)
                
                if is_position_valid(pos) and pos not in obstacles and pos != head:
                    safe_positions.append(pos)
        
        # Sort by distance from head
        safe_positions.sort(key=lambda pos: calculate_distance(head, pos))
        
        return safe_positions
        
    except Exception as e:
        logger.error(f"Error finding safe positions: {e}")
        return []