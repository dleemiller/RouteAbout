"""
Main DSL executor for parsing and executing Neovim DSL commands.

This module handles grammar loading, parsing, and coordination between
the parser and transformer components.
"""

import pynvim
from lark import Lark
from typing import List
from pathlib import Path

from .transformer import NvimDSLTransformer


class NvimDSLExecutor:
    """
    Main executor class that combines parsing and transformation.

    This class provides a simple interface to parse DSL commands and
    execute them on a Neovim instance.
    """

    def __init__(self, nvim_instance: pynvim.Nvim, grammar_file: str = None):
        """
        Initialize executor with Neovim instance.

        Args:
            nvim_instance: Connected pynvim.Nvim instance
            grammar_file: Path to .lark grammar file (optional)
        """
        self.nvim = nvim_instance
        self.grammar_file = self._resolve_grammar_file(grammar_file)
        self.parser = self._load_parser()
        self.transformer = NvimDSLTransformer(nvim_instance)

    def _resolve_grammar_file(self, grammar_file: str = None) -> Path:
        """
        Resolve the path to the grammar file.

        Args:
            grammar_file: Optional explicit path to grammar file

        Returns:
            Path object pointing to the grammar file
        """
        if grammar_file is not None:
            return Path(grammar_file)

        # Default to stvim.lark in the grammars directory
        current_dir = Path(__file__).parent.parent
        grammar_path = current_dir / "grammars" / "stvim.lark"

        if not grammar_path.exists():
            raise FileNotFoundError(f"Grammar file not found: {grammar_path}")

        return grammar_path

    def _load_parser(self) -> Lark:
        """
        Load the Lark parser from the grammar file.

        Returns:
            Configured Lark parser instance
        """
        try:
            with open(self.grammar_file, "r") as f:
                grammar_content = f.read()

            return Lark(grammar_content, parser="lalr")

        except FileNotFoundError:
            raise FileNotFoundError(f"Grammar file not found: {self.grammar_file}")
        except Exception as e:
            raise RuntimeError(f"Error loading grammar: {e}")

    def execute(self, dsl_command: str) -> str:
        """
        Parse and execute a DSL command.

        Args:
            dsl_command: DSL command string to execute

        Returns:
            Result message from command execution
        """
        try:
            # Parse the command
            parse_tree = self.parser.parse(dsl_command)

            # Transform and execute
            result = self.transformer.transform(parse_tree)

            # Return the result (should be a list with one item)
            if isinstance(result, list) and len(result) > 0:
                return result[0]
            else:
                return str(result)

        except Exception as e:
            return f"Error executing '{dsl_command}': {e}"

    def execute_batch(self, commands: List[str]) -> List[str]:
        """
        Execute multiple DSL commands in sequence.

        Args:
            commands: List of DSL command strings

        Returns:
            List of result messages
        """
        results = []
        for cmd in commands:
            results.append(self.execute(cmd))
        return results

    def validate_command(self, dsl_command: str) -> bool:
        """
        Validate a DSL command without executing it.

        Args:
            dsl_command: DSL command string to validate

        Returns:
            True if command is valid, False otherwise
        """
        try:
            self.parser.parse(dsl_command)
            return True
        except Exception:
            return False

    def get_parse_tree(self, dsl_command: str):
        """
        Get the parse tree for a DSL command without executing it.

        Args:
            dsl_command: DSL command string to parse

        Returns:
            Lark Tree object representing the parsed command
        """
        return self.parser.parse(dsl_command)

    def reload_grammar(self):
        """
        Reload the grammar file and recreate the parser.

        Useful for development when the grammar is being modified.
        """
        self.parser = self._load_parser()

    @property
    def grammar_path(self) -> str:
        """Get the path to the currently loaded grammar file."""
        return str(self.grammar_file)


class ExecutorError(Exception):
    """Base exception for executor-related errors."""

    pass


class GrammarError(ExecutorError):
    """Exception raised when there are grammar-related errors."""

    pass


class CommandError(ExecutorError):
    """Exception raised when there are command execution errors."""

    pass
