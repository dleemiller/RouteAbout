"""
UI components for terminal interaction and display.

This module provides reusable components for enhanced terminal input,
Rich-based display functions, and demo utilities.
"""

# Import and re-export all components
from .prompt import SimplePrompt, console, USING_PROMPT_TOOLKIT, USING_READLINE
from .display import (
    show_welcome,
    show_commands,
    show_buffer,
    execute_and_display,
    show_help,
    show_history,
    show_interactive_instructions,
)
from .demo_utils import setup_demo_buffer

# Make everything available at package level
__all__ = [
    "SimplePrompt",
    "console",
    "USING_PROMPT_TOOLKIT",
    "USING_READLINE",
    "show_welcome",
    "show_commands",
    "show_buffer",
    "execute_and_display",
    "show_help",
    "show_history",
    "show_interactive_instructions",
    "setup_demo_buffer",
]
