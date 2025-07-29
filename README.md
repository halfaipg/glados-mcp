# GLaDOS MCP Server

A Model Context Protocol server that provides GLaDOS-style voice commentary for AI development workflows, along with professional Kokoro TTS voices.

## Overview

This project combines:

- **GLaDOS Voice**: Authentic Portal-style audio synthesis with characteristic commentary
- **Professional Alternatives**: 26 Kokoro voices for serious development work
- **MCP Integration**: Seamless integration with existing Model Context Protocol tools

## Demo Videos (Turn on sound)

https://github.com/user-attachments/assets/b82f5ab0-64e6-4b9f-8b33-c35292ee56bd


https://github.com/user-attachments/assets/0fb2be84-c665-4641-9552-ff5bc866e50a

## Installation

### 1. Download Models (Required)
The TTS models are too large for git, so download them first:
```bash
python download_models.py
```

### 2. Install System Dependencies

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install portaudio19-dev python3-pyaudio
```

**Linux (Fedora/RHEL):**
```bash
sudo dnf install portaudio-devel python3-pyaudio
```

**macOS:**
```bash
brew install portaudio
```

### 3. Install the Server
```bash
cd glados-mcp
python -m venv venv
source venv/bin/activate  # Windows users: venv\Scripts\activate
pip install -e .
```

## Configuration

Add this to your MCP client configuration:

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

The interface is straightforward:

**Default GLaDOS Voice**:
```python
speak("Your code is... adequate. I suppose.")
```

**Professional Kokoro Voices**:
```python
speak("Analysis complete.", voice="af_alloy")
speak("Task finished.", voice="bm_daniel")
```

**Available Voices**:
```python
list_voices()  # Returns all 26 Kokoro voices plus GLaDOS
```

## Voice Options

- **GLaDOS** (default): Characteristic Portal-style commentary
- **Kokoro Female US**: af_alloy, af_aoede, af_bella, af_jessica, af_kore, af_nicole, af_nova, af_river, af_sarah, af_sky
- **Kokoro Female British**: bf_alice, bf_emma, bf_isabella, bf_lily  
- **Kokoro Male US**: am_adam, am_echo, am_eric, am_fenrir, am_liam, am_michael, am_onyx, am_puck
- **Kokoro Male British**: bm_daniel, bm_fable, bm_george, bm_lewis

## Project Structure

```
├── download_models.py   # Downloads TTS models (run this first!)
├── mcp.json            # MCP client configuration
├── glados-mcp/         # Main server code
│   ├── tts/            # TTS system
│   ├── models/         # Voice models (downloaded by script)
│   └── README.md       # Detailed instructions
```

## Requirements

- Python 3.10+
- Audio output
- Internet connection for model download
- **Linux**: PortAudio system library (`portaudio19-dev`)

## License

Apache 2.0

---

*"The cake is a lie, but the voice commentary is real."* 