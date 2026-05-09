"""
Voice Clone — Minimal local voice cloning tool
Usage: python clone.py --input input/her_voice.mp3 --text "What you want her to say"
"""

import argparse
import os
import sys
from pathlib import Path


def check_dependencies():
    missing = []
    try:
        import torch
    except ImportError:
        missing.append("torch")
    try:
        from TTS.api import TTS
    except ImportError:
        missing.append("coqui-tts (install via: pip install coqui-tts)")
    try:
        from pydub import AudioSegment
    except ImportError:
        missing.append("pydub")

    if missing:
        print("❌ Missing dependencies:")
        for m in missing:
            print(f"   - {m}")
        print("\nRun: pip install -r requirements.txt")
        sys.exit(1)


def clone_voice(input_path: str, text: str, output_path: str):
    """
    Clone voice from input audio and synthesize new speech.
    
    Args:
        input_path: Path to the reference voice note (her voice)
        text:       What you want her to "say"
        output_path: Where to save the output .wav file
    """
    from TTS.api import TTS
    import torch

    # Validate input
    if not os.path.exists(input_path):
        print(f"❌ Input file not found: {input_path}")
        sys.exit(1)

    print(f"🎙️  Loading reference voice: {input_path}")
    print(f"📝  Text to synthesize: \"{text}\"")
    print(f"💾  Output will be saved to: {output_path}")
    print()

    # Use XTTS-v2 — best open-source multilingual voice cloning model
    # Downloads ~2GB on first run, cached after that
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"⚙️  Using device: {device}")
    print("📦  Loading model (downloads on first run, ~2GB, cached after)...")

    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

    print("🔄  Cloning voice and synthesizing speech...")

    # Create output directory if needed
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    tts.tts_to_file(
        text=text,
        speaker_wav=input_path,   # Her voice reference
        language="en",             # Change to "hi" for Hindi, "fr" for French, etc.
        file_path=output_path,
    )

    print(f"\n✅  Done! Output saved to: {output_path}")
    print("🎧  Play it and enjoy the surprise!")


def main():
    parser = argparse.ArgumentParser(
        description="Clone a voice from a reference audio and synthesize new speech.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python clone.py --input input/her_voice.mp3 --text "Happy birthday! I love you so much."
  python clone.py --input input/voice.ogg --text "Hey, surprise!" --output output/surprise.wav
  python clone.py --input input/voice.m4a --text "Tum bahut achhe ho" --lang hi
        """
    )

    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Path to reference voice note (mp3, wav, ogg, m4a — anything works)"
    )
    parser.add_argument(
        "--text", "-t",
        required=True,
        help="Text you want to synthesize in her voice"
    )
    parser.add_argument(
        "--output", "-o",
        default="output/cloned_voice.wav",
        help="Output file path (default: output/cloned_voice.wav)"
    )
    parser.add_argument(
        "--lang", "-l",
        default="en",
        help="Language code: en, hi, fr, es, de, etc. (default: en)"
    )

    args = parser.parse_args()

    print("=" * 50)
    print("       🎤  Voice Clone — Local & Private")
    print("=" * 50)
    print()

    check_dependencies()
    clone_voice(args.input, args.text, args.output)


if __name__ == "__main__":
    main()