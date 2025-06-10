"""
Game Package for AI Snake Battle

This package contains the core game logic including:
- Game state management
- AI controllers and strategies
- Game mechanics and rules

Author: Devansh Tomar
Version: 1.0.0
"""

from .game_state import GameState, GameStateError
from .ai_controller import AIController, AIError
from .ai_strategies import BalancedAI, AggressiveAI, DefensiveAI

__all__ = [
    'GameState', 
    'GameStateError',
    'AIController', 
    'AIError',
    'BalancedAI', 
    'AggressiveAI', 
    'DefensiveAI'
]

__version__ = '1.0.0'