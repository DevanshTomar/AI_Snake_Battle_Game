"""
AI Snake Battle Game - Main Entry Point

This module serves as the main entry point for the AI Snake Battle game.
It initializes the game window, handles the game loop, and manages user input.

The game features two AI-controlled snakes competing against each other using
different strategies (Balanced, Aggressive, or Defensive).

Author: Devansh Tomar
Version: 1.0.0
License: MIT

Usage:
    python main.py
"""

import pygame
import sys
import logging
import traceback
from typing import Optional, Tuple

from config import WINDOW_WIDTH, WINDOW_HEIGHT, FPS
from game.game_state import GameState, GameStateError
from ui.renderer import Renderer, RenderError
from ui.menu import AISelectionMenu, MenuError

# Configure logging for the main module
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('game.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SnakeGame:
    """
    Main game class that manages the game lifecycle.
    
    This class handles:
    - Game initialization and setup
    - Main game loop
    - Event handling (keyboard input)
    - Game state management
    - Error recovery
    
    Attributes:
        screen: Pygame display surface
        clock: Pygame clock for FPS control
        renderer: Game renderer for visual output
        game_state: Current game state
        running: Boolean flag for game loop control
    """
    
    def __init__(self):
        """
        Initialize the Snake Game.
        
        Sets up pygame, creates the game window, initializes the renderer,
        and starts the AI selection process.
        
        Raises:
            SystemExit: If initialization fails or user cancels during menu
        """
        try:
            # Initialize Pygame with error handling
            logger.info("Initializing Pygame...")
            pygame.init()
            
            # Verify pygame modules are loaded
            if not pygame.font.get_init():
                logger.warning("Pygame font module not initialized, attempting to initialize...")
                pygame.font.init()
            
            # Create game window with error handling
            logger.info(f"Creating game window: {WINDOW_WIDTH}x{WINDOW_HEIGHT}")
            self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
            pygame.display.set_caption("AI Snake Battle")
            
            # Set window icon if possible (optional enhancement)
            try:
                # You could add a custom icon here
                # icon = pygame.image.load("icon.png")
                # pygame.display.set_icon(icon)
                pass
            except Exception as e:
                logger.debug(f"Could not set window icon: {e}")
            
            # Initialize game clock for FPS control
            self.clock = pygame.time.Clock()
            
            # Initialize renderer with error handling
            try:
                self.renderer = Renderer(self.screen)
                logger.info("Renderer initialized successfully")
            except RenderError as e:
                logger.error(f"Failed to initialize renderer: {e}")
                raise SystemExit(f"Renderer initialization failed: {e}")
            
            # Show AI selection menu and get user choices
            self.game_state = self._initialize_game_with_menu()
            
            # Initialize game statistics tracking
            self.frame_count = 0
            self.error_count = 0
            self.max_consecutive_errors = 10
            
            logger.info("Game initialization completed successfully")
            
        except pygame.error as e:
            # Handle pygame-specific errors
            logger.critical(f"Pygame error during initialization: {e}")
            self._cleanup()
            raise SystemExit(f"Failed to initialize game: {e}")
            
        except Exception as e:
            # Handle any other unexpected errors
            logger.critical(f"Unexpected error during initialization: {e}")
            logger.debug(traceback.format_exc())
            self._cleanup()
            raise SystemExit(f"Game initialization failed: {e}")
    
    def _initialize_game_with_menu(self) -> GameState:
        """
        Show AI selection menu and initialize game state with selected AIs.
        
        Returns:
            GameState: Initialized game state with selected AI types
            
        Raises:
            SystemExit: If user cancels menu or menu fails
        """
        try:
            # Create and run AI selection menu
            logger.info("Showing AI selection menu...")
            menu = AISelectionMenu(self.screen)
            ai_selection = menu.run()
            
            if ai_selection:
                ai1_type, ai2_type = ai_selection
                logger.info(f"AI selection completed: {ai1_type} vs {ai2_type}")
                
                # Create game state with selected AI types
                try:
                    game_state = GameState(ai1_type, ai2_type)
                    return game_state
                except GameStateError as e:
                    logger.error(f"Failed to create game state: {e}")
                    raise SystemExit(f"Could not start game: {e}")
            else:
                # User cancelled menu
                logger.info("User cancelled AI selection")
                raise SystemExit("Game cancelled by user")
                
        except MenuError as e:
            logger.error(f"Menu error: {e}")
            raise SystemExit(f"Menu failed: {e}")
        except SystemExit:
            # Re-raise SystemExit to properly exit
            raise
        except Exception as e:
            logger.error(f"Unexpected error in menu: {e}")
            raise SystemExit(f"Menu error: {e}")
    
    def handle_events(self) -> bool:
        """
        Handle all game events including keyboard input and window events.
        
        Processes:
        - Window close events
        - Q key: Quit game
        - R key: Restart game with new AI selection
        - ESC key: Quit game (alternative)
        
        Returns:
            bool: True to continue game loop, False to exit
        """
        try:
            # Process all pending events
            for event in pygame.event.get():
                # Handle window close button
                if event.type == pygame.QUIT:
                    logger.info("Window close requested")
                    return False
                
                # Handle keyboard input
                elif event.type == pygame.KEYDOWN:
                    # Quit game
                    if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                        logger.info(f"Quit requested via {pygame.key.name(event.key)} key")
                        return False
                    
                    # Restart game
                    elif event.key == pygame.K_r:
                        logger.info("Restart requested")
                        return self._handle_restart()
                    
                    # Log any other key presses for debugging
                    else:
                        logger.debug(f"Unhandled key press: {pygame.key.name(event.key)}")
            
            return True
            
        except Exception as e:
            # Log error but try to continue
            logger.error(f"Error handling events: {e}")
            self.error_count += 1
            
            # If too many errors, exit gracefully
            if self.error_count >= self.max_consecutive_errors:
                logger.critical(f"Too many consecutive errors ({self.error_count}), exiting")
                return False
            
            return True
    
    def _handle_restart(self) -> bool:
        """
        Handle game restart by showing menu again and creating new game state.
        
        Returns:
            bool: True if restart successful, False if user cancels
        """
        try:
            logger.info("Attempting to restart game...")
            
            # Show AI selection menu again
            menu = AISelectionMenu(self.screen)
            ai_selection = menu.run()
            
            if ai_selection:
                ai1_type, ai2_type = ai_selection
                logger.info(f"Restart with new AI selection: {ai1_type} vs {ai2_type}")
                
                # Create new game state
                try:
                    self.game_state = GameState(ai1_type, ai2_type)
                    self.error_count = 0  # Reset error count on successful restart
                    return True
                except GameStateError as e:
                    logger.error(f"Failed to create new game state: {e}")
                    # Show error message to user
                    self._show_error_message(f"Failed to restart: {e}")
                    return True  # Keep current game running
            else:
                # User cancelled restart
                logger.info("Restart cancelled by user")
                return False
                
        except Exception as e:
            logger.error(f"Error during restart: {e}")
            # Continue with current game on restart failure
            return True
    
    def run(self):
        """
        Main game loop that runs continuously until exit is requested.
        
        The loop:
        1. Handles user input events
        2. Updates game state
        3. Renders the current frame
        4. Controls frame rate
        
        This method includes comprehensive error handling to ensure the game
        remains stable even if individual components fail.
        """
        logger.info("Starting main game loop")
        running = True
        consecutive_update_errors = 0
        consecutive_render_errors = 0
        max_errors = 5
        
        try:
            while running:
                # Reset error count on successful frame
                frame_success = True
                
                # 1. Handle input events
                try:
                    running = self.handle_events()
                except Exception as e:
                    logger.error(f"Critical error in event handling: {e}")
                    frame_success = False
                
                # 2. Update game state (if still running)
                if running:
                    try:
                        self.game_state.update()
                        consecutive_update_errors = 0  # Reset on success
                    except GameStateError as e:
                        logger.error(f"Game state error: {e}")
                        consecutive_update_errors += 1
                        frame_success = False
                    except Exception as e:
                        logger.error(f"Unexpected error updating game state: {e}")
                        logger.debug(traceback.format_exc())
                        consecutive_update_errors += 1
                        frame_success = False
                    
                    # Check if too many update errors
                    if consecutive_update_errors >= max_errors:
                        logger.critical(f"Too many consecutive update errors ({consecutive_update_errors})")
                        self._show_error_message("Game state corrupted. Please restart.")
                        running = False
                        continue
                
                # 3. Render current frame
                if running:
                    try:
                        self.renderer.draw(self.game_state)
                        consecutive_render_errors = 0  # Reset on success
                    except RenderError as e:
                        logger.error(f"Render error: {e}")
                        consecutive_render_errors += 1
                        frame_success = False
                    except Exception as e:
                        logger.error(f"Unexpected error rendering frame: {e}")
                        logger.debug(traceback.format_exc())
                        consecutive_render_errors += 1
                        frame_success = False
                    
                    # Check if too many render errors
                    if consecutive_render_errors >= max_errors:
                        logger.critical(f"Too many consecutive render errors ({consecutive_render_errors})")
                        self._show_error_message("Display error. Please restart.")
                        running = False
                        continue
                
                # 4. Control frame rate
                try:
                    self.clock.tick(FPS)
                    self.frame_count += 1
                    
                    # Log performance stats periodically
                    if self.frame_count % (FPS * 10) == 0:  # Every 10 seconds
                        actual_fps = self.clock.get_fps()
                        logger.debug(f"Performance: {actual_fps:.1f} FPS (target: {FPS})")
                        
                except Exception as e:
                    logger.error(f"Error controlling frame rate: {e}")
                
                # Reset general error count on successful frame
                if frame_success:
                    self.error_count = 0
                else:
                    self.error_count += 1
                    
                    # Emergency exit if too many general errors
                    if self.error_count >= self.max_consecutive_errors:
                        logger.critical("Too many consecutive errors, forcing exit")
                        running = False
        
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            logger.info("Game interrupted by user (Ctrl+C)")
        except Exception as e:
            # Catch any other unexpected errors
            logger.critical(f"Unexpected error in main loop: {e}")
            logger.debug(traceback.format_exc())
        finally:
            # Always clean up resources
            logger.info("Exiting game loop")
            self._cleanup()
    
    def _show_error_message(self, message: str):
        """
        Display an error message on screen for a brief period.
        
        Args:
            message: Error message to display
        """
        try:
            # Create a simple error overlay
            font = pygame.font.Font(None, 36)
            text = font.render(message, True, (255, 0, 0))
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            
            # Draw error message
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            self.screen.blit(text, text_rect)
            pygame.display.flip()
            
            # Show for 2 seconds
            pygame.time.wait(2000)
            
        except Exception as e:
            # If we can't show the error visually, just log it
            logger.error(f"Could not display error message: {e}")
    
    def _cleanup(self):
        """
        Clean up pygame resources before exit.
        
        This method ensures proper cleanup even if errors occur during shutdown.
        """
        try:
            logger.info("Cleaning up resources...")
            pygame.quit()
            logger.info("Cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


def main():
    """
    Main entry point for the AI Snake Battle game.
    
    This function:
    1. Displays a welcome message
    2. Creates and runs the game
    3. Handles any top-level exceptions
    4. Ensures proper exit
    """
    try:
        # Display welcome message
        print("=" * 50)
        print("Welcome to AI Snake Battle!")
        print("=" * 50)
        print("Watch as AI-controlled snakes compete for survival!")
        print("\nControls:")
        print("  R - Restart with new AI selection")
        print("  Q - Quit game")
        print("  ESC - Quit game")
        print("=" * 50)
        
        # Create and run the game
        game = SnakeGame()
        game.run()
        
    except SystemExit as e:
        # Handle clean exit
        logger.info(f"System exit: {e}")
        print(f"\nGame exited: {e}")
    except KeyboardInterrupt:
        # Handle Ctrl+C
        logger.info("Game interrupted by user")
        print("\nGame interrupted by user")
    except Exception as e:
        # Handle any unexpected errors
        logger.critical(f"Unexpected error in main: {e}")
        logger.debug(traceback.format_exc())
        print(f"\nUnexpected error: {e}")
        print("Please check game.log for details")
    finally:
        # Ensure pygame is properly shut down
        try:
            pygame.quit()
        except:
            pass
        
        # Exit cleanly
        sys.exit()


# Entry point when script is run directly
if __name__ == "__main__":
    main()