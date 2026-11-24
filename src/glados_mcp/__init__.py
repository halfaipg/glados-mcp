"""GLaDOS MCP server: GLaDOS and Kokoro text-to-speech for MCP clients."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("glados-mcp")
except PackageNotFoundError:  # running from a source checkout that is not installed
    __version__ = "0.0.0"
