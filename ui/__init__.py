"""
UI Package for AI Snake Battle

This package contains all user interface components including:
- Menu systems for AI selection
- Game rendering and visualization
- UI elements and overlays

Author: Devansh Tomar
Version: 1.0.0
"""

from .menu import AISelectionMenu, MenuError
from .renderer import Renderer, RenderError

__all__ = [
    'AISelectionMenu',
    'MenuError',
    'Renderer',
    'RenderError'
]

__version__ = '1.0.0'