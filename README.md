# pyqtPiperTTS

<p align="center">
  <a href="https://github.com/cfunkz/pyqtPiperTTS/releases">
    <img alt="Downloads" src="https://img.shields.io/github/downloads/cfunkz/pyqtPiperTTS/total?style=for-the-badge" />
  </a>
  <a href="https://github.com/cfunkz/pyqtPiperTTS/stargazers">
    <img alt="Stars" src="https://img.shields.io/github/stars/cfunkz/pyqtPiperTTS?style=for-the-badge" />
  </a>
  <a href="https://github.com/cfunkz/pyqtPiperTTS/network/members">
    <img alt="Forks" src="https://img.shields.io/github/forks/cfunkz/pyqtPiperTTS?style=for-the-badge" />
  </a>
  <a href="https://github.com/cfunkz/pyqtPiperTTS/issues">
    <img alt="Issues" src="https://img.shields.io/github/issues/cfunkz/pyqtPiperTTS?style=for-the-badge" />
  </a>
</p>

<p align="center">
  A Windows application wrapper for PiperTTS with auto-download and installation of models from Hugging Face. Manual model addition, text-to-speech playback, config adjustment, and WAV export.
</p>

> Add custom models to `models/` (in the app folder). folder within root.

## Get voice models manually

- [Piper (official) voice list](https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/VOICES.md)
- [Hugging Face: rhasspy/piper-voices](https://huggingface.co/rhasspy/piper-voices/tree/main)

## App Usage
- Download a [Release](https://github.com/cfunkz/pyqtPiperTTS/releases/)
- Run the `PiperTTS.exe`.
- Select/download/add model.
- Enter text in box.
- Adjust config (volume, speed, noise, noise_w).
- Click "▶" for audio or "💾" to export as WAV.

## Development Setup
- Install Python 3.10+.
- Install dependencies: `pip install pyqt6 piper-tts sounddevice numpy`
- Clone repo and run app.py.

### Get voice-models automatically from hugginface.co
<img width="1243" height="842" alt="image" src="https://github.com/user-attachments/assets/83ca3ef8-6666-458c-9a06-488d70a5aaeb" />

### Manually upload voice models
<img width="1247" height="843" alt="image" src="https://github.com/user-attachments/assets/b3eb13a1-9426-49c4-9ee3-725ffe0368dc" />

### Play or output to file
<img width="1241" height="847" alt="image" src="https://github.com/user-attachments/assets/379032c9-84f7-460b-8271-023c972c82d6" />

