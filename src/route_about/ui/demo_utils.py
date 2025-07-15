"""
Demo-specific utility functions.
"""


def setup_demo_buffer(nvim):
    """Set up demo content in the buffer."""
    content = [
        "Welcome to the DSL demo",
        "Hello World!",
        "This is line 3",
        "Another line here",
        "Sample text for testing",
        "Final line",
    ]
    nvim.current.buffer[:] = content
    return content
