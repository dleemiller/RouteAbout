#!/usr/bin/env python3
"""
Simplified DSL Demo - Interactive Mode

A focused command-line interface for testing the Neovim DSL commands
in interactive mode only. Supports multi-line INSERT and enhanced terminal features.
"""

import sys
import pynvim
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from route_about.stvim import NvimDSLExecutor
from route_about.ui import (
    SimplePrompt,
    console,
    show_welcome,
    show_commands,
    show_buffer,
    execute_and_display,
    show_help,
    show_history,
    setup_demo_buffer,
    show_interactive_instructions,
)


def connect_to_nvim(socket_path: str = "/tmp/nvim_socket") -> pynvim.Nvim:
    """Connect to a running Neovim instance."""
    try:
        with console.status("[bold green]Connecting to Neovim...", spinner="dots"):
            nvim = pynvim.attach("socket", path=socket_path)
        console.print(
            f"[green]✓[/green] Connected to Neovim at [cyan]{socket_path}[/cyan]"
        )
        return nvim
    except Exception as e:
        console.print(
            f"[red]✗[/red] Error connecting to Neovim at [cyan]{socket_path}[/cyan]"
        )
        console.print(f"[red]Error:[/red] {e}")
        console.print(
            "\n[yellow]💡 Tip:[/yellow] Start Neovim with: [cyan]nvim --listen /tmp/nvim_socket[/cyan]"
        )
        sys.exit(1)


def interactive_mode(executor: NvimDSLExecutor, nvim: pynvim.Nvim):
    """Run interactive DSL shell."""
    prompt = SimplePrompt()

    console.print("\n" + "=" * 60)
    show_interactive_instructions()

    show_commands()
    command_count = 0

    while True:
        try:
            cmd = prompt.get_input("stvim")

            if cmd.lower() in ["quit", "exit", "q"]:
                console.print("[yellow]👋[/yellow] Thanks for using RouteAbout DSL!")
                break
            elif cmd.lower() == "help":
                show_help()
                continue
            elif cmd.lower() == "show":
                show_buffer(nvim)
                continue
            elif cmd.lower() == "clear":
                console.clear()
                console.print("[green]✓[/green] Screen cleared")
                continue
            elif cmd.lower() == "history":
                show_history(prompt.history)
                continue
            elif cmd == "":
                continue

            command_count += 1
            console.print(f"\n[dim]Command #{command_count}[/dim]")
            execute_and_display(executor, nvim, cmd)

        except KeyboardInterrupt:
            console.print("\n[yellow]👋[/yellow] Thanks for using RouteAbout DSL!")
            break
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")


def main():
    """Main entry point."""
    # Parse simple arguments
    socket_path = "/tmp/nvim_socket"
    if len(sys.argv) > 1:
        if sys.argv[1] in ["-h", "--help"]:
            console.print(
                "[bold green]RouteAbout DSL Demo - Interactive Mode[/bold green]"
            )
            console.print("\nUsage:")
            console.print("  python demo.py [socket_path]")
            console.print("\nExamples:")
            console.print("  python demo.py                    # Use default socket")
            console.print("  python demo.py /tmp/my_nvim      # Use custom socket")
            console.print("\nStart Neovim with:")
            console.print("  nvim --listen /tmp/nvim_socket")
            return
        else:
            socket_path = sys.argv[1]

    # Show welcome
    show_welcome()

    # Connect to Neovim
    nvim = connect_to_nvim(socket_path)

    # Create executor
    try:
        with console.status("[bold blue]Initializing DSL executor...", spinner="dots"):
            executor = NvimDSLExecutor(nvim)
        console.print("[green]✓[/green] DSL executor initialized")
    except Exception as e:
        console.print(f"[red]✗[/red] Error initializing executor: {e}")
        sys.exit(1)

    # Set up demo buffer
    with console.status("[bold blue]Setting up demo buffer...", spinner="dots"):
        setup_demo_buffer(nvim)
    show_buffer(nvim, "Initial Buffer Content")

    # Run interactive mode
    interactive_mode(executor, nvim)

    console.print("\n[bold green]🎉 Demo completed![/bold green]")


if __name__ == "__main__":
    main()
