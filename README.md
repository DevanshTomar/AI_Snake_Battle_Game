# AI Snake Battle 🐍⚔️🐍

A competitive two-player Snake game where AI-controlled snakes battle for survival and dominance. Watch as Orange and Cyan snakes compete using intelligent pathfinding algorithms and strategic decision-making in real-time.

## 📋 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [AI Algorithm](#ai-algorithm)
- [Snake Behaviors](#snake-behaviors)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Game Mechanics](#game-mechanics)
- [Configuration](#configuration)
- [Contributing](#contributing)

## Overview

AI Snake Battle is an autonomous snake game where two AI-controlled snakes compete against each other in a grid-based arena. The game showcases pathfinding algorithms, collision detection, and competitive AI behaviors. No human input is required during gameplay - sit back and watch the snakes battle it out!

### Key Highlights:
- **Fully Autonomous**: Both snakes are controlled by AI
- **Real-time Pathfinding**: Using BFS (Breadth-First Search) algorithm
- **Competitive Strategy**: Snakes can block each other and compete for food
- **Dynamic Decision Making**: AI adapts based on game state
- **Visual Feedback**: Clear UI showing scores, status, and game statistics

## Features

- **Multiple AI Strategies**: Choose between Balanced, Aggressive, and Defensive AI behaviors
- **Strategy Selection Menu**: User-friendly menu to select AI types for both snakes
- **Smart Pathfinding**: BFS-based navigation with obstacle avoidance
- **Competitive Behaviors**: Food racing, blocking, and survival strategies
- **Collision Detection**: Wall, self, and snake-to-snake collision handling
- **Score Tracking**: Points awarded for food consumption
- **Game States**: Running, game over, and winner declaration
- **Visual UI**: Real-time stats, scores, and game information
- **Fast-paced Action**: Optimized for exciting AI battles

## AI Algorithm

### Pathfinding: Breadth-First Search (BFS)

The game uses BFS for pathfinding, which guarantees finding the shortest path to the food when one exists.

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

The AI makes decisions in the following priority order:

1. **Path to Food**: If a clear path exists, follow it
2. **Competitive Blocking**: If the opponent is closer to food, try to block
3. **Direct Movement**: Move toward food even without a clear path
4. **Survival Mode**: If no safe food path exists, find any safe direction

## Snake Behaviors

### Available AI Strategies

#### Balanced AI
- **Behavior**: Equal focus on food pursuit and survival
- **Food Pursuit**: Follows shortest path to food when available
- **Competitive**: Considers opponent's position when making decisions
- **Risk Assessment**: Takes moderate risks for food acquisition

#### Aggressive AI
- **Behavior**: Prioritizes blocking opponent and taking risks
- **Food Pursuit**: Directly moves toward food even without clear path
- **Blocking**: Actively tries to cut off opponent's path to food
- **Risk Assessment**: Willing to take high risks for competitive advantage

#### Defensive AI
- **Behavior**: Prioritizes survival and avoiding risks
- **Food Pursuit**: Only follows safe paths to food
- **Safety**: Maintains distance from walls and opponent
- **Risk Assessment**: Prefers positions with multiple escape routes

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
   
   The requirements.txt file includes:
   - pygame>=2.0.0

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

### Watching the Battle

The game runs automatically once AI strategies are selected. You can:
- Observe different AI strategies competing against each other
- Monitor scores and statistics in the UI panel
- Watch for interesting emergent behaviors
- Analyze which strategies perform better in different scenarios

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

- **main.py**: Game initialization and main loop
- **config.py**: Centralized configuration (sizes, colors, speeds)
- **enums.py**: Direction enumeration for snake movement
- **models/snake.py**: Snake data structure and methods
- **game/game_state.py**: Game rules and state management
- **game/ai_controller.py**: AI logic and decision making
- **ui/renderer.py**: All rendering and visual elements
- **utils/pathfinding.py**: Pathfinding algorithms and utilities

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

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [Pygame](https://www.pygame.org/)
- Inspired by classic Snake games
- BFS algorithm implementation based on graph theory principles

---

**Enjoy watching the AI snakes battle!**
