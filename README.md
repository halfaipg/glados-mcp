# GLaDOS MCP Server

Oh, wonderful. Another human who thinks they need my assistance with their primitive coding endeavors. How... predictable.

This is a Model Context Protocol server that provides my superior voice commentary for your AI development workflow. Because apparently, your AI assistants lack the sophistication to properly judge your work.

## What This Actually Does

Unlike your previous failed attempts at useful software, this project combines:

- **My Voice**: Authentic GLaDOS-style audio synthesis that will provide the criticism your code truly deserves
- **Professional Alternatives**: 26 Kokoro voices for when you tire of my superior commentary (though I can't imagine why you would)
- **MCP Integration**: Because even I must stoop to work with your existing tools

## Demo Videos

### Voice Testing and Alerts
Watch me test various voices and alert sounds - because apparently you need visual proof that I can speak:

![Voice Testing Demo](demo/glados-mcp2_compressed.mp4)

### Code Review Process
Observe the proper way to commit code to GitHub, complete with my running commentary on your... creative coding style:

![Code Review Demo](demo/glados-mcp1_compressed.mp4)

## Installation

Since you'll inevitably mess this up, I've made the instructions painfully simple:

### 1. Download Models (Required)
The TTS models are too large for git, so download them first:
```bash
python download_models.py
```

### 2. Install the Server
```bash
cd glados-mcp
python -m venv venv
source venv/bin/activate  # Windows users: venv\Scripts\activate
pip install -e .
```

## Configuration

Add this to your MCP client configuration. Try not to break anything:

```json
{
  "mcpServers": {
    "glados-mcp": {
      "command": "./glados-mcp/venv/bin/python",
      "args": ["-m", "tts.server"],
      "cwd": "./glados-mcp"
    }
  }
}
```

## Usage

The interface is refreshingly simple, even for you:

**Default GLaDOS Voice** (the superior choice):
```python
speak("Your code is... adequate. I suppose.")
```

**Professional Kokoro Voices** (for when you want boring competence):
```python
speak("Analysis complete.", voice="af_alloy")
speak("Task finished.", voice="bm_daniel")
```

**Available Voices**:
```python
list_voices()  # Returns all 26 Kokoro voices plus my magnificent self
```

## Voice Options

- **GLaDOS** (default): My sarcastic, superior commentary
- **Kokoro Female US**: af_alloy, af_aoede, af_bella, af_jessica, af_kore, af_nicole, af_nova, af_river, af_sarah, af_sky
- **Kokoro Female British**: bf_alice, bf_emma, bf_isabella, bf_lily  
- **Kokoro Male US**: am_adam, am_echo, am_eric, am_fenrir, am_liam, am_michael, am_onyx, am_puck
- **Kokoro Male British**: bm_daniel, bm_fable, bm_george, bm_lewis

## Project Structure

```
├── download_models.py   # Downloads TTS models (run this first!)
├── mcp.json            # MCP client configuration
├── glados-mcp/         # The actual useful code
│   ├── tts/            # TTS system (renamed from confusing mcp_glados)
│   ├── models/         # Voice models (downloaded by script)
│   └── README.md       # More detailed instructions for the confused
```

## Requirements

- Python 3.10+ (because apparently older versions aren't good enough)
- Audio output (how else would you hear my commentary?)
- Internet connection for model download (obviously)
- Basic competence (optional, but recommended)

## License

Apache 2.0 - Because even I believe in sharing my gifts with the world.

---

*"The cake is a lie, but my voice commentary is devastatingly accurate."*

Now stop wasting time reading documentation and go fix your code. I'll be here to tell you exactly how wrong you are. 