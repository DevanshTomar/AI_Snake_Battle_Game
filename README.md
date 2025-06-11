# AI Snake Battle 🐍⚔️🐍

A sophisticated Python game where two AI-controlled snakes compete against each other in real-time. This project showcases advanced AI concepts, clean software architecture, and sophisticated game development techniques with multiple AI strategies, intelligent pathfinding algorithms, and polished user interface.

## 📋 Table of Contents
- [Project Overview](#project-overview)
- [Core Architecture](#core-architecture)
- [Key Features](#key-features)
- [AI Strategies](#ai-strategies)
- [Technical Quality](#technical-quality)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Game Mechanics](#game-mechanics)
- [Configuration](#configuration)
- [Extending the Game](#extending-the-game)
- [Contributing](#contributing)

## Project Overview

**AI Snake Battle** is a production-quality game that demonstrates excellent software engineering practices combined with advanced AI concepts. Two AI-controlled snakes compete in a grid-based arena using intelligent pathfinding algorithms and strategic decision-making. The game features a modular architecture with well-separated concerns, comprehensive error handling, and performance optimizations.

### Key Highlights:
- **Multiple AI Personalities**: Three distinct AI strategies with unique behaviors
- **Advanced Pathfinding**: BFS algorithm with intelligent obstacle avoidance
- **Production Code Quality**: Type hints, comprehensive documentation, robust error handling
- **Real-time Competition**: Dynamic AI adaptation based on game state
- **Performance Optimized**: Cached rendering, FPS monitoring, efficient algorithms
- **User-Friendly Interface**: Interactive menu system and polished visuals

## Core Architecture

The project follows a clean modular architecture with well-separated concerns:

### Main Components
- **`main.py`** - Entry point with comprehensive error handling and game lifecycle management
- **`config.py`** - Centralized configuration for all game settings  
- **`enums.py`** - Direction enumeration for snake movement

### Game Logic (`game/` module)
- **`game_state.py`** - Core game state manager handling snakes, food, collisions, and win conditions
- **`ai_controller.py`** - Abstract base class for AI decision making with safety mechanisms
- **`ai_strategies.py`** - Three distinct AI implementations (Balanced, Aggressive, Defensive)

### Models (`models/` module)
- **`snake.py`** - Snake entity with movement, collision detection, and statistics tracking

### UI (`ui/` module)
- **`renderer.py`** - Comprehensive rendering system with performance optimizations
- **`menu.py`** - Interactive AI selection menu with smooth navigation

### Utilities (`utils/` module)
- **`pathfinding.py`** - Advanced pathfinding algorithms (BFS, A*) with obstacle detection

## Key Features

### 1. **AI Strategy System**
Three distinct AI personalities with unique decision-making patterns:
- **Balanced AI**: Equilibrium between aggression and safety
- **Aggressive AI**: Prioritizes blocking opponents and risk-taking  
- **Defensive AI**: Focuses on survival and careful play

### 2. **Advanced Pathfinding**
- BFS (Breadth-First Search) algorithm guaranteeing shortest paths
- A* pathfinding for complex scenarios
- Intelligent obstacle avoidance
- Dynamic path recalculation

### 3. **Comprehensive Game Mechanics**
- Multi-type collision detection (walls, self, snake-to-snake)
- Dynamic food generation with validation
- Real-time scoring and statistics tracking
- Graceful win/tie condition handling
- Performance monitoring and optimization

### 4. **Robust Error Handling**
- Extensive logging system for debugging and monitoring
- Graceful error recovery at multiple levels
- Validation and safety checks throughout
- Fallback mechanisms for critical operations

### 5. **Performance Optimized Rendering**
- Cached surfaces for improved performance
- FPS monitoring and display
- Smooth animations and visual effects
- Efficient draw calls and memory management

## Technical Quality

The codebase demonstrates excellent software engineering practices:

- **Type Hints**: Throughout codebase for better maintainability and IDE support
- **Comprehensive Documentation**: Detailed docstrings explaining functionality and usage
- **Modular Design**: Clear separation of concerns with well-defined interfaces
- **Error Handling**: Multiple levels of error recovery with graceful degradation
- **Logging System**: Comprehensive logging for debugging and monitoring
- **Configuration Management**: Centralized settings for easy customization
- **Performance Optimization**: Caching, efficient algorithms, and resource management

## AI Strategies

The game features three sophisticated AI strategies, each with unique decision-making patterns and behavioral characteristics:

### Pathfinding: Breadth-First Search (BFS)

All AI strategies use BFS for pathfinding, which guarantees finding the shortest path to the food when one exists.

#### How BFS Works in the Game:

1. **Graph Representation**: The game grid is treated as a graph where each cell is a node
2. **Queue-based Exploration**: Starting from the snake's head, BFS explores all neighboring cells level by level
3. **Obstacle Avoidance**: The algorithm marks cells containing snake bodies as obstacles
4. **Path Reconstruction**: Once food is found, the algorithm reconstructs the path from head to food

```python
def bfs_pathfind(start, target, obstacles):
    queue = [(start, [])]
    visited = {start}
    
    while queue:
        current, path = queue.pop(0)
        for neighbor in get_neighbors(current):
            if neighbor == target:
                return path + [neighbor]
            if neighbor not in visited and neighbor not in obstacles:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    return []  # No path found
```

### Decision Making Process

Each AI makes decisions following a priority hierarchy:

1. **Path to Food**: If a clear path exists, follow it
2. **Competitive Analysis**: Consider opponent's position and strategy
3. **Strategic Movement**: Execute strategy-specific behaviors
4. **Survival Mode**: If no safe food path exists, find any safe direction

### Available AI Strategies

#### 1. Balanced AI
- **Philosophy**: Equilibrium between aggression and safety
- **Decision Priority**: 
  1. Follow safe path to food if available
  2. Avoid opponent if they're closer to food
  3. Move toward food directly if safe
  4. Take any safe direction if no food path
- **Risk Assessment**: Takes moderate risks for food acquisition
- **Competitive Behavior**: Considers opponent's position when making decisions

#### 2. Aggressive AI  
- **Philosophy**: Prioritizes blocking opponents and risk-taking
- **Decision Priority**:
  1. Block opponent's path to food when possible
  2. Take direct path to food if available
  3. Move aggressively toward food even without clear path
  4. Avoid head-on collisions as last resort
- **Risk Assessment**: Willing to take high risks for competitive advantage
- **Competitive Behavior**: Actively tries to cut off opponent's path to food

#### 3. Defensive AI
- **Philosophy**: Prioritizes survival and avoiding risks
- **Decision Priority**:
  1. Ensure multiple escape routes
  2. Maintain distance from walls and opponent
  3. Only pursue food with safe, verified paths
  4. Choose positions with maximum safety score
- **Risk Assessment**: Prefers positions with multiple escape routes
- **Competitive Behavior**: Maintains distance from opponent and walls

### Competitive Behaviors

1. **Food Racing**
   - Calculates Manhattan distance to food
   - Compares distance with opponent
   - Chooses optimal path when winning the race

2. **Blocking Strategy**
   - When opponent is closer to food (within 3-5 cells)
   - Attempts to cut off opponent's path
   - Falls back to safe movement if blocking fails

3. **Survival Instinct**
   - Prioritizes avoiding immediate death
   - Checks all directions for safe moves
   - Avoids walls and snake bodies (including own tail)

4. **Opportunistic Movement**
   - Even without clear path, moves toward food
   - Takes calculated risks when necessary
   - Adapts strategy based on game state

## Dependencies

The project uses minimal, well-established dependencies:

- **`pygame>=2.1.0`** - Game framework and graphics library
- **`pathfinding>=1.0.1`** - Advanced pathfinding algorithms  
- **`numpy>=1.21.0`** - Numerical computations and array operations
- **`typing-extensions>=4.0.0`** - Enhanced type hints for better code quality

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/ai-snake-battle.git
   cd ai-snake-battle
   ```

2. **Create Virtual Environment** (Recommended)
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the Game

Navigate to the project directory and run:

```bash
python main.py
```

### AI Selection Menu

When you start the game, you'll see an AI selection menu:
1. Choose an AI strategy for the Orange snake (Balanced, Aggressive, or Defensive)
2. Press ENTER to confirm
3. Choose an AI strategy for the Cyan snake
4. Press ENTER to start the game

### Controls

- **Arrow Keys**: Navigate the AI selection menu
- **ENTER**: Confirm selection
- **R**: Restart the game (returns to AI selection menu)
- **Q**: Quit the game
- **Window Close**: Exit the game

### Game Flow

1. **Menu Phase**: Interactive AI strategy selection for both snakes
2. **Game Phase**: Real-time AI battle with pathfinding and collision detection  
3. **Results Phase**: Winner determination with comprehensive statistics
4. **Restart**: Return to menu for new AI combinations

### Watching the Battle

The game runs automatically once AI strategies are selected. You can:
- Observe different AI strategies competing against each other
- Monitor scores and statistics in the UI panel
- Watch for interesting emergent behaviors and strategy interactions
- Analyze which strategies perform better in different scenarios
- Observe the sophisticated pathfinding and decision-making in real-time

## Project Structure

```
AI_Snake_Battle_Game/
│
├── main.py                 # Entry point and game loop
├── config.py              # Game configuration and constants
├── enums.py               # Direction enumeration
│
├── models/
│   ├── __init__.py
│   └── snake.py           # Snake class and collision logic
│
├── game/
│   ├── __init__.py
│   ├── game_state.py      # Game state management
│   └── ai_controller.py   # AI decision making
│
├── ui/
│   ├── __init__.py
│   └── renderer.py        # Game rendering and UI
│
└── utils/
    ├── __init__.py
    └── pathfinding.py     # BFS and pathfinding utilities
```

### Module Descriptions

- **`main.py`**: Entry point with comprehensive error handling and game lifecycle management
- **`config.py`**: Centralized configuration for all game settings
- **`enums.py`**: Direction enumeration for snake movement
- **`models/snake.py`**: Snake entity with movement, collision detection, and statistics tracking
- **`game/game_state.py`**: Core game state manager handling snakes, food, collisions, and win conditions
- **`game/ai_controller.py`**: Abstract base class for AI decision making with safety mechanisms
- **`game/ai_strategies.py`**: Three distinct AI implementations (Balanced, Aggressive, Defensive)
- **`ui/renderer.py`**: Comprehensive rendering system with performance optimizations
- **`ui/menu.py`**: Interactive AI selection menu with smooth navigation
- **`utils/pathfinding.py`**: Advanced pathfinding algorithms (BFS, A*) with obstacle detection

## Game Mechanics

### Scoring System
- **Food Consumption**: +10 points
- **Length**: Increases by 1 segment per food
- **Winner**: Highest score when game ends

### Collision Rules
1. **Wall Collision**: Snake dies
2. **Self Collision**: Snake dies (hitting own body)
3. **Head-to-Head**: Both snakes die
4. **Head-to-Body**: Attacking snake dies

### Victory Conditions
- **Single Survivor**: Last snake alive wins
- **Both Dead**: Higher score wins
- **Tie**: Equal scores result in a tie

### Game Grid
- **Size**: 40x30 cells (800x600 pixels)
- **Cell Size**: 20x20 pixels
- **UI Height**: 100 pixels (separate from game area)

## Configuration

Edit `config.py` to customize:

```python
# Game Speed
FPS = 20  # Increase for faster game

# Window Dimensions
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 700

# Colors (RGB)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)

# Scoring
FOOD_SCORE = 10
```

### Difficulty Adjustments

1. **Increase Challenge**:
   - Increase FPS for faster gameplay
   - Reduce grid size for tighter space
   - Add more sophisticated blocking algorithms

2. **Modify AI Behavior**:
   - Adjust blocking distance threshold
   - Change path preference calculations
   - Add randomness for unpredictability

## Extending the Game

### Adding New Features

1. **Power-ups**
   ```python
   class PowerUp:
       def __init__(self, type, position):
           self.type = type  # speed, invincibility, etc.
           self.position = position
   ```

2. **Multiple AI Strategies**
   ```python
   class AggressiveAI(AIController):
       # Prioritize blocking over food
   
   class DefensiveAI(AIController):
       # Prioritize survival over scoring
   ```

3. **Obstacles**
   - Add static obstacles to the grid
   - Create moving obstacles
   - Implement destructible barriers

### Performance Optimization

- **Spatial Hashing**: For faster collision detection
- **A* Pathfinding**: For more efficient pathfinding
- **Caching**: Store calculated paths for reuse

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Areas for Contribution
- Additional AI strategies
- Performance optimizations
- New game modes
- Visual enhancements
- Documentation improvements

## Acknowledgments

- Built with [Pygame](https://www.pygame.org/)
- Inspired by classic Snake games
- BFS algorithm implementation based on graph theory principles

---

**Enjoy watching the AI snakes battle!**
