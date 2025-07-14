#!/usr/bin/env python3
"""
DSL Demo CLI Tool

A command-line interface for testing the Neovim DSL commands.
"""

import argparse
import sys
import pynvim
from pathlib import Path

# Rich imports for beautiful terminal output
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt
from rich.syntax import Syntax
from rich.columns import Columns
from rich.align import Align
from rich import box

# Add src directory to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from route_about.stvim import NvimDSLExecutor

# Initialize Rich console
console = Console()


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
    
    welcome_panel = Panel(
        Align.center(f"{title}\n{subtitle}"),
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
    console.print("\n" + "=" * 60)
    
    interactive_panel = Panel(
        "[bold cyan]Interactive Mode[/bold cyan]\n\n"
        "Enter DSL commands below. Type [yellow]'help'[/yellow] for examples, "
        "[yellow]'show'[/yellow] to view buffer, [yellow]'quit'[/yellow] to exit.",
        title="🎮 Interactive DSL Shell",
        box=box.DOUBLE,
        border_style="magenta"
    )
    console.print(interactive_panel)
    
    show_available_commands()
    
    command_count = 0
    
    while True:
        try:
            cmd = Prompt.ask("\n[bold green]stvim[/bold green]", default="").strip()
            
            if cmd.lower() in ['quit', 'exit', 'q']:
                console.print("[yellow]👋[/yellow] Thanks for using RouteAbout DSL!")
                break
            elif cmd.lower() == 'help':
                show_help_examples()
                continue
            elif cmd.lower() == 'show':
                show_buffer_content(nvim)
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
[bold]Examples:[/bold]
  uv run demo.py --demo                          # Run predefined demo
  uv run demo.py --interactive                   # Interactive mode
  uv run demo.py --command 'INSERT "Hello!"'     # Execute single command
  uv run demo.py --socket /tmp/my_nvim          # Use custom socket path
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
