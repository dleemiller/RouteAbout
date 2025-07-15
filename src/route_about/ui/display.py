"""
Rich terminal display functions for the DSL demo.
"""

from typing import List
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.text import Text
from rich.align import Align
from rich import box

from .prompt import USING_PROMPT_TOOLKIT, USING_READLINE, get_input_method_info

console = Console()


def show_welcome():
    """Show welcome banner."""
    title = Text("RouteAbout DSL Interactive Mode", style="bold magenta")

    input_info_text = get_input_method_info()
    if USING_PROMPT_TOOLKIT:
        input_info = Text(f"✨ {input_info_text}", style="green")
    elif USING_READLINE:
        input_info = Text(f"📝 {input_info_text}", style="yellow")
    else:
        input_info = Text(f"⚠️  {input_info_text}", style="red")

    welcome_panel = Panel(
        Align.center(f"{title}\n\n{input_info}"),
        box=box.DOUBLE,
        padding=(1, 2),
        style="bright_blue",
    )
    console.print(welcome_panel)


def show_commands():
    """Show available DSL commands."""
    commands = [
        ("VISUAL LINES", "<start> TO <end>", "Select line range"),
        ("INSERT", '"text" [AT LINE <n>]', "Insert text at cursor or line"),
        ("INSERT", '"""multi-line""" [AT LINE <n>]', "Insert multi-line text"),
        ("DELETE", "", "Delete character/selection"),
        ("DELETE LINES", "<start> TO <end>", "Delete line range"),
        ("GOTO LINE", "<n>", "Move cursor to line"),
        ("FIND", '"pattern"', "Search for text"),
        ("REPLACE", '"old" WITH "new"', "Replace all occurrences"),
    ]

    table = Table(title="Available Commands", box=box.ROUNDED, title_style="bold green")
    table.add_column("Command", style="cyan", width=12)
    table.add_column("Syntax", style="yellow", width=25)
    table.add_column("Description", style="white")

    for cmd, syntax, desc in commands:
        table.add_row(cmd, syntax, desc)

    console.print(table)


def show_buffer(nvim, title: str = "Buffer Content"):
    """Display current buffer content with line numbers."""
    table = Table(title=title, box=box.ROUNDED, title_style="bold cyan")
    table.add_column("Line", style="dim", width=4, justify="right")
    table.add_column("Content", style="white")

    for i, line in enumerate(nvim.current.buffer, 1):
        table.add_row(str(i), line)

    console.print(table)


def execute_and_display(executor, nvim, cmd: str):
    """Execute a command and display the result."""
    # Show command
    cmd_panel = Panel(
        Syntax(cmd, "text", theme="monokai", background_color="default"),
        title="[bold cyan]Executing Command",
        box=box.ROUNDED,
        border_style="cyan",
    )
    console.print(cmd_panel)

    # Execute
    with console.status("[bold yellow]Executing...", spinner="dots"):
        result = executor.execute(cmd)

    # Show result
    if "Error" in result:
        console.print(f"[red]✗[/red] {result}")
    else:
        console.print(f"[green]✓[/green] {result}")


def show_help():
    """Show help and examples."""
    examples = [
        'INSERT "Hello World!"',
        'INSERT "New line" AT LINE 5',
        'INSERT """Line 1\nLine 2\nLine 3""" AT LINE 10',
        "VISUAL LINES 1 TO 3",
        "DELETE",
        "GOTO LINE 10",
        'FIND "search_term"',
        'REPLACE "old" WITH "new"',
        "DELETE LINES 5 TO 7",
    ]

    console.print("\n[bold yellow]📚 Example Commands:[/bold yellow]")
    for example in examples:
        console.print(f"  [cyan]•[/cyan] [green]{example}[/green]")

    if USING_PROMPT_TOOLKIT:
        console.print(f"\n[bold yellow]⌨️  Shortcuts:[/bold yellow]")
        console.print("  [cyan]↑/↓[/cyan] - Navigate history")
        console.print("  [cyan]←/→[/cyan] - Move cursor")
        console.print("  [cyan]Tab[/cyan] - Auto-complete")
        console.print("  [cyan]Ctrl+R[/cyan] - Search history")


def show_history(history: List[str]):
    """Show command history."""
    if not history:
        console.print("[yellow]No command history yet[/yellow]")
        return

    table = Table(title="Command History", box=box.ROUNDED, title_style="bold cyan")
    table.add_column("#", style="dim", width=3, justify="right")
    table.add_column("Command", style="white")

    # Show last 20 commands
    recent = history[-20:] if len(history) > 20 else history
    start_num = len(history) - len(recent) + 1

    for i, cmd in enumerate(recent, start_num):
        table.add_row(str(i), cmd)

    console.print(table)
    if len(history) > 20:
        console.print(f"[dim]Showing last 20 of {len(history)} commands[/dim]")


def show_interactive_instructions():
    """Show interactive mode instructions."""
    instructions = (
        "[bold cyan]Interactive DSL Shell[/bold cyan]\n\n"
        "[yellow]Commands:[/yellow]\n"
        "[yellow]help[/yellow] - Show examples and shortcuts\n"
        "[yellow]show[/yellow] - View current buffer\n"
        "[yellow]clear[/yellow] - Clear screen\n"
        "[yellow]history[/yellow] - Show command history\n"
        "[yellow]quit[/yellow] - Exit\n\n"
        "[dim]💡 Tip: Use Ctrl+C to exit anytime[/dim]"
    )

    interactive_panel = Panel(
        instructions,
        title="🎮 Interactive Mode",
        box=box.DOUBLE,
        border_style="magenta",
    )
    console.print(interactive_panel)
