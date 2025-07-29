#!/usr/bin/env python3
"""
GLaDOS MCP Server - Model Download Script

Downloads the required TTS models for GLaDOS and Kokoro voices.
Uses the exact same URLs and checksums as the original GLaDOS repository.
"""

import os
import sys
import urllib.request
import hashlib
from pathlib import Path

# Model URLs from original GLaDOS GitHub releases
MODELS = {
    "glados.onnx": {
        "url": "https://github.com/dnhkng/GLaDOS/releases/download/0.1/glados.onnx",
        "checksum": "17ea16dd18e1bac343090b8589042b4052f1e5456d42cad8842a4f110de25095",
        "size": "63MB"
    },
    "kokoro-v1.0.fp16.onnx": {
        "url": "https://github.com/dnhkng/GLaDOS/releases/download/0.1/kokoro-v1.0.fp16.onnx",
        "checksum": "c1610a859f3bdea01107e73e50100685af38fff88f5cd8e5c56df109ec880204",
        "size": "163MB"
    },
    "kokoro-voices-v1.0.bin": {
        "url": "https://github.com/dnhkng/GLaDOS/releases/download/0.1/kokoro-voices-v1.0.bin",
        "checksum": "c5adf5cc911e03b76fa5025c1c225b141310d0c4a721d6ed6e96e73309d0fd88",
        "size": "13MB"
    },
    "phomenizer_en.onnx": {
        "url": "https://github.com/dnhkng/GLaDOS/releases/download/0.1/phomenizer_en.onnx",
        "checksum": "b64dbbeca8b350927a0b6ca5c4642e0230173034abd0b5bb72c07680d700c5a0",
        "size": "59MB"
    }
}

def verify_checksum(filepath: Path, expected_checksum: str) -> bool:
    """Verify SHA256 checksum of downloaded file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest() == expected_checksum

def download_file(url: str, filepath: Path, description: str, expected_checksum: str):
    """Download a file with progress indication and checksum verification."""
    print(f"Downloading {description}...")
    
    def progress_hook(block_num, block_size, total_size):
        if total_size > 0:
            percent = min(100, (block_num * block_size * 100) // total_size)
            sys.stdout.write(f"\r  Progress: {percent}% ({block_num * block_size // 1024 // 1024}MB)")
            sys.stdout.flush()
    
    try:
        urllib.request.urlretrieve(url, filepath, progress_hook)
        print(f"\n  Verifying checksum...")
        
        if verify_checksum(filepath, expected_checksum):
            print(f"  ✅ Downloaded and verified {description}")
            return True
        else:
            print(f"  ❌ Checksum verification failed for {description}")
            filepath.unlink()  # Delete corrupted file
            return False
            
    except Exception as e:
        print(f"\n  ❌ Failed to download {description}: {e}")
        return False

def main():
    """Download all required TTS models with checksum verification."""
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
        
        # Skip if already exists and checksum is correct
        if filepath.exists():
            print(f"⏭️  {filename} exists, verifying checksum...")
            if verify_checksum(filepath, info["checksum"]):
                print(f"  ✅ {filename} verified, skipping download")
                success_count += 1
                continue
            else:
                print(f"  ⚠️  {filename} checksum failed, re-downloading...")
                filepath.unlink()
        
        # Download the model
        if download_file(info["url"], filepath, f"{filename} ({info['size']})", info["checksum"]):
            success_count += 1
    
    # Summary
    print(f"\n📊 Download Summary:")
    print(f"   Successfully downloaded: {success_count}/{len(MODELS)} models")
    
    if success_count == len(MODELS):
        print("🎉 All models downloaded and verified! Ready to run GLaDOS MCP Server.")
        print("\nNext steps:")
        print("   cd glados-mcp")
        print("   python -m venv venv")
        print("   source venv/bin/activate")
        print("   pip install -e .")
    else:
        print("⚠️  Some models failed to download. Please try again.")

if __name__ == "__main__":
    main() 