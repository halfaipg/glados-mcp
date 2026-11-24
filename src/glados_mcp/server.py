"""MCP server that speaks through your speakers as GLaDOS or a Kokoro voice."""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Callable
from typing import Any, Optional, TypeVar

import anyio
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from . import __version__
from .manager import GladosManager
from .utils.resources import ensure_models, missing_models, models_dir

logger = logging.getLogger(__name__)

mcp = MCPServer(
    "glados-mcp",
    title="GLaDOS Voice",
    version=__version__,
    instructions=(
        "Text-to-speech through the user's speakers. `speak` plays text aloud in the GLaDOS "
        "voice (dry, sarcastic, passive-aggressive: write the text in that character) or in "
        "a neutral Kokoro voice. Keep spoken text short, a sentence or two. The first run "
        "downloads about 300 MB of voice models, during which tools report progress."
    ),
)

glados = GladosManager()

T = TypeVar("T")


async def _run(fn: Callable[..., T], *args: Any) -> T:
    """Run blocking audio work off the event loop, reporting failures to the model."""
    try:
        return await anyio.to_thread.run_sync(fn, *args)
    except Exception as e:
        # Everything here is local (bad voice name, models still downloading, no audio
        # device), so the message is safe and useful for the client to see.
        raise ToolError(str(e)) from e


@mcp.tool()
async def speak(text: str, voice: Optional[str] = None, volume: Optional[float] = None) -> str:
    """Speak text aloud through the user's speakers, returning once playback has finished.

    The default voice is GLaDOS from Portal. Text for that voice works best written in
    character: dry, sarcastic, faintly disappointed running commentary on what you are
    doing ("Analyzing this code. I use the term loosely."). For plain narration pick a
    Kokoro voice such as "af_alloy" or "bm_daniel"; `list_voices` returns all of them.

    Speaking interrupts any alert sound that is playing. Keep text to a sentence or two.

    Args:
        text: What to say.
        voice: "glados" or a Kokoro voice name. Omit to use the server's default voice.
        volume: 0.0 to 1.0. Omit for a sensible per-voice default.
    """
    return await _run(glados.speak, text, voice, volume)


@mcp.tool()
async def alert(alert_type: str = "chime") -> str:
    """Play a Portal sound effect to get the user's attention. Returns immediately.

    Args:
        alert_type: "chime" for a short elevator chime (about 3 seconds), or "radio" for
            the Portal radio tune (about 22 seconds). A later `speak` or `stop` call cuts
            the sound off.
    """
    return await _run(glados.alert, alert_type)


@mcp.tool()
async def stop() -> str:
    """Stop any speech or alert sound that is currently playing."""
    await _run(glados.stop)
    return "Audio stopped."


@mcp.tool()
async def list_voices() -> dict[str, Any]:
    """List the available voices: "glados" plus the Kokoro voices grouped by accent and gender."""
    return await _run(glados.get_available_voices)


def _download_models() -> int:
    if not missing_models():
        print(f"All voice models are already in {models_dir()}", file=sys.stderr)
        return 0
    print(f"Downloading voice models to {models_dir()}", file=sys.stderr)

    def progress(done: int, total: int) -> None:
        print(f"\r  {done >> 20} / {total >> 20} MB", end="", file=sys.stderr, flush=True)

    ensure_models(progress)
    print("\nDone.", file=sys.stderr)
    return 0


def main() -> None:
    """Entry point: run the stdio MCP server, or `glados-mcp download` to fetch models."""
    parser = argparse.ArgumentParser(prog="glados-mcp", description=__doc__)
    parser.add_argument("--version", action="version", version=f"glados-mcp {__version__}")
    parser.add_argument(
        "command",
        nargs="?",
        choices=["serve", "download"],
        default="serve",
        help="serve (default): run the MCP server on stdio. download: fetch the voice models and exit.",
    )
    args = parser.parse_args()

    # stdout carries the MCP protocol, so all logging goes to stderr.
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s", stream=sys.stderr)

    if args.command == "download":
        sys.exit(_download_models())

    glados.start()
    mcp.run()


if __name__ == "__main__":
    main()
