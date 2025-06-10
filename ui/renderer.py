"""
Game Renderer Module

This module handles all visual rendering for the AI Snake Battle game,
including the game grid, snakes, food, UI elements, and game over screen.

Classes:
    Renderer: Main rendering class for all game visuals
    RenderError: Exception for rendering-related errors

Author: Devansh Tomar
Version: 1.0.0
"""

import pygame
import logging
from typing import Optional, Tuple, List, Dict
from dataclasses import dataclass
import time

from config import *
from models.snake import Snake
from game.game_state import GameState

# Configure logging
logger = logging.getLogger(__name__)


class RenderError(Exception):
    """Exception for rendering-related errors"""
    pass


@dataclass
class RenderConfig:
    """Configuration for rendering appearance and behavior"""
    # Fonts
    main_font_size: int = 28
    big_font_size: int = 48
    small_font_size: int = 22
    
    # UI Panel
    ui_panel_alpha: int = 180
    ui_border_width: int = 2
    
    # Grid
    grid_line_alpha: int = 50
    
    # Game Over
    game_over_overlay_alpha: int = 200
    
    # Performance
    enable_grid: bool = True
    enable_animations: bool = True
    fps_display: bool = False


class Renderer:
    """
    Handles all visual rendering for the AI Snake Battle game.
    
    This class is responsible for drawing all game elements including
    the playing field, snakes, food, UI elements, and overlays.
    
    Attributes:
        screen: Pygame screen surface
        config: Rendering configuration
        fonts: Dictionary of loaded fonts
        surfaces: Pre-rendered surfaces for performance
    """
    
    def __init__(self, screen: pygame.Surface, config: Optional[RenderConfig] = None) -> None:
        """
        Initialize the renderer.
        
        Args:
            screen: Pygame screen surface to draw on
            config: Optional rendering configuration
            
        Raises:
            RenderError: If screen is invalid or initialization fails
        """
        # Validate pygame initialization
        if not pygame.get_init():
            raise RenderError("Pygame must be initialized before creating renderer")
        
        # Validate screen
        if not isinstance(screen, pygame.Surface):
            raise RenderError("Invalid screen surface provided")
        
        self.screen = screen
        self.screen_width, self.screen_height = screen.get_size()
        
        # Validate screen dimensions
        if self.screen_width <= 0 or self.screen_height <= 0:
            raise RenderError(f"Invalid screen dimensions: {self.screen_width}x{self.screen_height}")
        
        # Use provided config or defaults
        self.config = config or RenderConfig()
        
        # Initialize components
        try:
            self._init_fonts()
            self._init_surfaces()
            
            # Performance tracking
            self.frame_count = 0
            self.last_fps_update = time.time()
            self.current_fps = 0
            
            # Cache for optimization
            self._grid_surface = None
            self._last_grid_size = None
            
        except Exception as e:
            logger.error(f"Failed to initialize renderer: {e}")
            raise RenderError(f"Renderer initialization failed: {e}")
        
        logger.info("Renderer initialized successfully")
    
    def _init_fonts(self) -> None:
        """Initialize fonts with error handling"""
        self.fonts = {}
        
        try:
            # Try to load default fonts
            self.fonts['main'] = pygame.font.Font(None, self.config.main_font_size)
            self.fonts['big'] = pygame.font.Font(None, self.config.big_font_size)
            self.fonts['small'] = pygame.font.Font(None, self.config.small_font_size)
            
        except Exception as e:
            logger.warning(f"Failed to load default fonts: {e}")
            
            # Fallback to system fonts
            try:
                self.fonts['main'] = pygame.font.SysFont('arial', self.config.main_font_size)
                self.fonts['big'] = pygame.font.SysFont('arial', self.config.big_font_size)
                self.fonts['small'] = pygame.font.SysFont('arial', self.config.small_font_size)
                
            except Exception as e2:
                logger.error(f"Failed to load fallback fonts: {e2}")
                raise RenderError("Could not initialize any fonts")
        
        # Convenience aliases
        self.font = self.fonts['main']
        self.big_font = self.fonts['big']
        self.small_font = self.fonts['small']
    
    def _init_surfaces(self) -> None:
        """Initialize reusable surfaces for performance"""
        self.surfaces = {}
        
        try:
            # Create UI panel surface
            self.surfaces['ui_panel'] = pygame.Surface((WINDOW_WIDTH, UI_HEIGHT))
            self.surfaces['ui_panel'].set_alpha(self.config.ui_panel_alpha)
            
            # Create game over overlay
            self.surfaces['game_over_overlay'] = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            self.surfaces['game_over_overlay'].set_alpha(self.config.game_over_overlay_alpha)
            
        except Exception as e:
            logger.error(f"Failed to create surfaces: {e}")
            # Continue without pre-created surfaces
            self.surfaces = {}
    
    def draw(self, game_state: GameState) -> None:
        """
        Draw the complete game frame.
        
        Args:
            game_state: Current game state to render
            
        Raises:
            RenderError: If rendering fails critically
        """
        try:
            # Validate game state
            if not isinstance(game_state, GameState):
                raise RenderError("Invalid game state provided")
            
            # Clear screen
            self.screen.fill(BLACK)
            
            # Draw game elements in order
            if self.config.enable_grid:
                self._draw_grid()
            
            # Draw game objects
            self._draw_game_objects(game_state)
            
            # Draw UI
            self._draw_ui(game_state)
            
            # Draw FPS if enabled
            if self.config.fps_display:
                self._draw_fps()
            
            # Update display
            pygame.display.flip()
            
            # Update frame counter
            self.frame_count += 1
            
        except Exception as e:
            logger.error(f"Critical rendering error: {e}")
            # Try to show error on screen
            self._draw_error_state(str(e))
            raise RenderError(f"Failed to render frame: {e}")
    
    def _draw_game_objects(self, game_state: GameState) -> None:
        """Draw all game objects (snakes and food)"""
        try:
            # Draw snakes
            if hasattr(game_state, 'snake1') and game_state.snake1:
                self._draw_snake(game_state.snake1, ORANGE, DARK_ORANGE)
            
            if hasattr(game_state, 'snake2') and game_state.snake2:
                self._draw_snake(game_state.snake2, CYAN, DARK_CYAN)
            
            # Draw food
            if hasattr(game_state, 'food') and game_state.food:
                self._draw_food(game_state.food)
                
        except Exception as e:
            logger.error(f"Error drawing game objects: {e}")
    
    def _draw_grid(self) -> None:
        """Draw the game grid with caching for performance"""
        try:
            # Check if we need to regenerate grid
            current_size = (WINDOW_WIDTH, WINDOW_HEIGHT, GRID_SIZE)
            if self._grid_surface is None or self._last_grid_size != current_size:
                self._generate_grid_surface()
                self._last_grid_size = current_size
            
            # Blit cached grid
            if self._grid_surface:
                self.screen.blit(self._grid_surface, (0, UI_HEIGHT))
                
        except Exception as e:
            logger.error(f"Error drawing grid: {e}")
            # Fall back to direct drawing
            self._draw_grid_direct()
    
    def _generate_grid_surface(self) -> None:
        """Generate cached grid surface"""
        try:
            self._grid_surface = pygame.Surface((WINDOW_WIDTH, GAME_HEIGHT))
            self._grid_surface.fill(BLACK)
            self._grid_surface.set_alpha(255)
            
            # Draw vertical lines
            for x in range(0, WINDOW_WIDTH, GRID_SIZE):
                pygame.draw.line(self._grid_surface, GRAY, (x, 0), (x, GAME_HEIGHT))
            
            # Draw horizontal lines
            for y in range(0, GAME_HEIGHT, GRID_SIZE):
                pygame.draw.line(self._grid_surface, GRAY, (0, y), (WINDOW_WIDTH, y))
                
        except Exception as e:
            logger.error(f"Failed to generate grid surface: {e}")
            self._grid_surface = None
    
    def _draw_grid_direct(self) -> None:
        """Draw grid directly without caching (fallback)"""
        # Vertical lines
        for x in range(0, WINDOW_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (x, UI_HEIGHT), (x, WINDOW_HEIGHT))
        
        # Horizontal lines
        for y in range(UI_HEIGHT, WINDOW_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (0, y), (WINDOW_WIDTH, y))
    
    def _draw_snake(self, snake: Snake, head_color: Tuple[int, int, int], 
                   body_color: Tuple[int, int, int]) -> None:
        """
        Draw a snake with proper error handling.
        
        Args:
            snake: Snake object to draw
            head_color: Color for the snake's head
            body_color: Color for the snake's body
        """
        try:
            # Validate snake
            if not snake or not hasattr(snake, 'body') or not snake.body:
                logger.warning("Attempted to draw invalid snake")
                return
            
            # Determine colors based on alive status
            if not snake.alive:
                head_color = GRAY
                body_color = (64, 64, 64)
            
            # Draw each segment
            for i, segment in enumerate(snake.body):
                try:
                    x, y = segment
                    
                    # Validate coordinates
                    if not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT):
                        logger.warning(f"Snake segment out of bounds: ({x}, {y})")
                        continue
                    
                    # Choose color
                    color = head_color if i == 0 else body_color
                    
                    # Calculate pixel position
                    pixel_x = x * GRID_SIZE
                    pixel_y = y * GRID_SIZE + UI_HEIGHT
                    
                    # Draw segment with border for visibility
                    segment_rect = pygame.Rect(pixel_x, pixel_y, GRID_SIZE, GRID_SIZE)
                    pygame.draw.rect(self.screen, color, segment_rect)
                    
                    # Optional: Add border for better visibility
                    if self.config.enable_animations and i == 0:  # Head only
                        pygame.draw.rect(self.screen, BLACK, segment_rect, 1)
                        
                except Exception as e:
                    logger.error(f"Error drawing snake segment {i}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error drawing snake: {e}")
    
    def _draw_food(self, food_pos: Tuple[int, int]) -> None:
        """
        Draw food with validation.
        
        Args:
            food_pos: (x, y) position of food
        """
        try:
            # Validate position
            if not isinstance(food_pos, (tuple, list)) or len(food_pos) != 2:
                logger.error(f"Invalid food position: {food_pos}")
                return
            
            food_x, food_y = food_pos
            
            # Validate coordinates
            if not (0 <= food_x < GRID_WIDTH and 0 <= food_y < GRID_HEIGHT):
                logger.error(f"Food position out of bounds: ({food_x}, {food_y})")
                return
            
            # Calculate pixel position
            pixel_x = food_x * GRID_SIZE
            pixel_y = food_y * GRID_SIZE + UI_HEIGHT
            
            # Draw food with animation if enabled
            if self.config.enable_animations:
                # Pulsing effect
                pulse = abs((self.frame_count % 60) - 30) / 30
                size = int(GRID_SIZE * (0.8 + 0.2 * pulse))
                offset = (GRID_SIZE - size) // 2
                
                food_rect = pygame.Rect(pixel_x + offset, pixel_y + offset, size, size)
            else:
                food_rect = pygame.Rect(pixel_x, pixel_y, GRID_SIZE, GRID_SIZE)
            
            pygame.draw.rect(self.screen, RED, food_rect)
            
        except Exception as e:
            logger.error(f"Error drawing food: {e}")
    
    def _draw_ui(self, game_state: GameState) -> None:
        """Draw the UI panel with game information"""
        try:
            # Draw UI background
            if 'ui_panel' in self.surfaces:
                self.surfaces['ui_panel'].fill(BLACK)
                self.screen.blit(self.surfaces['ui_panel'], (0, 0))
            else:
                # Fallback
                ui_rect = pygame.Rect(0, 0, WINDOW_WIDTH, UI_HEIGHT)
                pygame.draw.rect(self.screen, BLACK, ui_rect)
            
            # Draw UI border
            pygame.draw.line(self.screen, WHITE, (0, UI_HEIGHT), 
                           (WINDOW_WIDTH, UI_HEIGHT), self.config.ui_border_width)
            
            # Draw snake stats
            if hasattr(game_state, 'snake1') and game_state.snake1:
                ai1_type = getattr(game_state, 'ai1_type', 'Unknown')
                self._draw_snake_stats(game_state.snake1, 20, ORANGE, "ORANGE", ai1_type)
            
            if hasattr(game_state, 'snake2') and game_state.snake2:
                ai2_type = getattr(game_state, 'ai2_type', 'Unknown')
                self._draw_snake_stats(game_state.snake2, WINDOW_WIDTH - 200, CYAN, "CYAN", ai2_type)
            
            # Draw center information
            self._draw_center_info(game_state)
            
            # Draw game over overlay if needed
            if hasattr(game_state, 'game_over') and game_state.game_over:
                self._draw_game_over(game_state)
                
        except Exception as e:
            logger.error(f"Error drawing UI: {e}")
    
    def _draw_snake_stats(self, snake: Snake, x_pos: int, color: Tuple[int, int, int], 
                         title: str, ai_type: Optional[str] = None) -> None:
        """Draw statistics for a single snake"""
        try:
            # Title with AI type
            if ai_type and ai_type != 'Unknown':
                title_text = self.font.render(f"{title} ({ai_type})", True, color)
            else:
                title_text = self.font.render(title, True, color)
            self.screen.blit(title_text, (x_pos, 10))
            
            # Score
            score_text = self.font.render(f"Score: {snake.score}", True, WHITE)
            self.screen.blit(score_text, (x_pos, 35))
            
            # Length
            length_text = self.small_font.render(f"Length: {len(snake.body)}", True, WHITE)
            self.screen.blit(length_text, (x_pos, 55))
            
            # Status
            status_color = color if snake.alive else RED
            status_text = self.small_font.render(
                f"Status: {'ALIVE' if snake.alive else 'DEAD'}", 
                True, status_color
            )
            self.screen.blit(status_text, (x_pos, 75))
            
        except Exception as e:
            logger.error(f"Error drawing snake stats: {e}")
    
    def _draw_center_info(self, game_state: GameState) -> None:
        """Draw central game information"""
        try:
            center_x = WINDOW_WIDTH // 2
            
            # Game title
            game_title = self.font.render("AI SNAKE BATTLE", True, YELLOW)
            title_rect = game_title.get_rect(center=(center_x, 25))
            self.screen.blit(game_title, title_rect)
            
            # Food position
            if hasattr(game_state, 'food') and game_state.food:
                food_info = self.small_font.render(
                    f"Food at ({game_state.food[0]}, {game_state.food[1]})", 
                    True, WHITE
                )
                food_rect = food_info.get_rect(center=(center_x, 50))
                self.screen.blit(food_info, food_rect)
            
            # Game mode
            speed_info = self.small_font.render("FAST MODE", True, WHITE)
            speed_rect = speed_info.get_rect(center=(center_x, 70))
            self.screen.blit(speed_info, speed_rect)
            
        except Exception as e:
            logger.error(f"Error drawing center info: {e}")
    
    def _draw_game_over(self, game_state: GameState) -> None:
        """Draw game over overlay with results"""
        try:
            # Draw overlay
            if 'game_over_overlay' in self.surfaces:
                self.surfaces['game_over_overlay'].fill(BLACK)
                self.screen.blit(self.surfaces['game_over_overlay'], (0, 0))
            else:
                # Fallback
                overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
                overlay.set_alpha(self.config.game_over_overlay_alpha)
                overlay.fill(BLACK)
                self.screen.blit(overlay, (0, 0))
            
            # Determine winner and stats
            winner = getattr(game_state, 'winner', None)
            
            if winner:
                # Winner announcement
                winner_color = ORANGE if winner == game_state.snake1 else CYAN
                winner_text = self.big_font.render(
                    f"{winner.name.upper()} WINS!", 
                    True, winner_color
                )
                
                # Winner stats
                stats_lines = [
                    f"Final Score: {winner.score} points",
                    f"Final Length: {len(winner.body)} segments",
                    f"Food Consumed: {winner.score // FOOD_SCORE} items"
                ]
            else:
                # Tie game
                winner_text = self.big_font.render("IT'S A TIE!", True, YELLOW)
                
                # Tie stats
                stats_lines = [
                    f"Orange Score: {game_state.snake1.score} | Cyan Score: {game_state.snake2.score}",
                    f"Orange Length: {len(game_state.snake1.body)} | Cyan Length: {len(game_state.snake2.body)}",
                    f"Total Food: {(game_state.snake1.score + game_state.snake2.score) // FOOD_SCORE} items"
                ]
            
            # Draw winner text
            winner_rect = winner_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100))
            self.screen.blit(winner_text, winner_rect)
            
            # Draw stats
            for i, line in enumerate(stats_lines):
                stat_text = self.font.render(line, True, WHITE)
                stat_rect = stat_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30 + i * 30))
                self.screen.blit(stat_text, stat_rect)
            
            # Draw instructions
            restart_text = self.font.render("Press R to Restart | Press Q to Quit", True, WHITE)
            restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 80))
            self.screen.blit(restart_text, restart_rect)
            
            # Performance info
            performance_text = self.small_font.render("High-Speed AI Battle Mode Active", True, GRAY)
            perf_rect = performance_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 120))
            self.screen.blit(performance_text, perf_rect)
            
        except Exception as e:
            logger.error(f"Error drawing game over screen: {e}")
    
    def _draw_fps(self) -> None:
        """Draw FPS counter for performance monitoring"""
        try:
            # Update FPS calculation
            current_time = time.time()
            if current_time - self.last_fps_update > 1.0:
                self.current_fps = self.frame_count / (current_time - self.last_fps_update)
                self.frame_count = 0
                self.last_fps_update = current_time
            
            # Draw FPS
            fps_text = self.small_font.render(f"FPS: {self.current_fps:.1f}", True, YELLOW)
            self.screen.blit(fps_text, (10, 10))
            
        except Exception as e:
            logger.error(f"Error drawing FPS: {e}")
    
    def _draw_error_state(self, error_message: str) -> None:
        """Draw error state as fallback"""
        try:
            self.screen.fill(BLACK)
            error_text = self.font.render(f"Render Error: {error_message}", True, RED)
            error_rect = error_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.screen.blit(error_text, error_rect)
            pygame.display.flip()
        except:
            logger.critical(f"Failed to display error state: {error_message}")