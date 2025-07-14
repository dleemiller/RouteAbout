#!/usr/bin/env python3
"""
DSL Demo CLI Tool with Fixed Terminal Input

A command-line interface for testing the Neovim DSL commands with proper
arrow key support, command history, and cursor movement.
"""

import argparse
import sys
import pynvim
from pathlib import Path
from typing import List, Optional

# Rich imports for beautiful terminal output
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.syntax import Syntax
from rich.columns import Columns
from rich.align import Align
from rich.pager import Pager
from rich import box

# Terminal input solution - try prompt_toolkit first, fallback to readline
try:
    from prompt_toolkit import prompt
    from prompt_toolkit.history import InMemoryHistory
    from prompt_toolkit.completion import WordCompleter
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    from prompt_toolkit.shortcuts import CompleteStyle
    USING_PROMPT_TOOLKIT = True
except ImportError:
    USING_PROMPT_TOOLKIT = False
    # Fallback to readline + Rich console.input()
    try:
        import readline
        USING_READLINE = True
    except ImportError:
        USING_READLINE = False

# Add src directory to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from route_about.stvim import NvimDSLExecutor

# Initialize Rich console
console = Console()


class EnhancedPromptHandler:
    """Handles enhanced terminal input with history and completion."""
    
    def __init__(self):
        self.command_history: List[str] = []
        
        if USING_PROMPT_TOOLKIT:
            # Set up prompt_toolkit with history and completion
            self.history = InMemoryHistory()
            
            # DSL commands for auto-completion
            dsl_commands = [
                'INSERT', 'DELETE LINES', 'GOTO LINE', 'FIND', 'REPLACE',
                'VISUAL LINES', 'AT LINE', 'TO', 'WITH', 'help', 'show', 
                'clear', 'history', 'quit', 'exit'
            ]
            self.completer = WordCompleter(dsl_commands, ignore_case=True)
            
        elif USING_READLINE:
            # Configure readline for history
            readline.parse_and_bind('tab: complete')
            readline.parse_and_bind('"\\e[A": history-search-backward')
            readline.parse_and_bind('"\\e[B": history-search-forward')
            
            # Set up completion function
            def complete_dsl(text, state):
                dsl_commands = [
                    'INSERT', 'DELETE LINES', 'GOTO LINE', 'FIND', 'REPLACE',
                    'VISUAL LINES', 'AT LINE', 'TO', 'WITH', 'help', 'show', 
                    'clear', 'history', 'quit', 'exit'
                ]
                matches = [cmd for cmd in dsl_commands if cmd.lower().startswith(text.lower())]
                try:
                    return matches[state]
                except IndexError:
                    return None
            
            readline.set_completer(complete_dsl)
    
    def get_input(self, prompt_text: str = "stvim") -> str:
        """Get input with enhanced terminal features."""
        if USING_PROMPT_TOOLKIT:
            try:
                # Use prompt_toolkit for the best experience
                result = prompt(
                    f"{prompt_text}> ",
                    history=self.history,
                    completer=self.completer,
                    complete_style=CompleteStyle.READLINE_LIKE,
                    auto_suggest=AutoSuggestFromHistory(),
                    enable_history_search=True,
                )
                
                # Add to our internal history (avoid duplicates)
                if result.strip() and result.strip() not in self.command_history:
                    self.command_history.append(result.strip())
                    if len(self.command_history) > 100:  # Keep reasonable size
                        self.command_history.pop(0)
                
                return result.strip()
                
            except (KeyboardInterrupt, EOFError):
                raise KeyboardInterrupt()
                
        elif USING_READLINE:
            try:
                # Use Rich console.input() with readline
                console.print(f"[bold green]{prompt_text}[/bold green]> ", end="")
                result = console.input()
                
                # Add to readline history
                if result.strip():
                    readline.add_history(result.strip())
                    
                # Add to our internal history
                if result.strip() and result.strip() not in self.command_history:
                    self.command_history.append(result.strip())
                    if len(self.command_history) > 100:
                        self.command_history.pop(0)
                
                return result.strip()
                
            except (KeyboardInterrupt, EOFError):
                raise KeyboardInterrupt()
        else:
            # Fallback to basic Rich Prompt (limited functionality)
            console.print(f"[yellow]⚠️  Limited input mode - install prompt_toolkit for full features[/yellow]")
            from rich.prompt import Prompt
            result = Prompt.ask(f"[bold green]{prompt_text}[/bold green]", default="").strip()
            
            if result and result not in self.command_history:
                self.command_history.append(result)
                if len(self.command_history) > 50:
                    self.command_history.pop(0)
            
            return result


def connect_to_nvim(socket_path: str = "/tmp/nvim_socket") -> pynvim.Nvim:
    """Connect to a running Neovim instance."""
    try:
        with console.status("[bold green]Connecting to Neovim...", spinner="dots"):
            nvim = pynvim.attach('socket', path=socket_path)
        
        console.print(f"[green]✓[/green] Connected to Neovim at [cyan]{socket_path}[/cyan]")
        return nvim
    except Exception as e:
        console.print(f"[red]✗[/red] Error connecting to Neovim at [cyan]{socket_path}[/cyan]")
        console.print(f"[red]Error:[/red] {e}")
        console.print("\n[yellow]💡 Tip:[/yellow] Start Neovim with: [cyan]nvim --listen /tmp/nvim_socket[/cyan]")
        sys.exit(1)


def setup_demo_buffer(nvim: pynvim.Nvim):
    """Set up the buffer with some initial content for demonstration."""
    initial_content = [
        "Welcome to the DSL demo",
        "Hello World!",
        "This is line 3",
        "Another line here", 
        "Sample text for testing",
        "Final line"
    ]
    nvim.current.buffer[:] = initial_content
    return initial_content


def show_buffer_content(nvim: pynvim.Nvim, title: str = "Buffer Content"):
    """Display current buffer content with line numbers in a nice table."""
    table = Table(title=title, box=box.ROUNDED, title_style="bold cyan")
    table.add_column("Line", style="dim", width=4, justify="right")
    table.add_column("Content", style="white")
    
    for i, line in enumerate(nvim.current.buffer, 1):
        table.add_row(str(i), line)
    
    console.print(table)


def show_welcome_banner():
    """Display a welcome banner."""
    title = Text("RouteAbout DSL Demo", style="bold magenta")
    subtitle = Text("Natural language commands for Neovim", style="italic cyan")
    
    # Show input method info
    if USING_PROMPT_TOOLKIT:
        input_info = Text("✨ Enhanced input with prompt_toolkit", style="green")
    elif USING_READLINE:
        input_info = Text("📝 Using readline for history support", style="yellow")
    else:
        input_info = Text("⚠️  Basic input mode (install prompt_toolkit for best experience)", style="red")
    
    welcome_panel = Panel(
        Align.center(f"{title}\n{subtitle}\n\n{input_info}"),
        box=box.DOUBLE,
        padding=(1, 2),
        style="bright_blue"
    )
    
    console.print(welcome_panel)


def show_available_commands():
    """Display available DSL commands in a nice format."""
    commands = [
        ("VISUAL LINES", "<start> TO <end>", "Select line range"),
        ("INSERT", '"text" [AT LINE <n>]', "Insert text at cursor or specific line"),
        ("DELETE LINES", "<start> TO <end>", "Delete line range"),
        ("GOTO LINE", "<n>", "Move cursor to line"),
        ("FIND", '"pattern"', "Search for text"),
        ("REPLACE", '"old" WITH "new"', "Replace all occurrences"),
    ]
    
    table = Table(title="Available DSL Commands", box=box.ROUNDED, title_style="bold green")
    table.add_column("Command", style="cyan", width=12)
    table.add_column("Syntax", style="yellow", width=25)
    table.add_column("Description", style="white")
    
    for cmd, syntax, desc in commands:
        table.add_row(cmd, syntax, desc)
    
    console.print(table)


def execute_command_with_display(executor: NvimDSLExecutor, nvim: pynvim.Nvim, cmd: str):
    """Execute a command and display the result nicely."""
    # Show the command being executed
    cmd_panel = Panel(
        Syntax(cmd, "text", theme="monokai", background_color="default"),
        title="[bold cyan]Executing Command",
        box=box.ROUNDED,
        border_style="cyan"
    )
    console.print(cmd_panel)
    
    # Execute and show result
    with console.status("[bold yellow]Executing...", spinner="dots"):
        result = executor.execute(cmd)
    
    # Color-code the result based on success/error
    if "Error" in result:
        result_style = "red"
        result_icon = "✗"
    else:
        result_style = "green"
        result_icon = "✓"
    
    console.print(f"[{result_style}]{result_icon}[/{result_style}] {result}")


def run_demo_commands(executor: NvimDSLExecutor, nvim: pynvim.Nvim):
    """Run a predefined set of demo commands."""
    demo_commands = [
        'INSERT "Hello, DSL World!"',
        'INSERT "New line at position 3" AT LINE 3',
        'GOTO LINE 2', 
        'VISUAL LINES 1 TO 3',
        'FIND "Hello"',
        'REPLACE "Hello" WITH "Goodbye"',
        'DELETE LINES 7 TO 8'
    ]
    
    console.print("\n[bold magenta]🎬 Running Demo Commands[/bold magenta]")
    console.print("=" * 60)
    
    for i, cmd in enumerate(demo_commands, 1):
        console.print(f"\n[bold cyan]Step {i} of {len(demo_commands)}[/bold cyan]")
        execute_command_with_display(executor, nvim, cmd)
        show_buffer_content(nvim, f"Buffer after Step {i}")
        
        if i < len(demo_commands):
            console.print()  # Add spacing between commands


def interactive_mode(executor: NvimDSLExecutor, nvim: pynvim.Nvim):
    """Run in interactive mode where user can enter commands."""
    
    # Initialize the enhanced prompt handler
    prompt_handler = EnhancedPromptHandler()
    
    console.print("\n" + "=" * 60)
    
    # Show different instructions based on input method
    if USING_PROMPT_TOOLKIT:
        features_text = (
            "[bold cyan]Interactive Mode[/bold cyan] [green](Enhanced with prompt_toolkit)[/green]\n\n"
            "[yellow]Navigation:[/yellow]\n"
            "• ↑/↓ arrows - Navigate command history\n"
            "• ←/→ arrows - Move cursor within line\n"
            "• Home/End - Move to start/end of line\n"
            "• Tab - Auto-complete commands\n"
            "• Ctrl+R - Reverse search history\n\n"
            "[yellow]Commands:[/yellow]\n"
            "[yellow]help[/yellow] - Show examples and shortcuts\n"
            "[yellow]show[/yellow] - View current buffer\n"
            "[yellow]clear[/yellow] - Clear screen\n"
            "[yellow]history[/yellow] - Show command history\n"
            "[yellow]quit[/yellow] - Exit\n\n"
            "[dim]💡 Tip: Use Ctrl+C to exit anytime[/dim]"
        )
    elif USING_READLINE:
        features_text = (
            "[bold cyan]Interactive Mode[/bold cyan] [yellow](Using readline)[/yellow]\n\n"
            "[yellow]Navigation:[/yellow]\n"
            "• ↑/↓ arrows - Navigate command history\n"
            "• ←/→ arrows - Move cursor within line\n"
            "• Home/End - Move to start/end of line\n\n"
            "[yellow]Commands:[/yellow]\n"
            "[yellow]help[/yellow] - Show examples and shortcuts\n"
            "[yellow]show[/yellow] - View current buffer\n"
            "[yellow]clear[/yellow] - Clear screen\n"
            "[yellow]history[/yellow] - Show command history\n"
            "[yellow]quit[/yellow] - Exit\n\n"
            "[dim]💡 Tip: Use Ctrl+C to exit anytime[/dim]"
        )
    else:
        features_text = (
            "[bold cyan]Interactive Mode[/bold cyan] [red](Limited input)[/red]\n\n"
            "[yellow]Install prompt_toolkit for enhanced features:[/yellow]\n"
            "[cyan]pip install prompt_toolkit[/cyan]\n\n"
            "[yellow]Commands:[/yellow]\n"
            "[yellow]help[/yellow] - Show examples and shortcuts\n"
            "[yellow]show[/yellow] - View current buffer\n"
            "[yellow]clear[/yellow] - Clear screen\n"
            "[yellow]history[/yellow] - Show command history\n"
            "[yellow]quit[/yellow] - Exit\n\n"
            "[dim]💡 Tip: Use Ctrl+C to exit anytime[/dim]"
        )
    
    interactive_panel = Panel(
        features_text,
        title="🎮 Interactive DSL Shell",
        box=box.DOUBLE,
        border_style="magenta"
    )
    console.print(interactive_panel)
    
    show_available_commands()
    
    command_count = 0
    
    while True:
        try:
            # Get input with enhanced terminal features
            cmd = prompt_handler.get_input("stvim")
            
            if cmd.lower() in ['quit', 'exit', 'q']:
                console.print("[yellow]👋[/yellow] Thanks for using RouteAbout DSL!")
                break
            elif cmd.lower() == 'help':
                show_help_examples()
                show_keyboard_shortcuts()
                continue
            elif cmd.lower() == 'show':
                show_buffer_content(nvim)
                continue
            elif cmd.lower() == 'clear':
                console.clear()
                console.print("[green]✓[/green] Screen cleared")
                continue
            elif cmd.lower() == 'history':
                show_command_history(prompt_handler.command_history)
                continue
            elif cmd == '':
                continue
            
            command_count += 1
            console.print(f"\n[dim]Command #{command_count}[/dim]")
            execute_command_with_display(executor, nvim, cmd)
            
        except KeyboardInterrupt:
            console.print("\n[yellow]👋[/yellow] Thanks for using RouteAbout DSL!")
            break
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")


def show_keyboard_shortcuts():
    """Show helpful keyboard shortcuts."""
    if USING_PROMPT_TOOLKIT:
        shortcuts_text = (
            "[bold yellow]Keyboard Shortcuts & Tips[/bold yellow]\n\n"
            "[cyan]↑/↓[/cyan] - Navigate command history\n"
            "[cyan]←/→[/cyan] - Move cursor left/right\n"
            "[cyan]Home/End[/cyan] - Move to start/end of line\n"
            "[cyan]Ctrl+A/E[/cyan] - Alternative start/end of line\n"
            "[cyan]Ctrl+K[/cyan] - Delete from cursor to end of line\n"
            "[cyan]Ctrl+U[/cyan] - Delete entire line\n"
            "[cyan]Ctrl+W[/cyan] - Delete word before cursor\n"
            "[cyan]Ctrl+R[/cyan] - Reverse search history\n"
            "[cyan]Tab[/cyan] - Auto-complete commands\n"
            "[cyan]Ctrl+C[/cyan] - Exit interactive mode\n\n"
            "[dim]Full readline functionality available![/dim]"
        )
    elif USING_READLINE:
        shortcuts_text = (
            "[bold yellow]Keyboard Shortcuts & Tips[/bold yellow]\n\n"
            "[cyan]↑/↓[/cyan] - Navigate command history\n"
            "[cyan]←/→[/cyan] - Move cursor left/right\n"
            "[cyan]Home/End[/cyan] - Move to start/end of line\n"
            "[cyan]Ctrl+A/E[/cyan] - Alternative start/end of line\n"
            "[cyan]Ctrl+K[/cyan] - Delete from cursor to end of line\n"
            "[cyan]Ctrl+U[/cyan] - Delete entire line\n"
            "[cyan]Ctrl+W[/cyan] - Delete word before cursor\n"
            "[cyan]Ctrl+C[/cyan] - Exit interactive mode\n\n"
            "[dim]Basic readline functionality available[/dim]"
        )
    else:
        shortcuts_text = (
            "[bold yellow]Keyboard Shortcuts & Tips[/bold yellow]\n\n"
            "[cyan]Ctrl+C[/cyan] - Exit interactive mode\n"
            "[red]Limited input mode[/red] - Install prompt_toolkit for:\n"
            "• Arrow key navigation\n"
            "• Command history\n"
            "• Cursor movement\n"
            "• Auto-completion\n\n"
            "[cyan]pip install prompt_toolkit[/cyan]"
        )
    
    shortcuts_panel = Panel(
        shortcuts_text,
        title="⌨️  Shortcuts",
        box=box.ROUNDED,
        border_style="yellow"
    )
    console.print(shortcuts_panel)


def show_command_history(command_history: List[str]):
    """Display command history."""
    if not command_history:
        console.print("[yellow]No command history yet[/yellow]")
        return
    
    table = Table(title="Command History", box=box.ROUNDED, title_style="bold cyan")
    table.add_column("#", style="dim", width=3, justify="right")
    table.add_column("Command", style="white")
    
    # Show last 20 commands
    recent_history = command_history[-20:] if len(command_history) > 20 else command_history
    start_num = len(command_history) - len(recent_history) + 1
    
    for i, cmd in enumerate(recent_history, start_num):
        table.add_row(str(i), cmd)
    
    # Use pager for long history
    if len(command_history) > 20:
        with console.pager():
            console.print(table)
        console.print(f"[dim]Showing last 20 of {len(command_history)} commands[/dim]")
    else:
        console.print(table)


def show_help_examples():
    """Show example commands in interactive mode."""
    examples = [
        'INSERT "Hello World!"',
        'INSERT "New line" AT LINE 5',
        'VISUAL LINES 1 TO 3',
        'GOTO LINE 10',
        'FIND "search_term"',
        'REPLACE "old_text" WITH "new_text"',
        'DELETE LINES 5 TO 7'
    ]
    
    console.print("\n[bold yellow]📚 Example Commands:[/bold yellow]")
    
    for example in examples:
        console.print(f"  [cyan]•[/cyan] [green]{example}[/green]")


def main():
    parser = argparse.ArgumentParser(
        description="RouteAbout DSL Demo - Natural language commands for Neovim",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python demo.py --demo                          # Run predefined demo
  python demo.py --interactive                   # Interactive mode
  python demo.py --command 'INSERT "Hello!"'     # Execute single command
  python demo.py --socket /tmp/my_nvim          # Use custom socket path

For best experience, install prompt_toolkit:
  pip install prompt_toolkit
        """
    )
    
    parser.add_argument(
        '--socket', '-s',
        default='/tmp/nvim_socket',
        help='Neovim socket path (default: /tmp/nvim_socket)'
    )
    
    parser.add_argument(
        '--demo', '-d',
        action='store_true',
        help='Run predefined demo commands'
    )
    
    parser.add_argument(
        '--interactive', '-i',
        action='store_true', 
        help='Start interactive mode'
    )
    
    parser.add_argument(
        '--command', '-c',
        help='Execute a single DSL command'
    )
    
    parser.add_argument(
        '--setup-buffer',
        action='store_true',
        help='Set up buffer with demo content (default with --demo)'
    )
    
    args = parser.parse_args()
    
    # Show welcome banner
    show_welcome_banner()
    
    # If no mode specified, default to demo
    if not any([args.demo, args.interactive, args.command]):
        args.demo = True
        args.setup_buffer = True
    
    # Connect to Neovim
    nvim = connect_to_nvim(args.socket)
    
    # Create executor
    try:
        with console.status("[bold blue]Initializing DSL executor...", spinner="dots"):
            executor = NvimDSLExecutor(nvim)
        console.print("[green]✓[/green] DSL executor initialized")
    except Exception as e:
        console.print(f"[red]✗[/red] Error initializing executor: {e}")
        sys.exit(1)
    
    # Set up demo buffer if requested or running demo
    if args.setup_buffer or args.demo:
        with console.status("[bold blue]Setting up demo buffer...", spinner="dots"):
            setup_demo_buffer(nvim)
        show_buffer_content(nvim, "Initial Buffer Content")
    
    # Run appropriate mode
    if args.command:
        console.print(f"\n[bold magenta]🎯 Single Command Mode[/bold magenta]")
        execute_command_with_display(executor, nvim, args.command)
        show_buffer_content(nvim, "Buffer After Command")
    
    elif args.demo:
        run_demo_commands(executor, nvim)
        
    elif args.interactive:
        interactive_mode(executor, nvim)
    
    console.print("\n[bold green]🎉 Demo completed![/bold green]")


if __name__ == "__main__":
    main()

