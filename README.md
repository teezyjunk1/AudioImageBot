# Audio+Image → MP4 Telegram Bot (RU/EN)

> Created with the help of ChatGPT.

The bot accepts **audio in MP3 format** and **PNG/JPG images** (as *photo* or *file*) and creates **MP4 1920×1080**: image centered, black background, duration matching the audio length.

## Features
- Accepts only **MP3** for audio
- Accepts **PNG/JPG** as photo and as file, any resolution
- Localization **RU/EN** with user choice saved
- Language change via `/lang` (after selection, the language is saved; on the next /start — it works immediately without selection)

## Quick start
1. Install dependencies and FFmpeg:
   ```bash
   sudo apt-get update && sudo apt-get install -y ffmpeg python3-venv python3-pip
   python3 -m venv venv && source venv/bin/activate
   pip install -r requirements.txt