#!/usr/bin/env python3
"""
Voice Clone — Minimal local voice cloning tool
Usage: python clone.py --input input/her_voice.mp3 --text "What you want her to say"
"""

import argparse
import os
import re
import sys
from pathlib import Path


def check_dependencies():
    missing = []
    try:
        import torch
    except ImportError:
        missing.append("torch")
    try:
        import TTS
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


def detect_language(text: str) -> str:
    """
    Auto-detect if text is Hindi/Hinglish or English.
    Returns 'hi' or 'en'.
    """
    # Check for Devanagari script (actual Hindi)
    if re.search(r'[\u0900-\u097F]', text):
        return 'hi'

    # Common Hinglish romanized words
    hinglish_words = [
        'aap', 'apko', 'apni', 'tum', 'tumhe', 'kese', 'kaise', 'hai', 'hain',
        'nahi', 'nahin', 'mujhe', 'mera', 'meri', 'tera', 'teri', 'bahut',
        'achhe', 'acchi', 'theek', 'yaar', 'bhai', 'dost', 'pyaar', 'love',
        'sun', 'suno', 'bolo', 'kya', 'kyun', 'kab', 'kaun', 'kahan',
        'abhi', 'kal', 'aaj', 'raat', 'din', 'subah', 'shaam', 'lagi',
        'lagta', 'lagti', 'hoga', 'hogi', 'tha', 'thi', 'woh', 'yeh',
        'aur', 'lekin', 'toh', 'bhi', 'hi', 'na', 'ji'
    ]
    text_lower = text.lower()
    words = re.findall(r'\b\w+\b', text_lower)
    hindi_count = sum(1 for w in words if w in hinglish_words)

    # If more than 1 Hinglish word detected, treat as Hindi
    return 'hi' if hindi_count > 1 else 'en'


def clean_text_for_tts(text: str, lang: str) -> str:
    """
    Clean and prepare text for better TTS output.
    Removes patterns that cause unnatural pauses.
    """
    # Remove multiple spaces
    text = re.sub(r' +', ' ', text)

    # Remove excessive punctuation that causes long pauses
    text = re.sub(r'\.{2,}', '.', text)       # ... -> .
    text = re.sub(r',{2,}', ',', text)         # ,, -> ,
    text = re.sub(r'-{2,}', ' ', text)         # -- -> space

    # For Hindi/Hinglish — commas cause long unnatural pauses, replace with space
    if lang == 'hi':
        text = text.replace(',', ' ')
        text = text.replace(';', ' ')

    # Strip leading/trailing whitespace
    text = text.strip()

    return text


def split_into_chunks(text: str, lang: str) -> list:
    """
    Split long text into natural chunks for better synthesis.
    Short chunks = less robotic output.
    """
    if lang == 'hi':
        chunks = re.split(r'[।|.!?]+', text)
    else:
        chunks = re.split(r'[.!?]+', text)

    chunks = [c.strip() for c in chunks if c.strip()]
    return chunks


def clone_voice(input_path: str, text: str, output_path: str, lang: str = 'auto'):
    """
    Clone voice from input audio and synthesize new speech.
    """
    from TTS.api import TTS
    import torch
    import soundfile as sf
    import numpy as np

    # Validate input
    if not os.path.exists(input_path):
        print(f"❌ Input file not found: {input_path}")
        sys.exit(1)

    # Auto detect language
    if lang == 'auto':
        lang = detect_language(text)
        print(f"🔍  Auto-detected language: {'Hindi/Hinglish' if lang == 'hi' else 'English'}")

    # Clean text
    cleaned_text = clean_text_for_tts(text, lang)
    if cleaned_text != text:
        print(f"🧹  Cleaned text: \"{cleaned_text}\"")

    print(f"🎙️  Loading reference voice: {input_path}")
    print(f"📝  Text to synthesize: \"{cleaned_text}\"")
    print(f"💾  Output will be saved to: {output_path}")
    print()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"⚙️  Using device: {device}")
    print("📦  Loading model...")

    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

    # Create output directory if needed
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Split into chunks for more natural output
    chunks = split_into_chunks(cleaned_text, lang)

    if len(chunks) <= 1:
        # Single chunk — synthesize directly
        print("🔄  Synthesizing speech...")
        tts.tts_to_file(
            text=cleaned_text,
            speaker_wav=input_path,
            language=lang,
            file_path=output_path,
        )
    else:
        # Multiple chunks — synthesize each and merge
        print(f"🔄  Synthesizing {len(chunks)} chunks and merging...")
        chunk_files = []

        for i, chunk in enumerate(chunks):
            if not chunk:
                continue
            chunk_path = f"output/chunk_{i}.wav"
            print(f"   chunk {i+1}/{len(chunks)}: \"{chunk}\"")
            tts.tts_to_file(
                text=chunk,
                speaker_wav=input_path,
                language=lang,
                file_path=chunk_path,
            )
            chunk_files.append(chunk_path)

        # Merge chunks with a small natural pause between them
        print("🔗  Merging chunks...")
        merged = []
        sample_rate = None

        for cf in chunk_files:
            data, sr = sf.read(cf)
            sample_rate = sr
            merged.append(data)
            # Add 0.2s natural pause between sentences
            merged.append(np.zeros(int(sr * 0.2)))

        final_audio = np.concatenate(merged)
        sf.write(output_path, final_audio, sample_rate)

        # Cleanup chunk files
        for cf in chunk_files:
            os.remove(cf)

    print(f"\n✅  Done! Output saved to: {output_path}")
    print("🎧  Play it and enjoy the surprise!")


def main():
    parser = argparse.ArgumentParser(
        description="Clone a voice from a reference audio and synthesize new speech.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python clone.py --input input/her_voice.mp3 --text "Happy birthday! I love you so much."
  python clone.py --input input/voice.ogg --text "Apko apni voice kesi lagi?"
  python clone.py --input input/voice.ogg --text "Yaar tum bahut achhe ho" --lang hi
        """
    )

    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Path to reference voice note (mp3, wav, ogg, m4a)"
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
        default="auto",
        help="Language: auto (default), en, hi, fr, es, de, etc."
    )

    args = parser.parse_args()

    print("=" * 50)
    print("       🎤  Voice Clone — Local & Private")
    print("=" * 50)
    print()

    check_dependencies()
    clone_voice(args.input, args.text, args.output, args.lang)


if __name__ == "__main__":
    main()