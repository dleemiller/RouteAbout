"""
Individual DSL command implementations.

Each command is implemented as a separate function that takes a pynvim instance
and command arguments, returning a result message.
"""

import pynvim
from typing import List, Any


def visual_lines_command(nvim: pynvim.Nvim, start_line: int, end_line: int) -> str:
    """
    Execute VISUAL LINES start TO end command.
    
    Selects the specified line range in visual line mode.
    Uses Neovim's visual selection commands.
    """
    try:
        # Move cursor to start line
        nvim.api.win_set_cursor(0, [start_line, 0])
        
        # Enter visual line mode and select to end line
        # V enters visual line mode, then G goes to specific line
        nvim.command('normal! V')
        nvim.api.win_set_cursor(0, [end_line, 0])
        
        return f"Selected lines {start_line} to {end_line}"
        
    except Exception as e:
        return f"Error selecting lines {start_line}-{end_line}: {e}"


def insert_text_command(nvim: pynvim.Nvim, text: str, line_num: int = None) -> str:
    """
    Execute INSERT "text" [AT LINE n] command.
    
    Inserts text at cursor position or at specified line.
    Uses buffer manipulation for precise line insertion.
    """
    try:
        buffer = nvim.current.buffer
        
        if line_num is not None:
            # Insert at specific line (convert to 0-based indexing)
            line_idx = line_num - 1
            
            # Get current line content and insert new text
            current_lines = buffer[:]
            current_lines.insert(line_idx, text)
            buffer[:] = current_lines
            
            return f"Inserted '{text}' at line {line_num}"
        else:
            # Insert at current cursor position
            cursor_pos = nvim.api.win_get_cursor(0)
            current_line = cursor_pos[0] - 1  # Convert to 0-based
            
            # Insert new line after current position
            current_lines = buffer[:]
            current_lines.insert(current_line + 1, text)
            buffer[:] = current_lines
            
            return f"Inserted '{text}' at current position"
            
    except Exception as e:
        return f"Error inserting text: {e}"


def delete_lines_command(nvim: pynvim.Nvim, start_line: int, end_line: int) -> str:
    """
    Execute DELETE LINES start TO end command.
    
    Deletes the specified range of lines from the buffer.
    Uses nvim_buf_set_lines with empty list to delete.
    """
    try:
        # Convert to 0-based indexing for API
        start_idx = start_line - 1
        end_idx = end_line  # end is exclusive in nvim_buf_set_lines
        
        # Delete lines by setting range to empty list
        nvim.api.buf_set_lines(0, start_idx, end_idx, False, [])
        
        return f"Deleted lines {start_line} to {end_line}"
        
    except Exception as e:
        return f"Error deleting lines {start_line}-{end_line}: {e}"


def goto_line_command(nvim: pynvim.Nvim, line_num: int) -> str:
    """
    Execute GOTO LINE n command.
    
    Moves cursor to the specified line number.
    Uses nvim_win_set_cursor for precise positioning.
    """
    try:
        # Move cursor to specified line (column 0)
        nvim.api.win_set_cursor(0, [line_num, 0])
        
        return f"Moved to line {line_num}"
        
    except Exception as e:
        return f"Error going to line {line_num}: {e}"


def find_text_command(nvim: pynvim.Nvim, pattern: str) -> str:
    """
    Execute FIND "pattern" command.
    
    Searches for the specified pattern and moves cursor to first match.
    Uses Neovim's search command (/) for consistency with editor behavior.
    """
    try:
        # Use Neovim's search command
        # The 'n' flag means don't jump to match, 'W' means don't wrap
        search_result = nvim.call('search', pattern, 'nW')
        
        if search_result > 0:
            # Pattern found, move cursor to match
            nvim.command(f'/{pattern}')
            return f"Found '{pattern}' at line {search_result}"
        else:
            return f"Pattern '{pattern}' not found"
            
    except Exception as e:
        return f"Error searching for '{pattern}': {e}"


def replace_text_command(nvim: pynvim.Nvim, old_pattern: str, new_text: str) -> str:
    """
    Execute REPLACE "old" WITH "new" command.
    
    Replaces all occurrences of old pattern with new text.
    Uses Neovim's substitute command (:s) for powerful replacement.
    """
    try:
        # Use substitute command to replace all occurrences in file
        # %s = all lines, g = all occurrences per line
        substitute_cmd = f'%s/{old_pattern}/{new_text}/g'
        
        # Execute the substitute command
        nvim.command(substitute_cmd)
        
        return f"Replaced all '{old_pattern}' with '{new_text}'"
        
    except Exception as e:
        return f"Error replacing '{old_pattern}' with '{new_text}': {e}"


# Command registry - maps command names to their implementations
COMMAND_REGISTRY = {
    'visual_lines': visual_lines_command,
    'insert_text': insert_text_command,
    'delete_lines': delete_lines_command,
    'goto_line': goto_line_command,
    'find_text': find_text_command,
    'replace_text': replace_text_command,
}


def get_command_function(command_name: str):
    """
    Get the implementation function for a command.
    
    Args:
        command_name: Name of the command to look up
        
    Returns:
        Command function or None if not found
    """
    return COMMAND_REGISTRY.get(command_name)


def list_available_commands() -> List[str]:
    """Return a list of all available command names."""
    return list(COMMAND_REGISTRY.keys())
