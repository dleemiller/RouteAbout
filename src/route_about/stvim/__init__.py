"""
Neovim DSL Transformers Package

This package provides the core functionality for parsing and executing
DSL commands against a Neovim instance.

Main Classes:
    NvimDSLExecutor: Primary interface for executing DSL commands
    NvimDSLTransformer: Handles parse tree transformation

Exceptions:
    ExecutorError: Base exception for executor errors
    GrammarError: Grammar-related errors
    CommandError: Command execution errors
"""

from .executor import NvimDSLExecutor, ExecutorError, GrammarError, CommandError
from .transformer import NvimDSLTransformer
from .commands import (
    visual_lines_command,
    insert_text_command,
    delete_lines_command,
    goto_line_command,
    find_text_command,
    replace_text_command,
    get_command_function,
    list_available_commands,
    COMMAND_REGISTRY,
)

# Main exports - what users typically need
__all__ = [
    # Primary classes
    "NvimDSLExecutor",
    "NvimDSLTransformer",
    # Exceptions
    "ExecutorError",
    "GrammarError",
    "CommandError",
    # Command functions (for advanced usage)
    "visual_lines_command",
    "insert_text_command",
    "delete_lines_command",
    "goto_line_command",
    "find_text_command",
    "replace_text_command",
    # Utilities
    "get_command_function",
    "list_available_commands",
    "COMMAND_REGISTRY",
]

# Package metadata
__version__ = "0.1.0"
__author__ = "DSL Project"
__description__ = "Neovim DSL command parser and executor"
