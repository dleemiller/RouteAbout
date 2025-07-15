# RouteAbout

A domain-specific language (DSL) for controlling Neovim through simple, readable commands.

## Overview

RouteAbout provides a custom DSL that translates natural language commands into Neovim operations. Instead of remembering complex vim commands, you can use intuitive syntax like `INSERT "Hello World!" AT LINE 5` or `REPLACE "old" WITH "new"`.

## Features

- **Simple syntax** - Natural language commands for Neovim operations
- **Multi-line support** - Insert multi-line text with triple-quoted strings
- **Interactive shell** - Enhanced terminal interface with history and completion
- **Real-time execution** - Commands execute immediately in your Neovim buffer

## Requirements

- Python 3.8+
- Neovim with pynvim support
- A running Neovim instance with socket enabled
- Optional: `prompt_toolkit` for enhanced terminal features

## Installation

```bash
uv sync --all-groups
```

For the best interactive experience, install prompt_toolkit:
```bash
pip install prompt_toolkit
```

## Quick Start

1. Start Neovim with a socket:
```bash
nvim --listen /tmp/nvim_socket
```

2. Run the interactive demo:
```bash
uv run demo.py
```

3. Or use a custom socket path:
```bash
uv run demo.py /path/to/your/socket
```

## Available Commands

| Command | Syntax | Description |
|---------|--------|-------------|
| **VISUAL LINES** | `<start> TO <end>` | Select line range |
| **INSERT** | `"text" [AT LINE <n>]` | Insert text at cursor or specific line |
| **INSERT** | `"""multi-line""" [AT LINE <n>]` | Insert multi-line text |
| **DELETE** | | Delete character under cursor or selection |
| **DELETE LINES** | `<start> TO <end>` | Delete line range |
| **GOTO LINE** | `<n>` | Move cursor to line |
| **FIND** | `"pattern"` | Search for text |
| **REPLACE** | `"old" WITH "new"` | Replace all occurrences |

## Usage Examples

### Single-line operations:
```
INSERT "Hello, World!"
INSERT "New line" AT LINE 5
VISUAL LINES 1 TO 10
GOTO LINE 42
FIND "TODO"
REPLACE "bug" WITH "feature"
DELETE LINES 15 TO 20
```

### Multi-line operations:
```
INSERT """
function greet(name) {
    console.log("Hello, " + name + "!");
    return true;
}
""" AT LINE 10
```

## Interactive Shell Commands

- `help` - Show examples and keyboard shortcuts
- `show` - Display current buffer content
- `clear` - Clear screen
- `history` - Show command history
- `quit` - Exit the shell

## Keyboard Shortcuts

When using prompt_toolkit:
- **↑/↓** - Navigate command history
- **←/→** - Move cursor within line
- **Tab** - Auto-complete commands
- **Ctrl+R** - Reverse search history
- **Ctrl+C** - Exit

## Development

The project is organized into:

```
src/route_about/
├── grammars/stvim.lark     # DSL grammar definition
├── stvim/                  # Core DSL engine
│   ├── commands.py         # Command implementations
│   ├── transformer.py      # Parse tree transformation
│   └── executor.py         # Command execution
└── ui/                     # Terminal interface components
    ├── prompt.py           # Input handling
    ├── display.py          # Rich display functions
    └── demo_utils.py       # Demo utilities

demo.py                     # Interactive shell
```

### Adding New Commands

1. **Define grammar** in `src/route_about/grammars/stvim.lark`
2. **Implement command** in `src/route_about/stvim/commands.py`
3. **Add transformation** in `src/route_about/stvim/transformer.py`
4. **Update completion** in `src/route_about/ui/prompt.py` (optional)

### Example: Adding a new command

```lark
# In stvim.lark
copy_line: "COPY"i "LINE"i NUMBER "TO"i "LINE"i NUMBER
```

```python
# In commands.py
def copy_line_command(nvim: pynvim.Nvim, from_line: int, to_line: int) -> str:
    # Implementation here
    pass
```

```python
# In transformer.py
def copy_line(self, items: List[Any]) -> str:
    from_line = int(items[0])
    to_line = int(items[1])
    return copy_line_command(self.nvim, from_line, to_line)
```

## License

See LICENSE file for details.
