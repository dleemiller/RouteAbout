# RouteAbout

A domain-specific language (DSL) for controlling Neovim through simple, readable commands.

## Overview

RouteAbout provides a custom DSL that translates natural language commands into Neovim operations. Instead of remembering complex vim commands, you can use intuitive syntax like `INSERT "Hello World!" AT LINE 5` or `REPLACE "old" WITH "new"`.

## Requirements

- Python 3.8+
- Neovim with pynvim support
- A running Neovim instance with socket enabled

## Installation

```bash
uv sync --all-groups
```

## Quick Start

1. Start Neovim with a socket:
```bash
nvim --listen /tmp/nvim_socket
```

2. Run the demo:
```bash
uv run demo.py --demo
```

3. Or use interactive mode:
```bash
uv run demo.py --interactive
```

## Available Commands

- `VISUAL LINES <start> TO <end>` - Select line range
- `INSERT "text" [AT LINE <n>]` - Insert text at cursor or specific line
- `DELETE LINES <start> TO <end>` - Delete line range
- `GOTO LINE <n>` - Move cursor to line
- `FIND "pattern"` - Search for text
- `REPLACE "old" WITH "new"` - Replace all occurrences

## Usage Examples

```
INSERT "Hello, World!"
INSERT "New line" AT LINE 5
VISUAL LINES 1 TO 10
GOTO LINE 42
FIND "TODO"
REPLACE "bug" WITH "feature"
DELETE LINES 15 TO 20
```

## CLI Options

```bash
uv run demo.py --help                    # Show all options
uv run demo.py --demo                    # Run predefined demo
uv run demo.py --interactive             # Interactive command mode
uv run demo.py --command 'INSERT "Hi"'   # Execute single command
uv run demo.py --socket /path/to/socket  # Custom socket path
```

## Development

The project is organized into:

- `src/route_about/grammars/stvim.lark` - DSL grammar definition
- `src/route_about/stvim/` - Command parsing and execution
- `demo.py` - CLI interface

To extend the DSL, add new grammar rules to `stvim.lark` and implement corresponding commands in the stvim module.

## License

See LICENSE file for details.
