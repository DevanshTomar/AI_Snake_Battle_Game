"""
Game State Module

This module manages the overall game state including:
- Snake initialization and positioning
- Food generation and management
- Game loop update logic
- Collision detection orchestration
- Win condition checking

Classes:
    GameState: Main game state manager
    GameStateError: Exception for game state errors

Author: Devansh Tomar
Version: 1.0.0
"""

import random
import logging
import time
from typing import Tuple, Optional, Dict, Type
from dataclasses import dataclass, field

from models.snake import Snake
from game.ai_controller import AIController, AIError
from game.ai_strategies import BalancedAI, AggressiveAI, DefensiveAI
from enums import Direction
from config import (
    GRID_WIDTH, GRID_HEIGHT, ORANGE, CYAN, FOOD_SCORE
)

# Configure logging
logger = logging.getLogger(__name__)


class GameStateError(Exception):
    """Exception for game state related errors"""
    pass


@dataclass
class GameStatistics:
    """Track game statistics"""
    game_duration: float = 0.0
    moves_count: int = 0
    food_generated: int = 0
    head_collisions: int = 0
    simultaneous_food_attempts: int = 0
    
    # Performance metrics
    update_times: list = field(default_factory=list)
    
    def add_update_time(self, duration: float) -> None:
        """Add update duration for performance tracking"""
        self.update_times.append(duration)
        if len(self.update_times) > 100:  # Keep last 100 updates
            self.update_times.pop(0)
    
    def get_average_update_time(self) -> float:
        """Get average update time in milliseconds"""
        if not self.update_times:
            return 0.0
        return sum(self.update_times) / len(self.update_times) * 1000


class GameState:
    """
    Manages the complete game state for AI Snake Battle.
    
    This class coordinates all game elements including snakes, food, AI controllers,
    and game rules. It handles the main game loop update, collision detection,
    and win condition checking.
    
    Attributes:
        snake1 (Snake): First snake (Orange)
        snake2 (Snake): Second snake (Cyan)
        ai1_controller (AIController): AI controller for snake1
        ai2_controller (AIController): AI controller for snake2
        food (Tuple[int, int]): Current food position
        game_over (bool): Whether the game has ended
        winner (Optional[Snake]): The winning snake (None for tie)
        statistics (GameStatistics): Game performance and event statistics
    """
    
    # Class constants
    MIN_SNAKE_DISTANCE = 10  # Minimum starting distance between snakes
    MAX_FOOD_GENERATION_ATTEMPTS = 1000  # Prevent infinite loops
    
    # Available AI strategies
    AI_STRATEGIES: Dict[str, Type[AIController]] = {
        "Balanced": BalancedAI,
        "Aggressive": AggressiveAI,
        "Defensive": DefensiveAI
    }
    
    def __init__(self, ai1_type: str = "Balanced", ai2_type: str = "Balanced") -> None:
        """
        Initialize the game state with specified AI types.
        
        Args:
            ai1_type: AI strategy for snake1 (Balanced/Aggressive/Defensive)
            ai2_type: AI strategy for snake2 (Balanced/Aggressive/Defensive)
            
        Raises:
            GameStateError: If invalid AI type is specified
        """
        # Validate AI types
        if ai1_type not in self.AI_STRATEGIES:
            raise GameStateError(
                f"Invalid AI type for snake1: {ai1_type}. "
                f"Valid options: {list(self.AI_STRATEGIES.keys())}"
            )
        
        if ai2_type not in self.AI_STRATEGIES:
            raise GameStateError(
                f"Invalid AI type for snake2: {ai2_type}. "
                f"Valid options: {list(self.AI_STRATEGIES.keys())}"
            )
        
        self.ai1_type = ai1_type
        self.ai2_type = ai2_type
        
        # Initialize game components
        self.snake1: Optional[Snake] = None
        self.snake2: Optional[Snake] = None
        self.ai1_controller: Optional[AIController] = None
        self.ai2_controller: Optional[AIController] = None
        self.food: Optional[Tuple[int, int]] = None
        self.game_over: bool = False
        self.winner: Optional[Snake] = None
        
        # Statistics tracking
        self.statistics = GameStatistics()
        self.start_time: Optional[float] = None
        
        # Initialize game
        self.reset()
        
        logger.info(f"GameState initialized with AI types: {ai1_type} vs {ai2_type}")
    
    def reset(self) -> None:
        """
        Reset the game to initial state.
        
        This method reinitializes all game components including snakes,
        AI controllers, and food position.
        """
        try:
            # Create snakes with safe starting positions
            self._initialize_snakes()
            
            # Create AI controllers
            self._initialize_ai_controllers()
            
            # Generate initial food
            self.food = self.generate_food()
            
            # Reset game state
            self.game_over = False
            self.winner = None
            
            # Reset statistics
            self.statistics = GameStatistics()
            self.start_time = time.time()
            
            logger.info("Game state reset successfully")
            
        except Exception as e:
            logger.error(f"Failed to reset game state: {e}")
            raise GameStateError(f"Game reset failed: {e}")
    
    def _initialize_snakes(self) -> None:
        """Initialize snakes with safe starting positions"""
        # Ensure snakes start far enough apart
        margin = 5  # Distance from edges
        
        # Snake 1 starts on the left side
        snake1_x = margin
        snake1_y = GRID_HEIGHT // 2
        
        # Snake 2 starts on the right side
        snake2_x = GRID_WIDTH - margin - 1
        snake2_y = GRID_HEIGHT // 2
        
        # Validate positions
        if snake2_x - snake1_x < self.MIN_SNAKE_DISTANCE:
            logger.warning("Grid too small for safe snake spacing")
        
        # Create snakes
        self.snake1 = Snake((snake1_x, snake1_y), ORANGE, "Orange Snake")
        self.snake2 = Snake((snake2_x, snake2_y), CYAN, "Cyan Snake")
        
        # Set initial directions (facing each other)
        self.snake1.direction = Direction.RIGHT
        self.snake2.direction = Direction.LEFT
        
        logger.debug(f"Snakes initialized at ({snake1_x}, {snake1_y}) and ({snake2_x}, {snake2_y})")
    
    def _initialize_ai_controllers(self) -> None:
        """Initialize AI controllers for both snakes"""
        try:
            # Get AI classes
            AI1Class = self.AI_STRATEGIES[self.ai1_type]
            AI2Class = self.AI_STRATEGIES[self.ai2_type]
            
            # Create controller instances
            self.ai1_controller = AI1Class(self.snake1, self.snake2)
            self.ai2_controller = AI2Class(self.snake1, self.snake2)
            
            logger.debug(f"AI controllers initialized: {self.ai1_type} vs {self.ai2_type}")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI controllers: {e}")
            raise GameStateError(f"AI initialization failed: {e}")
    
    def generate_food(self) -> Tuple[int, int]:
        """
        Generate food at a random unoccupied position.
        
        Returns:
            Tuple[int, int]: The (x, y) position of the new food
            
        Raises:
            GameStateError: If no valid position can be found
        """
        # Track generation for statistics
        self.statistics.food_generated += 1
        
        # Get occupied positions
        occupied_positions = set()
        if self.snake1:
            occupied_positions.update(self.snake1.body)
        if self.snake2:
            occupied_positions.update(self.snake2.body)
        
        # Check if there's space for food
        total_cells = GRID_WIDTH * GRID_HEIGHT
        if len(occupied_positions) >= total_cells:
            raise GameStateError("No space available for food generation")
        
        # Try random positions
        attempts = 0
        while attempts < self.MAX_FOOD_GENERATION_ATTEMPTS:
            food_pos = (random.randint(0, GRID_WIDTH - 1), 
                       random.randint(0, GRID_HEIGHT - 1))
            
            if food_pos not in occupied_positions:
                logger.debug(f"Food generated at {food_pos} after {attempts + 1} attempts")
                return food_pos
            
            attempts += 1
        
        # If random generation fails, find first available position
        logger.warning("Random food generation failed, using systematic search")
        
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                if (x, y) not in occupied_positions:
                    return (x, y)
        
        # This should never happen if we checked space availability correctly
        raise GameStateError("Failed to generate food position")
    
    def update(self) -> None:
        """
        Update the game state for one frame.
        
        This method handles:
        1. AI decision making
        2. Snake movement
        3. Food consumption
        4. Collision detection
        5. Win condition checking
        """
        # Track update time for performance monitoring
        update_start = time.time()
        
        try:
            # Don't update if game is over
            if self.game_over:
                return
            
            # Validate game state
            if not self._validate_game_state():
                logger.error("Invalid game state detected")
                self.game_over = True
                return
            
            # Update statistics
            self.statistics.moves_count += 1
            
            # Phase 1: AI Decision Making
            self._update_ai_decisions()
            
            # Phase 2: Snake Movement and Food Consumption
            food_eaten_by = self._update_snake_movements()
            
            # Phase 3: Generate new food if eaten
            if food_eaten_by:
                food_eaten_by.score += FOOD_SCORE
                self.food = self.generate_food()
            
            # Phase 4: Check all collisions
            self._check_collisions()
            
            # Phase 5: Check win conditions
            self._check_win_condition()
            
            # Update game duration
            if self.start_time:
                self.statistics.game_duration = time.time() - self.start_time
            
        except Exception as e:
            logger.error(f"Error during game update: {e}")
            self.game_over = True
            self.winner = None  # Error results in no winner
        
        finally:
            # Track update duration
            update_duration = time.time() - update_start
            self.statistics.add_update_time(update_duration)
    
    def _validate_game_state(self) -> bool:
        """Validate that game state is consistent"""
        if not self.snake1 or not self.snake2:
            logger.error("Snakes not initialized")
            return False
        
        if not self.ai1_controller or not self.ai2_controller:
            logger.error("AI controllers not initialized")
            return False
        
        if not self.food:
            logger.error("Food not initialized")
            return False
        
        return True
    
    def _update_ai_decisions(self) -> None:
        """Update AI decisions for both snakes"""
        # Make decisions for alive snakes
        if self.snake1.alive:
            try:
                self.ai1_controller.make_decision(self.snake1, self.food)
            except Exception as e:
                logger.error(f"AI1 decision error: {e}")
                # Keep current direction on error
        
        if self.snake2.alive:
            try:
                self.ai2_controller.make_decision(self.snake2, self.food)
            except Exception as e:
                logger.error(f"AI2 decision error: {e}")
                # Keep current direction on error
    
    def _update_snake_movements(self) -> Optional[Snake]:
        """
        Update snake movements and handle food consumption.
        
        Returns:
            The snake that ate food, or None
        """
        food_eaten_by = None
        
        # Pre-calculate next positions to handle simultaneous food eating
        snake1_next = None
        snake2_next = None
        
        if self.snake1.alive:
            head_x, head_y = self.snake1.get_head()
            dx, dy = self.snake1.direction.value
            snake1_next = (head_x + dx, head_y + dy)
        
        if self.snake2.alive:
            head_x, head_y = self.snake2.get_head()
            dx, dy = self.snake2.direction.value
            snake2_next = (head_x + dx, head_y + dy)
        
        # Check for simultaneous food attempts
        if (snake1_next == self.food and snake2_next == self.food and 
            self.snake1.alive and self.snake2.alive):
            # Both snakes trying to eat same food
            self.statistics.simultaneous_food_attempts += 1
            
            # Award to snake with higher score (or snake1 if tied)
            if self.snake1.score >= self.snake2.score:
                food_eaten_by = self.snake1
                logger.debug("Simultaneous food attempt - awarded to snake1")
            else:
                food_eaten_by = self.snake2
                logger.debug("Simultaneous food attempt - awarded to snake2")
        else:
            # Normal food checking
            if snake1_next == self.food and self.snake1.alive:
                food_eaten_by = self.snake1
            elif snake2_next == self.food and self.snake2.alive:
                food_eaten_by = self.snake2
        
        # Move snakes
        if self.snake1.alive:
            will_eat = (food_eaten_by == self.snake1)
            self.snake1.move(grow=will_eat)
        
        if self.snake2.alive:
            will_eat = (food_eaten_by == self.snake2)
            self.snake2.move(grow=will_eat)
        
        return food_eaten_by
    
    def _check_collisions(self) -> None:
        """Check all collision types and update snake states"""
        # Wall collisions
        if self.snake1.alive and self.snake1.check_wall_collision():
            self.snake1.alive = False
            logger.info(f"{self.snake1.name} hit wall")
        
        if self.snake2.alive and self.snake2.check_wall_collision():
            self.snake2.alive = False
            logger.info(f"{self.snake2.name} hit wall")
        
        # Self collisions
        if self.snake1.alive and self.snake1.check_self_collision():
            self.snake1.alive = False
            logger.info(f"{self.snake1.name} hit itself")
        
        if self.snake2.alive and self.snake2.check_self_collision():
            self.snake2.alive = False
            logger.info(f"{self.snake2.name} hit itself")
        
        # Snake-to-snake collisions
        if self.snake1.alive and self.snake2.alive:
            snake1_head = self.snake1.get_head()
            snake2_head = self.snake2.get_head()
            
            # Head-to-head collision
            if snake1_head == snake2_head:
                self.snake1.alive = False
                self.snake2.alive = False
                self.statistics.head_collisions += 1
                logger.info("Head-to-head collision occurred")
            else:
                # Check body collisions
                if self.snake1.check_collision_with_snake(self.snake2):
                    self.snake1.alive = False
                    logger.info(f"{self.snake1.name} hit {self.snake2.name}")
                
                if self.snake2.check_collision_with_snake(self.snake1):
                    self.snake2.alive = False
                    logger.info(f"{self.snake2.name} hit {self.snake1.name}")
    
    def _check_win_condition(self) -> None:
        """Check if the game has ended and determine winner"""
        if not self.snake1.alive and not self.snake2.alive:
            # Both snakes died
            self.game_over = True
            
            # Determine winner by score
            if self.snake1.score > self.snake2.score:
                self.winner = self.snake1
                logger.info(f"{self.snake1.name} wins by score: {self.snake1.score} vs {self.snake2.score}")
            elif self.snake2.score > self.snake1.score:
                self.winner = self.snake2
                logger.info(f"{self.snake2.name} wins by score: {self.snake2.score} vs {self.snake1.score}")
            else:
                self.winner = None  # Tie
                logger.info(f"Game ended in tie: {self.snake1.score} - {self.snake2.score}")
                
        elif not self.snake1.alive:
            # Snake 1 died, snake 2 wins
            self.game_over = True
            self.winner = self.snake2
            logger.info(f"{self.snake2.name} wins by survival")
            
        elif not self.snake2.alive:
            # Snake 2 died, snake 1 wins
            self.game_over = True
            self.winner = self.snake1
            logger.info(f"{self.snake1.name} wins by survival")
    
    def get_game_stats(self) -> Dict:
        """
        Get comprehensive game statistics.
        
        Returns:
            Dictionary containing game statistics
        """
        return {
            "game_duration": self.statistics.game_duration,
            "moves_count": self.statistics.moves_count,
            "food_generated": self.statistics.food_generated,
            "head_collisions": self.statistics.head_collisions,
            "simultaneous_food_attempts": self.statistics.simultaneous_food_attempts,
            "average_update_time_ms": self.statistics.get_average_update_time(),
            "snake1_stats": {
                "score": self.snake1.score if self.snake1 else 0,
                "length": len(self.snake1.body) if self.snake1 else 0,
                "alive": self.snake1.alive if self.snake1 else False,
                "moves": self.snake1.stats.moves_made if self.snake1 else 0,
                "food_eaten": self.snake1.stats.food_eaten if self.snake1 else 0
            },
            "snake2_stats": {
                "score": self.snake2.score if self.snake2 else 0,
                "length": len(self.snake2.body) if self.snake2 else 0,
                "alive": self.snake2.alive if self.snake2 else False,
                "moves": self.snake2.stats.moves_made if self.snake2 else 0,
                "food_eaten": self.snake2.stats.food_eaten if self.snake2 else 0
            }
        }