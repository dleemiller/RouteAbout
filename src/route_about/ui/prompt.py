"""
Terminal input handling with history and completion.
"""

from typing import List
from rich.console import Console

# Terminal input handling - check for available libraries
USING_PROMPT_TOOLKIT = False
USING_READLINE = False

try:
    from prompt_toolkit import prompt
    from prompt_toolkit.history import InMemoryHistory
    from prompt_toolkit.completion import WordCompleter
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    from prompt_toolkit.shortcuts import CompleteStyle

    USING_PROMPT_TOOLKIT = True
except ImportError:
    pass

if not USING_PROMPT_TOOLKIT:
    try:
        import readline

        USING_READLINE = True
    except ImportError:
        pass

console = Console()


class SimplePrompt:
    """Simple prompt handler with history and completion."""

    def __init__(self):
        self.history: List[str] = []

        # DSL commands for completion
        dsl_commands = [
            "INSERT",
            "DELETE",
            "DELETE LINES",
            "GOTO LINE",
            "FIND",
            "REPLACE",
            "VISUAL LINES",
            "AT LINE",
            "TO",
            "WITH",
            "help",
            "show",
            "clear",
            "history",
            "quit",
            "exit",
        ]

        if USING_PROMPT_TOOLKIT:
            self.pt_history = InMemoryHistory()
            self.completer = WordCompleter(dsl_commands, ignore_case=True)
        elif USING_READLINE:
            readline.parse_and_bind("tab: complete")
            readline.parse_and_bind('"\\e[A": history-search-backward')
            readline.parse_and_bind('"\\e[B": history-search-forward')

            def complete_dsl(text, state):
                matches = [
                    cmd for cmd in dsl_commands if cmd.lower().startswith(text.lower())
                ]
                try:
                    return matches[state]
                except IndexError:
                    return None

            readline.set_completer(complete_dsl)

    def get_input(self, prompt_text: str = "stvim") -> str:
        """Get user input with enhanced features and multi-line support."""

        def _get_single_line(prompt_str):
            """Get a single line of input."""
            if USING_PROMPT_TOOLKIT:
                return prompt(prompt_str)  # prompt_toolkit handles its own styling
            elif USING_READLINE:
                console.print(f"[bold green]{prompt_text}[/bold green]> ", end="")
                return console.input()
            else:
                console.print(f"[bold green]{prompt_text}[/bold green]> ", end="")
                return input()

        try:
            # Get the first line - use plain text for prompt_toolkit
            if USING_PROMPT_TOOLKIT:
                result = prompt(
                    f"{prompt_text}> ",
                    history=self.pt_history,
                    completer=self.completer,
                    complete_style=CompleteStyle.READLINE_LIKE,
                    auto_suggest=AutoSuggestFromHistory(),
                    enable_history_search=True,
                )
            else:
                result = _get_single_line(f"{prompt_text}> ")

            # Check if this starts a multi-line string
            if '"""' in result:
                # Count triple quotes to see if string is complete
                triple_quote_count = result.count('"""')

                # If odd number of triple quotes, the string is incomplete
                if triple_quote_count % 2 == 1:
                    lines = [result]

                    # Continue reading lines until we get the closing """
                    while True:
                        try:
                            if USING_PROMPT_TOOLKIT:
                                continuation = prompt("... ")
                            else:
                                console.print("... ", end="")
                                continuation = (
                                    console.input() if USING_READLINE else input()
                                )

                            lines.append(continuation)

                            # Check if this line completes the multi-line string
                            if '"""' in continuation:
                                # Join all lines and count total triple quotes
                                full_text = "\n".join(lines)
                                total_triple_quotes = full_text.count('"""')

                                # If even number, the string is complete
                                if total_triple_quotes % 2 == 0:
                                    result = full_text
                                    break
                        except (KeyboardInterrupt, EOFError):
                            # If user interrupts, return what we have so far
                            result = "\n".join(lines)
                            break

            # Add to history if not empty and not duplicate
            if result.strip() and result.strip() not in self.history:
                self.history.append(result.strip())
                if len(self.history) > 100:
                    self.history.pop(0)

                # Also add to readline history if using it
                if USING_READLINE:
                    readline.add_history(result.strip())

            return result.strip()

        except (KeyboardInterrupt, EOFError):
            raise KeyboardInterrupt()


def get_input_method_info() -> str:
    """Get information about the current input method."""
    if USING_PROMPT_TOOLKIT:
        return "Enhanced input with prompt_toolkit"
    elif USING_READLINE:
        return "Using readline for history"
    else:
        return "Basic input (install prompt_toolkit for best experience)"


# Export the capability flags for other modules
__all__ = [
    "SimplePrompt",
    "console",
    "get_input_method_info",
    "USING_PROMPT_TOOLKIT",
    "USING_READLINE",
]
