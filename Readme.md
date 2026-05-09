# 🎤 Voice Clone — Local & Private

Clone a voice from a reference audio note and synthesize new speech in that voice.
Runs **100% locally** — no API, no cloud, nothing leaves your machine.

---

## How It Works

1. You provide voice note (any format — mp3, ogg, m4a, wav)
2. XTTS-v2 extracts voice's tone, pitch, and speaking style
3. It synthesizes new audio with your text, in voice

---

## Setup (One Time)

### 1. Install ffmpeg (required for non-wav audio)
```bash
# Mac
brew install ffmpeg

# Ubuntu / Debian
sudo apt install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html and add to PATH
```

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```
> ⚠️ First run downloads the XTTS-v2 model (~2GB). Cached after that.

---

## Usage

```bash
# Basic
python clone.py --input input/her_voice.mp3 --text "Happy birthday! I love you so much."

# With custom output path
python clone.py --input input/voice.ogg --text "Surprise!" --output output/surprise.wav

# Hindi or other language
python clone.py --input input/voice.m4a --text "Tum bahut special ho" --lang hi
```

### Arguments

| Flag | Short | Description |
|------|-------|-------------|
| `--input` | `-i` | Path to voice note (any audio format) |
| `--text` | `-t` | What you want to synthesize in voice |
| `--output` | `-o` | Output file path (default: `output/cloned_voice.wav`) |
| `--lang` | `-l` | Language: `en`, `hi`, `fr`, `es`, `de`, etc. (default: `en`) |

---

## Tips for Best Results

- **Longer reference = better clone.** Use at least 6–10 seconds of clean audio
- **Clean audio matters.** Less background noise = more accurate voice match
- **No music in the background** of the reference clip
- If voice note is very short (<5 sec), quality may be lower but still works
- Works with WhatsApp voice notes (.ogg), iPhone voice memos (.m4a), and regular mp3/wav

---

## Project Structure

```
voice-clone/
├── clone.py            ← Main script (only file you need)
├── requirements.txt    ← Dependencies
├── README.md           ← This file
├── input/              ← Drop her voice note here
│   └── her_voice.mp3
└── output/             ← Generated audio appears here
    └── cloned_voice.wav
```

---

## Supported Languages

`en` English · `hi` Hindi · `fr` French · `es` Spanish · `de` German  
`it` Italian · `pt` Portuguese · `pl` Polish · `tr` Turkish · `ru` Russian  
`nl` Dutch · `cs` Czech · `ar` Arabic · `zh-cn` Chinese · `ja` Japanese · `ko` Korean

---

## Privacy

Everything runs locally on your machine. No data is sent anywhere. The model weights download once from Hugging Face and are cached in `~/.local/share/tts/`.