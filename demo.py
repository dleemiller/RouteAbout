#!/usr/bin/env python3
"""
DSL Demo CLI Tool

A command-line interface for testing the Neovim DSL commands.
"""

import argparse
import sys
import pynvim
from pathlib import Path

# Add src directory to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from route_about.stvim import NvimDSLExecutor


def connect_to_nvim(socket_path: str = "/tmp/nvim_socket") -> pynvim.Nvim:
    """Connect to a running Neovim instance."""
    try:
        nvim = pynvim.attach("socket", path=socket_path)
        return nvim
    except Exception as e:
        print(f"Error connecting to Neovim at {socket_path}: {e}")
        print("Make sure Neovim is running with: nvim --listen /tmp/nvim_socket")
        sys.exit(1)


def setup_demo_buffer(nvim: pynvim.Nvim):
    """Set up the buffer with some initial content for demonstration."""
    initial_content = [
        "Welcome to the DSL demo",
        "Hello World!",
        "This is line 3",
        "Another line here",
        "Sample text for testing",
        "Final line",
    ]
    nvim.current.buffer[:] = initial_content
    return initial_content


def show_buffer_content(nvim: pynvim.Nvim, title: str = "Buffer content"):
    """Display current buffer content with line numbers."""
    print(f"\n{title}:")
    print("-" * 40)
    for i, line in enumerate(nvim.current.buffer, 1):
        print(f"{i:2}: {line}")
    print("-" * 40)


def run_demo_commands(executor: NvimDSLExecutor, nvim: pynvim.Nvim):
    """Run a predefined set of demo commands."""
    demo_commands = [
        'INSERT "Hello, DSL World!"',
        'INSERT "New line at position 3" AT LINE 3',
        "GOTO LINE 2",
        "VISUAL LINES 1 TO 3",
        'FIND "Hello"',
        'REPLACE "Hello" WITH "Goodbye"',
        "DELETE LINES 7 TO 8",
    ]

    print("\nRunning demo commands:")
    print("=" * 50)

    for cmd in demo_commands:
        print(f"\nExecuting: {cmd}")
        result = executor.execute(cmd)
        print(f"Result: {result}")

        # Show buffer after each command
        show_buffer_content(nvim, f"Buffer after: {cmd}")


def interactive_mode(executor: NvimDSLExecutor, nvim: pynvim.Nvim):
    """Run in interactive mode where user can enter commands."""
    print("\n" + "=" * 60)
    print("INTERACTIVE MODE")
    print("=" * 60)
    print("Enter DSL commands (type 'help' for examples, 'quit' to exit)")
    print("Available commands:")
    print("  VISUAL LINES <start> TO <end>")
    print('  INSERT "text" [AT LINE <n>]')
    print("  DELETE LINES <start> TO <end>")
    print("  GOTO LINE <n>")
    print('  FIND "pattern"')
    print('  REPLACE "old" WITH "new"')
    print("-" * 60)

    while True:
        try:
            cmd = input("\nstvim> ").strip()

            if cmd.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break
            elif cmd.lower() == "help":
                print("\nExample commands:")
                print('  INSERT "Hello World!"')
                print('  INSERT "New line" AT LINE 5')
                print("  VISUAL LINES 1 TO 3")
                print("  GOTO LINE 10")
                print('  FIND "search_term"')
                print('  REPLACE "old_text" WITH "new_text"')
                print("  DELETE LINES 5 TO 7")
                continue
            elif cmd.lower() == "show":
                show_buffer_content(nvim)
                continue
            elif cmd == "":
                continue

            # Execute the command
            result = executor.execute(cmd)
            print(f"Result: {result}")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="DSL Demo CLI - Test Neovim DSL commands",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --demo                          # Run predefined demo
  %(prog)s --interactive                   # Interactive mode
  %(prog)s --command 'INSERT "Hello!"'     # Execute single command
  %(prog)s --socket /tmp/my_nvim          # Use custom socket path
        """,
    )

    parser.add_argument(
        "--socket",
        "-s",
        default="/tmp/nvim_socket",
        help="Neovim socket path (default: /tmp/nvim_socket)",
    )

    parser.add_argument(
        "--demo", "-d", action="store_true", help="Run predefined demo commands"
    )

    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Start interactive mode"
    )

    parser.add_argument("--command", "-c", help="Execute a single DSL command")

    parser.add_argument(
        "--setup-buffer",
        action="store_true",
        help="Set up buffer with demo content (default with --demo)",
    )

    args = parser.parse_args()

    # If no mode specified, default to demo
    if not any([args.demo, args.interactive, args.command]):
        args.demo = True
        args.setup_buffer = True

    # Connect to Neovim
    print(f"Connecting to Neovim at {args.socket}...")
    nvim = connect_to_nvim(args.socket)
    print("✓ Connected successfully!")

    # Create executor
    try:
        executor = NvimDSLExecutor(nvim)
        print("✓ DSL executor initialized")
    except Exception as e:
        print(f"Error initializing executor: {e}")
        sys.exit(1)

    # Set up demo buffer if requested or running demo
    if args.setup_buffer or args.demo:
        setup_demo_buffer(nvim)
        show_buffer_content(nvim, "Initial buffer content")

    # Run appropriate mode
    if args.command:
        print(f"\nExecuting command: {args.command}")
        result = executor.execute(args.command)
        print(f"Result: {result}")
        show_buffer_content(nvim, "Buffer after command")

    elif args.demo:
        run_demo_commands(executor, nvim)

    elif args.interactive:
        interactive_mode(executor, nvim)

    print("\nDone!")


if __name__ == "__main__":
    main()
