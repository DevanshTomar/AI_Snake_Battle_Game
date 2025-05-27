"""Game configuration constants"""

# Window dimensions
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 700
UI_HEIGHT = 100
GAME_HEIGHT = WINDOW_HEIGHT - UI_HEIGHT

# Grid settings
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = GAME_HEIGHT // GRID_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)

# Snake 1 - Orange theme
ORANGE = (255, 165, 0)
DARK_ORANGE = (255, 140, 0)

# Snake 2 - Cyan theme  
CYAN = (0, 255, 255)
DARK_CYAN = (0, 200, 200)

# Game settings
FPS = 20  # Game speed
FOOD_SCORE = 10