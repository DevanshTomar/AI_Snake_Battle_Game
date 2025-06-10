"""
AI Selection Menu Module

This module provides an interactive menu system for selecting AI strategies
for both snakes before starting the game.

Classes:
    AISelectionMenu: Interactive menu for AI strategy selection
    MenuError: Exception for menu-related errors

Author: Devansh Tomar
Version: 1.0.0
"""

import pygame
import logging
from typing import Optional, Tuple, Dict, List
from dataclasses import dataclass
from enum import Enum

from config import *

# Configure logging
logger = logging.getLogger(__name__)


class MenuError(Exception):
    """Exception for menu-related errors"""
    pass


class MenuState(Enum):
    """Enumeration of menu states"""
    SELECTING_SNAKE1 = 1
    SELECTING_SNAKE2 = 2
    COMPLETE = 3
    CANCELLED = 4


@dataclass
class MenuConfig:
    """Configuration for menu appearance and behavior"""
    # Font sizes
    title_font_size: int = 48
    main_font_size: int = 36
    small_font_size: int = 24
    
    # Layout
    title_y: int = 50
    subtitle_y: int = 100
    snake_indicator_y: int = 180
    options_start_y: int = 250
    option_spacing: int = 100
    instructions_bottom_margin: int = 120
    
    # Visual
    selection_box_padding: int = 30
    selection_box_width: int = 500
    selection_box_height: int = 80
    selection_box_thickness: int = 3
    
    # Timing
    fps: int = 30
    key_repeat_delay: int = 200  # milliseconds
    key_repeat_interval: int = 50  # milliseconds


class AISelectionMenu:
    """
    Interactive menu for selecting AI strategies for both snakes.
    
    This menu provides a user-friendly interface for choosing AI behaviors
    before starting the game. It handles keyboard input, visual feedback,
    and state management.
    
    Attributes:
        screen: Pygame screen surface
        clock: Pygame clock for FPS control
        ai_options: List of available AI strategies
        ai_descriptions: Descriptions for each AI strategy
        state: Current menu state
        config: Menu configuration settings
    """
    
    def __init__(self, screen: pygame.Surface, config: Optional[MenuConfig] = None) -> None:
        """
        Initialize the AI selection menu.
        
        Args:
            screen: Pygame screen surface to draw on
            config: Optional menu configuration (uses defaults if None)
            
        Raises:
            MenuError: If screen is invalid or pygame not initialized
        """
        # Validate pygame initialization
        if not pygame.get_init():
            raise MenuError("Pygame must be initialized before creating menu")
        
        # Validate screen
        if not isinstance(screen, pygame.Surface):
            raise MenuError("Invalid screen surface provided")
        
        self.screen = screen
        self.screen_width, self.screen_height = screen.get_size()
        
        # Use provided config or defaults
        self.config = config or MenuConfig()
        
        # Initialize pygame components
        try:
            self.clock = pygame.time.Clock()
            
            # Initialize fonts with error handling
            self._init_fonts()
            
        except Exception as e:
            logger.error(f"Failed to initialize menu components: {e}")
            raise MenuError(f"Menu initialization failed: {e}")
        
        # AI options and descriptions
        self.ai_options = ["Balanced", "Aggressive", "Defensive"]
        self.ai_descriptions = {
            "Balanced": "Equal focus on food and survival",
            "Aggressive": "Prioritizes blocking opponent and taking risks",
            "Defensive": "Prioritizes survival and avoiding risks"
        }
        
        # Validate AI options match descriptions
        for option in self.ai_options:
            if option not in self.ai_descriptions:
                raise MenuError(f"Missing description for AI option: {option}")
        
        # Menu state
        self.snake1_selection = 0  # Index in ai_options
        self.snake2_selection = 0
        self.state = MenuState.SELECTING_SNAKE1
        
        # Performance tracking
        self.frame_count = 0
        self.last_key_time = 0
        
        # Enable key repeat for smoother navigation
        pygame.key.set_repeat(self.config.key_repeat_delay, self.config.key_repeat_interval)
        
        logger.info("AI Selection Menu initialized successfully")
    
    def _init_fonts(self) -> None:
        """Initialize fonts with fallback handling"""
        try:
            # Try to use default font
            self.title_font = pygame.font.Font(None, self.config.title_font_size)
            self.font = pygame.font.Font(None, self.config.main_font_size)
            self.small_font = pygame.font.Font(None, self.config.small_font_size)
            
        except Exception as e:
            logger.warning(f"Failed to load default font: {e}")
            
            # Fallback to system font
            try:
                self.title_font = pygame.font.SysFont('arial', self.config.title_font_size)
                self.font = pygame.font.SysFont('arial', self.config.main_font_size)
                self.small_font = pygame.font.SysFont('arial', self.config.small_font_size)
                
            except Exception as e2:
                logger.error(f"Failed to load fallback font: {e2}")
                raise MenuError("Could not initialize any fonts")
    
    def draw(self) -> None:
        """
        Draw the menu interface.
        
        This method renders all menu elements including title, options,
        descriptions, and instructions.
        """
        try:
            # Clear screen
            self.screen.fill(BLACK)
            
            # Draw title
            self._draw_title()
            
            # Draw current selection state
            self._draw_selection_state()
            
            # Draw AI options
            self._draw_ai_options()
            
            # Draw instructions
            self._draw_instructions()
            
            # Draw previous selection if on snake 2
            if self.state == MenuState.SELECTING_SNAKE2:
                self._draw_previous_selection()
            
            # Update display
            pygame.display.flip()
            
            # Track frame count for animations
            self.frame_count += 1
            
        except Exception as e:
            logger.error(f"Error drawing menu: {e}")
            # Try to at least show error message
            self._draw_error_screen(str(e))
    
    def _draw_title(self) -> None:
        """Draw the main title"""
        try:
            title = self.title_font.render("AI SNAKE BATTLE", True, YELLOW)
            title_rect = title.get_rect(center=(self.screen_width // 2, self.config.title_y))
            self.screen.blit(title, title_rect)
            
            subtitle = self.font.render("Select AI Behavior", True, WHITE)
            subtitle_rect = subtitle.get_rect(center=(self.screen_width // 2, self.config.subtitle_y))
            self.screen.blit(subtitle, subtitle_rect)
            
        except Exception as e:
            logger.error(f"Error drawing title: {e}")
    
    def _draw_selection_state(self) -> None:
        """Draw current selection state indicator"""
        if self.state not in [MenuState.SELECTING_SNAKE1, MenuState.SELECTING_SNAKE2]:
            return
        
        try:
            # Determine snake info based on current state
            if self.state == MenuState.SELECTING_SNAKE1:
                snake_color = ORANGE
                snake_name = "ORANGE SNAKE"
                current_selection = self.snake1_selection
            else:
                snake_color = CYAN
                snake_name = "CYAN SNAKE"
                current_selection = self.snake2_selection
            
            # Draw snake selection text
            snake_text = self.font.render(f"Selecting for {snake_name}", True, snake_color)
            snake_rect = snake_text.get_rect(center=(self.screen_width // 2, self.config.snake_indicator_y))
            self.screen.blit(snake_text, snake_rect)
            
        except Exception as e:
            logger.error(f"Error drawing selection state: {e}")
    
    def _draw_ai_options(self) -> None:
        """Draw AI strategy options with descriptions"""
        try:
            current_selection = (self.snake1_selection if self.state == MenuState.SELECTING_SNAKE1 
                               else self.snake2_selection)
            snake_color = ORANGE if self.state == MenuState.SELECTING_SNAKE1 else CYAN
            
            for i, option in enumerate(self.ai_options):
                y = self.config.options_start_y + i * self.config.option_spacing
                
                # Draw selection box for current selection
                if i == current_selection and self.state in [MenuState.SELECTING_SNAKE1, MenuState.SELECTING_SNAKE2]:
                    # Animated selection box
                    box_alpha = int(128 + 127 * abs((self.frame_count % 60) - 30) / 30)
                    box_color = (*snake_color, box_alpha) if len(snake_color) == 3 else snake_color
                    
                    box_rect = pygame.Rect(
                        self.screen_width // 2 - self.config.selection_box_width // 2,
                        y - self.config.selection_box_padding,
                        self.config.selection_box_width,
                        self.config.selection_box_height
                    )
                    
                    pygame.draw.rect(self.screen, snake_color[:3], box_rect, self.config.selection_box_thickness)
                
                # Draw option text
                option_text = self.font.render(option, True, WHITE)
                option_rect = option_text.get_rect(center=(self.screen_width // 2, y))
                self.screen.blit(option_text, option_rect)
                
                # Draw description
                desc_text = self.small_font.render(self.ai_descriptions[option], True, GRAY)
                desc_rect = desc_text.get_rect(center=(self.screen_width // 2, y + 25))
                self.screen.blit(desc_text, desc_rect)
                
        except Exception as e:
            logger.error(f"Error drawing AI options: {e}")
    
    def _draw_instructions(self) -> None:
        """Draw control instructions"""
        try:
            instructions = [
                "↑↓ Arrow Keys: Select AI",
                "ENTER: Confirm Selection",
                "ESC: Quit"
            ]
            
            y = self.screen_height - self.config.instructions_bottom_margin
            
            for instruction in instructions:
                inst_text = self.small_font.render(instruction, True, WHITE)
                inst_rect = inst_text.get_rect(center=(self.screen_width // 2, y))
                self.screen.blit(inst_text, inst_rect)
                y += 30
                
        except Exception as e:
            logger.error(f"Error drawing instructions: {e}")
    
    def _draw_previous_selection(self) -> None:
        """Draw the first snake's selection when selecting second snake"""
        try:
            selection_text = self.small_font.render(
                f"Orange: {self.ai_options[self.snake1_selection]}", 
                True, ORANGE
            )
            selection_rect = selection_text.get_rect(
                center=(self.screen_width // 2, self.screen_height - 20)
            )
            self.screen.blit(selection_text, selection_rect)
            
        except Exception as e:
            logger.error(f"Error drawing previous selection: {e}")
    
    def _draw_error_screen(self, error_message: str) -> None:
        """Draw error screen as fallback"""
        try:
            self.screen.fill(BLACK)
            error_font = pygame.font.Font(None, 24)
            error_text = error_font.render(f"Menu Error: {error_message}", True, RED)
            error_rect = error_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(error_text, error_rect)
            pygame.display.flip()
        except:
            # If even error screen fails, just log it
            logger.critical(f"Failed to display error screen: {error_message}")
    
    def handle_events(self) -> bool:
        """
        Handle input events for menu navigation.
        
        Returns:
            bool: True to continue, False to exit
        """
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.state = MenuState.CANCELLED
                    return False
                
                elif event.type == pygame.KEYDOWN:
                    return self._handle_keydown(event)
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling events: {e}")
            return True  # Continue despite error
    
    def _handle_keydown(self, event: pygame.event.Event) -> bool:
        """
        Handle keyboard input.
        
        Args:
            event: Pygame keyboard event
            
        Returns:
            bool: True to continue, False to exit
        """
        current_time = pygame.time.get_ticks()
        
        # Handle escape key
        if event.key == pygame.K_ESCAPE:
            self.state = MenuState.CANCELLED
            logger.info("Menu cancelled by user")
            return False
        
        # Handle navigation based on current state
        if self.state == MenuState.SELECTING_SNAKE1:
            return self._handle_snake1_input(event)
        elif self.state == MenuState.SELECTING_SNAKE2:
            return self._handle_snake2_input(event)
        
        return True
    
    def _handle_snake1_input(self, event: pygame.event.Event) -> bool:
        """Handle input for snake 1 selection"""
        if event.key == pygame.K_UP:
            self.snake1_selection = (self.snake1_selection - 1) % len(self.ai_options)
            logger.debug(f"Snake 1 selection: {self.ai_options[self.snake1_selection]}")
            
        elif event.key == pygame.K_DOWN:
            self.snake1_selection = (self.snake1_selection + 1) % len(self.ai_options)
            logger.debug(f"Snake 1 selection: {self.ai_options[self.snake1_selection]}")
            
        elif event.key == pygame.K_RETURN:
            self.state = MenuState.SELECTING_SNAKE2
            logger.info(f"Snake 1 AI selected: {self.ai_options[self.snake1_selection]}")
        
        return True
    
    def _handle_snake2_input(self, event: pygame.event.Event) -> bool:
        """Handle input for snake 2 selection"""
        if event.key == pygame.K_UP:
            self.snake2_selection = (self.snake2_selection - 1) % len(self.ai_options)
            logger.debug(f"Snake 2 selection: {self.ai_options[self.snake2_selection]}")
            
        elif event.key == pygame.K_DOWN:
            self.snake2_selection = (self.snake2_selection + 1) % len(self.ai_options)
            logger.debug(f"Snake 2 selection: {self.ai_options[self.snake2_selection]}")
            
        elif event.key == pygame.K_RETURN:
            self.state = MenuState.COMPLETE
            logger.info(f"Snake 2 AI selected: {self.ai_options[self.snake2_selection]}")
            return True
        
        return True
    
    def run(self) -> Optional[Tuple[str, str]]:
        """
        Run the menu loop and return selected AI types.
        
        Returns:
            Tuple of (snake1_ai_type, snake2_ai_type) if completed,
            None if cancelled or error occurred
        """
        logger.info("Starting AI selection menu")
        
        try:
            running = True
            
            while running and self.state not in [MenuState.COMPLETE, MenuState.CANCELLED]:
                # Handle events
                running = self.handle_events()
                
                # Draw menu
                self.draw()
                
                # Control frame rate
                self.clock.tick(self.config.fps)
            
            # Disable key repeat when done
            pygame.key.set_repeat()
            
            # Return results
            if self.state == MenuState.COMPLETE:
                result = (self.ai_options[self.snake1_selection], 
                         self.ai_options[self.snake2_selection])
                logger.info(f"Menu completed with selections: {result}")
                return result
            else:
                logger.info("Menu cancelled or failed")
                return None
                
        except Exception as e:
            logger.error(f"Fatal error in menu run loop: {e}")
            pygame.key.set_repeat()  # Ensure key repeat is disabled
            return None
    
    def reset(self) -> None:
        """Reset menu to initial state"""
        self.snake1_selection = 0
        self.snake2_selection = 0
        self.state = MenuState.SELECTING_SNAKE1
        self.frame_count = 0
        logger.debug("Menu reset to initial state")