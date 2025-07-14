import pynvim
from lark import Lark, Transformer
from typing import Any, List
import os
from pathlib import Path


class NvimDSLTransformer(Transformer):
    """
    Transformer class that converts DSL parse trees into actual Neovim operations.

    This class implements each DSL command using the pynvim API to interact
    with a Neovim instance.
    """

    def __init__(self, nvim_instance: pynvim.Nvim):
        """
        Initialize the transformer with a pynvim instance.

        Args:
            nvim_instance: Connected pynvim.Nvim instance
        """
        super().__init__()
        self.nvim = nvim_instance
        self.buffer = nvim_instance.current.buffer

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
        """
        Execute VISUAL LINES start TO end command.

        Selects the specified line range in visual line mode.
        Uses Neovim's visual selection commands.
        """
        start_line = int(items[0])
        end_line = int(items[1])

        try:
            # Move cursor to start line
            self.nvim.api.win_set_cursor(0, [start_line, 0])

            # Enter visual line mode and select to end line
            # V enters visual line mode, then G goes to specific line
            self.nvim.command("normal! V")
            self.nvim.api.win_set_cursor(0, [end_line, 0])

            return f"Selected lines {start_line} to {end_line}"

        except Exception as e:
            return f"Error selecting lines {start_line}-{end_line}: {e}"

    def insert_text(self, items: List[Any]) -> str:
        """
        Execute INSERT "text" [AT LINE n] command.

        Inserts text at cursor position or at specified line.
        Uses nvim_buf_set_lines for precise line insertion.
        """
        text = items[0].strip('"')  # Remove quotes from string
        line_num = None

        # Check if AT LINE was specified
        if len(items) > 1 and items[1] is not None:
            line_num = int(items[1])

        try:
            if line_num is not None:
                # Insert at specific line (convert to 0-based indexing)
                line_idx = line_num - 1

                # Get current line content and insert new text
                current_lines = self.buffer[:]
                current_lines.insert(line_idx, text)
                self.buffer[:] = current_lines

                return f"Inserted '{text}' at line {line_num}"
            else:
                # Insert at current cursor position
                cursor_pos = self.nvim.api.win_get_cursor(0)
                current_line = cursor_pos[0] - 1  # Convert to 0-based

                # Insert new line after current position
                current_lines = self.buffer[:]
                current_lines.insert(current_line + 1, text)
                self.buffer[:] = current_lines

                return f"Inserted '{text}' at current position"

        except Exception as e:
            return f"Error inserting text: {e}"

    def delete_lines(self, items: List[Any]) -> str:
        """
        Execute DELETE LINES start TO end command.

        Deletes the specified range of lines from the buffer.
        Uses nvim_buf_set_lines with empty list to delete.
        """
        start_line = int(items[0])
        end_line = int(items[1])

        try:
            # Convert to 0-based indexing for API
            start_idx = start_line - 1
            end_idx = end_line  # end is exclusive in nvim_buf_set_lines

            # Delete lines by setting range to empty list
            self.nvim.api.buf_set_lines(0, start_idx, end_idx, False, [])

            return f"Deleted lines {start_line} to {end_line}"

        except Exception as e:
            return f"Error deleting lines {start_line}-{end_line}: {e}"

    def goto_line(self, items: List[Any]) -> str:
        """
        Execute GOTO LINE n command.

        Moves cursor to the specified line number.
        Uses nvim_win_set_cursor for precise positioning.
        """
        line_num = int(items[0])

        try:
            # Move cursor to specified line (column 0)
            self.nvim.api.win_set_cursor(0, [line_num, 0])

            return f"Moved to line {line_num}"

        except Exception as e:
            return f"Error going to line {line_num}: {e}"

    def find_text(self, items: List[Any]) -> str:
        """
        Execute FIND "pattern" command.

        Searches for the specified pattern and moves cursor to first match.
        Uses Neovim's search command (/) for consistency with editor behavior.
        """
        pattern = items[0].strip('"')  # Remove quotes

        try:
            # Use Neovim's search command
            # The 'n' flag means don't jump to match, 'W' means don't wrap
            search_result = self.nvim.call("search", pattern, "nW")

            if search_result > 0:
                # Pattern found, move cursor to match
                self.nvim.command(f"/{pattern}")
                return f"Found '{pattern}' at line {search_result}"
            else:
                return f"Pattern '{pattern}' not found"

        except Exception as e:
            return f"Error searching for '{pattern}': {e}"

    def replace_text(self, items: List[Any]) -> str:
        """
        Execute REPLACE "old" WITH "new" command.

        Replaces all occurrences of old pattern with new text.
        Uses Neovim's substitute command (:s) for powerful replacement.
        """
        old_pattern = items[0].strip('"')  # Remove quotes
        new_text = items[1].strip('"')  # Remove quotes

        try:
            # Use substitute command to replace all occurrences in file
            # %s = all lines, g = all occurrences per line
            substitute_cmd = f"%s/{old_pattern}/{new_text}/g"

            # Execute the substitute command
            self.nvim.command(substitute_cmd)

            return f"Replaced all '{old_pattern}' with '{new_text}'"

        except Exception as e:
            return f"Error replacing '{old_pattern}' with '{new_text}': {e}"

    def at_line(self, items: List[Any]) -> int:
        """Process AT LINE n clause."""
        return int(items[0])

    # Handle terminal tokens
    def STRING(self, token: str) -> str:
        return str(token)

    def NUMBER(self, token: str) -> str:
        return str(token)


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
        if grammar_file is None:
            # Default to stvim.lark in the grammars directory
            current_dir = Path(__file__).parent.parent
            grammar_file = current_dir / "grammars" / "stvim.lark"

        # Load grammar from file
        with open(grammar_file, "r") as f:
            grammar_content = f.read()

        self.parser = Lark(grammar_content, parser="lalr")
        self.transformer = NvimDSLTransformer(nvim_instance)
        self.nvim = nvim_instance

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
