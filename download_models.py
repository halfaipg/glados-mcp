#!/usr/bin/env python3
"""
GLaDOS MCP Server - Model Download Script

Downloads the required TTS models for GLaDOS and Kokoro voices.
Based on the original GLaDOS repo approach but simplified for TTS only.
"""

import os
import sys
import urllib.request
import hashlib
from pathlib import Path

# Model URLs and checksums
MODELS = {
    "glados.onnx": {
        "url": "https://github.com/dnhkng/GLaDOS/raw/main/models/TTS/glados.onnx",
        "size": "63MB"
    },
    "kokoro-v1.0.fp16.onnx": {
        "url": "https://huggingface.co/remsky/Kokoro-TTS/resolve/main/kokoro-v1.0.fp16.onnx", 
        "size": "169MB"
    },
    "kokoro-voices-v1.0.bin": {
        "url": "https://huggingface.co/remsky/Kokoro-TTS/resolve/main/kokoro-voices-v1.0.bin",
        "size": "13MB"  
    },
    "phomenizer_en.onnx": {
        "url": "https://github.com/dnhkng/GLaDOS/raw/main/models/TTS/phomenizer_en.onnx",
        "size": "58MB"
    }
}

def download_file(url: str, filepath: Path, description: str):
    """Download a file with progress indication."""
    print(f"Downloading {description}...")
    
    def progress_hook(block_num, block_size, total_size):
        if total_size > 0:
            percent = min(100, (block_num * block_size * 100) // total_size)
            sys.stdout.write(f"\r  Progress: {percent}% ({block_num * block_size // 1024 // 1024}MB)")
            sys.stdout.flush()
    
    try:
        urllib.request.urlretrieve(url, filepath, progress_hook)
        print(f"\n  ✅ Downloaded {description}")
        return True
    except Exception as e:
        print(f"\n  ❌ Failed to download {description}: {e}")
        return False

def main():
    """Download all required TTS models."""
    print("🤖 GLaDOS MCP Server - Model Download")
    print("=====================================")
    
    # Create models directory
    models_dir = Path("glados-mcp/models")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Models directory: {models_dir}")
    
    # Download each model
    success_count = 0
    for filename, info in MODELS.items():
        filepath = models_dir / filename
        
        # Skip if already exists
        if filepath.exists():
            print(f"⏭️  {filename} already exists, skipping...")
            success_count += 1
            continue
            
        # Download the model
        if download_file(info["url"], filepath, f"{filename} ({info['size']})"):
            success_count += 1
    
    # Summary
    print(f"\n📊 Download Summary:")
    print(f"   Successfully downloaded: {success_count}/{len(MODELS)} models")
    
    if success_count == len(MODELS):
        print("🎉 All models downloaded! Ready to run GLaDOS MCP Server.")
        print("\nNext steps:")
        print("   cd glados-mcp")
        print("   python -m venv venv")
        print("   source venv/bin/activate")
        print("   pip install -e .")
    else:
        print("⚠️  Some models failed to download. Please try again.")
        sys.exit(1)

if __name__ == "__main__":
    main() 