"""
ESC/POS utilities for WN-PrinterHub
Enhanced ESC/POS command generation with additional features
"""
from typing import Dict, Any, Optional
import textwrap


class ESCPOSCommands:
    """ESC/POS command constants."""
    
    # Initialization
    INIT = b"\x1b@"
    
    # Text formatting
    BOLD_ON = b"\x1b\x45\x01"
    BOLD_OFF = b"\x1b\x45\x00"
    UNDERLINE_ON = b"\x1b\x2d\x01"
    UNDERLINE_OFF = b"\x1b\x2d\x00"
    
    # Alignment
    ALIGN_LEFT = b"\x1b\x61\x00"
    ALIGN_CENTER = b"\x1b\x61\x01"
    ALIGN_RIGHT = b"\x1b\x61\x02"
    
    # Size
    SIZE_NORMAL = b"\x1b\x21\x00"
    SIZE_DOUBLE_HEIGHT = b"\x1b\x21\x10"
    SIZE_DOUBLE_WIDTH = b"\x1b\x21\x20"
    SIZE_DOUBLE = b"\x1b\x21\x30"
    
    # Paper
    CUT_FULL = b"\x1d\x56\x00"
    CUT_PARTIAL = b"\x1d\x56\x01"
    FEED_LINE = b"\x0a"
    
    # Character sets
    CHARSET_USA = b"\x1b\x52\x00"
    CHARSET_FRANCE = b"\x1b\x52\x01"
    CHARSET_GERMANY = b"\x1b\x52\x02"


class ESCPOSBuilder:
    """Builder for creating ESC/POS commands with fluent interface."""
    
    def __init__(self):
        self._commands = bytearray()
        self.initialize()
    
    def initialize(self):
        """Initialize the printer."""
        self._commands.extend(ESCPOSCommands.INIT)
        return self
    
    def text(self, content: str, encoding: str = "utf-8"):
        """Add text content."""
        try:
            self._commands.extend(content.encode(encoding, errors="replace"))
        except (UnicodeError, LookupError):
            # Fallback to UTF-8
            self._commands.extend(content.encode("utf-8", errors="replace"))
        return self
    
    def line(self, content: str = "", encoding: str = "utf-8"):
        """Add text content followed by a newline."""
        self.text(content, encoding)
        self._commands.extend(ESCPOSCommands.FEED_LINE)
        return self
    
    def bold(self, enabled: bool = True):
        """Enable/disable bold text."""
        self._commands.extend(ESCPOSCommands.BOLD_ON if enabled else ESCPOSCommands.BOLD_OFF)
        return self
    
    def underline(self, enabled: bool = True):
        """Enable/disable underlined text."""
        self._commands.extend(ESCPOSCommands.UNDERLINE_ON if enabled else ESCPOSCommands.UNDERLINE_OFF)
        return self
    
    def align(self, alignment: str):
        """Set text alignment: 'left', 'center', 'right'."""
        align_commands = {
            'left': ESCPOSCommands.ALIGN_LEFT,
            'center': ESCPOSCommands.ALIGN_CENTER,
            'right': ESCPOSCommands.ALIGN_RIGHT,
        }
        if alignment in align_commands:
            self._commands.extend(align_commands[alignment])
        return self
    
    def size(self, size: str):
        """Set text size: 'normal', 'double_height', 'double_width', 'double'."""
        size_commands = {
            'normal': ESCPOSCommands.SIZE_NORMAL,
            'double_height': ESCPOSCommands.SIZE_DOUBLE_HEIGHT,
            'double_width': ESCPOSCommands.SIZE_DOUBLE_WIDTH,
            'double': ESCPOSCommands.SIZE_DOUBLE,
        }
        if size in size_commands:
            self._commands.extend(size_commands[size])
        return self
    
    def feed(self, lines: int = 1):
        """Feed specified number of lines."""
        for _ in range(lines):
            self._commands.extend(ESCPOSCommands.FEED_LINE)
        return self
    
    def cut(self, partial: bool = False):
        """Cut paper. Use partial=True for partial cut."""
        self._commands.extend(ESCPOSCommands.CUT_PARTIAL if partial else ESCPOSCommands.CUT_FULL)
        return self
    
    def separator(self, char: str = "-", width: int = 32):
        """Add a separator line."""
        self.line(char * width)
        return self
    
    def header(self, title: str, encoding: str = "utf-8"):
        """Add a centered header with formatting."""
        return (self
                .align("center")
                .bold(True)
                .size("double")
                .line(title, encoding)
                .size("normal")
                .bold(False)
                .align("left")
                .feed(1))
    
    def key_value(self, key: str, value: str, key_width: int = 15, encoding: str = "utf-8"):
        """Add a key-value pair with proper spacing."""
        formatted_line = f"{key:<{key_width}} {value}"
        return self.line(formatted_line, encoding)
    
    def table_row(self, columns: list, widths: list = None, encoding: str = "utf-8"):
        """Add a table row with specified column widths."""
        if widths is None:
            # Default equal width distribution
            total_width = 32
            width_per_col = total_width // len(columns)
            widths = [width_per_col] * len(columns)
        
        row_text = ""
        for i, (col, width) in enumerate(zip(columns, widths)):
            col_str = str(col)
            if len(col_str) > width:
                col_str = col_str[:width-3] + "..."
            
            if i == len(columns) - 1:
                # Last column - right align
                row_text += col_str.rjust(width)
            else:
                # Other columns - left align
                row_text += col_str.ljust(width)
        
        return self.line(row_text, encoding)
    
    def build(self) -> bytes:
        """Build and return the final ESC/POS command sequence."""
        return bytes(self._commands)


def create_receipt(items: list, total: float, **kwargs) -> bytes:
    """
    Create a simple receipt using ESC/POS commands.
    
    Args:
        items: List of dictionaries with 'name', 'qty', 'price' keys
        total: Total amount
        **kwargs: Additional options like header, footer, encoding
    """
    builder = ESCPOSBuilder()
    encoding = kwargs.get('encoding', 'utf-8')
    
    # Header
    if 'header' in kwargs:
        builder.header(kwargs['header'], encoding)
    
    # Date/time if provided
    if 'datetime' in kwargs:
        builder.align("center").line(kwargs['datetime'], encoding).feed(1)
    
    # Items table
    builder.separator("=", 32)
    builder.table_row(["Item", "Qty", "Price"], [16, 6, 10], encoding)
    builder.separator("-", 32)
    
    for item in items:
        name = str(item.get('name', ''))
        qty = str(item.get('qty', ''))
        price = f"${item.get('price', 0):.2f}"
        builder.table_row([name, qty, price], [16, 6, 10], encoding)
    
    # Total
    builder.separator("-", 32)
    builder.bold(True).table_row(["TOTAL:", "", f"${total:.2f}"], [16, 6, 10], encoding).bold(False)
    builder.separator("=", 32)
    
    # Footer
    if 'footer' in kwargs:
        builder.feed(1).align("center").line(kwargs['footer'], encoding)
    
    # Final formatting
    builder.feed(kwargs.get('feed_lines', 3))
    
    if kwargs.get('cut', True):
        builder.cut()
    
    return builder.build()


def create_simple_text(text: str, **options) -> bytes:
    """
    Create simple formatted text with ESC/POS commands.
    Supports the same options as the original function for compatibility.
    """
    builder = ESCPOSBuilder()
    
    encoding = options.get('encoding', 'utf-8')
    append_newlines = options.get('append_newlines', 2)
    append_cut = options.get('append_cut', True)
    
    # Process text with basic formatting
    builder.text(text, encoding)
    
    if append_newlines > 0:
        builder.feed(append_newlines)
    
    if append_cut:
        builder.cut()
    
    return builder.build()