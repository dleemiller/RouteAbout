"""
Base transformer class for converting DSL parse trees into Neovim operations.

This module handles the tree transformation logic and delegates actual
command execution to the command implementations.
"""

import pynvim
from lark import Transformer
from typing import Any, List

from .commands import (
    visual_lines_command,
    insert_text_command,
    delete_command,
    delete_lines_command,
    goto_line_command,
    find_text_command,
    replace_text_command,
)


class NvimDSLTransformer(Transformer):
    """
    Transformer class that converts DSL parse trees into actual Neovim operations.

    This class handles the tree transformation and delegates command execution
    to individual command functions for better modularity.
    """

    def __init__(self, nvim_instance: pynvim.Nvim):
        """
        Initialize the transformer with a pynvim instance.

        Args:
            nvim_instance: Connected pynvim.Nvim instance
        """
        super().__init__()
        self.nvim = nvim_instance

    def start(self, items: List[Any]) -> List[Any]:
        """Process all commands in sequence."""
        results = []
        for item in items:
            if item is not None:
                results.append(item)
        return results

    def command(self, items: List[Any]) -> Any:
        """Execute a single command."""
        return items[0]

    def visual_lines(self, items: List[Any]) -> str:
        """Transform VISUAL LINES command."""
        start_line = int(items[0])
        end_line = int(items[1])
        return visual_lines_command(self.nvim, start_line, end_line)

    def insert_text(self, items: List[Any]) -> str:
        """Transform INSERT command (supports both single-line and multi-line text)."""
        # First item is the text (either STRING or MULTILINE_STRING)
        text = items[0]

        # Remove quotes based on string type
        if text.startswith('"""') and text.endswith('"""'):
            # Multi-line string - strip triple quotes
            text = text[3:-3]
        else:
            # Regular string - strip single/double quotes
            text = text.strip("\"'")

        line_num = None

        # Check if AT LINE was specified
        if len(items) > 1 and items[1] is not None:
            line_num = int(items[1])

        return insert_text_command(self.nvim, text, line_num)

    def delete_command(self, items: List[Any]) -> str:
        """Transform DELETE command (with optional target)."""
        if not items or items[0] is None:
            # No target specified - regular DELETE (character/selection)
            return delete_command(self.nvim)
        else:
            # Target specified - should be handled by delete_target -> lines_range
            return items[0]

    def delete_target(self, items: List[Any]) -> str:
        """Process delete target (currently only lines_range)."""
        return items[0]

    def lines_range(self, items: List[Any]) -> str:
        """Transform LINES start TO end."""
        start_line = int(items[0])
        end_line = int(items[1])
        return delete_lines_command(self.nvim, start_line, end_line)

    def goto_line(self, items: List[Any]) -> str:
        """Transform GOTO LINE command."""
        line_num = int(items[0])
        return goto_line_command(self.nvim, line_num)

    def find_text(self, items: List[Any]) -> str:
        """Transform FIND command."""
        pattern = items[0].strip('"')  # Remove quotes
        return find_text_command(self.nvim, pattern)

    def replace_text(self, items: List[Any]) -> str:
        """Transform REPLACE command."""
        old_pattern = items[0].strip('"')  # Remove quotes
        new_text = items[1].strip('"')  # Remove quotes
        return replace_text_command(self.nvim, old_pattern, new_text)

    def at_line(self, items: List[Any]) -> int:
        """Process AT LINE n clause."""
        return int(items[0])

    # Handle terminal tokens
    def STRING(self, token: str) -> str:
        """Process STRING tokens (single-line quoted strings)."""
        return str(token)

    def MULTILINE_STRING(self, token: str) -> str:
        """Process MULTILINE_STRING tokens (triple-quoted strings)."""
        return str(token)

    def NUMBER(self, token: str) -> str:
        """Process NUMBER tokens."""
        return str(token)
