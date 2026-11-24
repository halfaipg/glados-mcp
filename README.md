# GLaDOS MCP Server

[![PyPI](https://img.shields.io/pypi/v/glados-mcp)](https://pypi.org/project/glados-mcp/)
[![Python versions](https://img.shields.io/pypi/pyversions/glados-mcp)](https://pypi.org/project/glados-mcp/)
[![License: MIT](https://img.shields.io/pypi/l/glados-mcp)](LICENSE)
[![MCP Registry](https://img.shields.io/badge/MCP%20Registry-io.github.halfaipg%2Fglados--mcp-blue)](https://registry.modelcontextprotocol.io/v0.1/servers?search=io.github.halfaipg/glados-mcp)
[![Publish](https://github.com/halfaipg/glados-mcp/actions/workflows/publish.yml/badge.svg)](https://github.com/halfaipg/glados-mcp/actions/workflows/publish.yml)

<!-- mcp-name: io.github.halfaipg/glados-mcp -->

Your AI coding assistant, now with opinions about you. This Model Context Protocol server lets it talk out loud: GLaDOS-style commentary on whatever it is doing, or one of 26 neutral Kokoro voices when you want it to be serious.

Speech is synthesized locally with ONNX models. Nothing you say or it says leaves your machine.

```bash
uvx glados-mcp
```

## Demo

Turn the sound on.

https://github.com/user-attachments/assets/15be4927-439f-4697-b17f-991c6de69d80

https://github.com/user-attachments/assets/f90c3673-f9d7-41f9-a643-6e5f0464545f

These are scripted scenes; the voice is real output from this server.

## Quick start

You need [uv](https://docs.astral.sh/uv/) and working speakers. Add this to your MCP client configuration (Claude Desktop, Cursor, and so on):

```json
{
  "mcpServers": {
    "glados": {
      "command": "uvx",
      "args": ["glados-mcp"]
    }
  }
}
```

For Claude Code:

```bash
claude mcp add glados -- uvx glados-mcp
```

The first start downloads about 300 MB of voice models into your user cache directory. Until that finishes, the tools reply with download progress. To fetch the models ahead of time:

```bash
uvx glados-mcp download
```

**Linux** also needs the PortAudio library (macOS and Windows wheels include it):

```bash
sudo apt install libportaudio2      # Debian/Ubuntu
sudo dnf install portaudio          # Fedora/RHEL
```

## Tools

| Tool | What it does |
| --- | --- |
| `speak(text, voice?, volume?)` | Speaks the text and returns when playback finishes. Defaults to the GLaDOS voice. |
| `alert(alert_type?)` | Plays a Portal sound: `"chime"` (about 3 seconds, the default) or `"radio"` (about 22 seconds). Returns immediately. |
| `stop()` | Stops whatever is playing. |
| `list_voices()` | Lists GLaDOS and the Kokoro voices. |

To get running commentary, tell your assistant so, for example in your rules or `CLAUDE.md` file: "Use the glados speak tool to comment briefly on what you are doing."

## Voices

- **GLaDOS** (default): `glados`
- **Kokoro female, US**: af_alloy, af_aoede, af_bella, af_jessica, af_kore, af_nicole, af_nova, af_river, af_sarah, af_sky
- **Kokoro female, British**: bf_alice, bf_emma, bf_isabella, bf_lily
- **Kokoro male, US**: am_adam, am_echo, am_eric, am_fenrir, am_liam, am_michael, am_onyx, am_puck
- **Kokoro male, British**: bm_daniel, bm_fable, bm_george, bm_lewis

## Configuration

Optional environment variables:

| Variable | Default | Purpose |
| --- | --- | --- |
| `GLADOS_MCP_DEFAULT_VOICE` | `glados` | Voice used when `speak` is called without one. |
| `GLADOS_MCP_MODELS_DIR` | per-user cache directory | Where the voice models are stored. |

```json
{
  "mcpServers": {
    "glados": {
      "command": "uvx",
      "args": ["glados-mcp"],
      "env": { "GLADOS_MCP_DEFAULT_VOICE": "bm_daniel" }
    }
  }
}
```

## Development

```bash
git clone https://github.com/halfaipg/glados-mcp
cd glados-mcp
uv sync
uv run pytest
uv run glados-mcp          # runs the server on stdio
```

To release, bump the version in `pyproject.toml` and `server.json`, then push a `v*` tag. The `Publish` workflow uploads to PyPI and the MCP Registry.

## Requirements

- Python 3.10 or newer
- Audio output
- Internet access on first run, for the model download

## Credits and license

MIT. The speech synthesis code and voice models come from [dnhkng/GLaDOS](https://github.com/dnhkng/GLaDOS) (MIT); the neutral voices are [Kokoro](https://huggingface.co/hexgrad/Kokoro-82M). GLaDOS and Portal are property of Valve. This is an unofficial fan project, not affiliated with or endorsed by Valve.

---

*"The cake is a lie, but the voice commentary is real."*
