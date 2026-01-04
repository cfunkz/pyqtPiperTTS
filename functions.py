"""Core Piper TTS functionality."""
from __future__ import annotations

import io
import os
import shutil
import sys
import wave
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import sounddevice as sd
from piper import PiperVoice
from piper.config import SynthesisConfig
import piper.download_voices as piper_dl

if TYPE_CHECKING:
    from PyQt6.QtCore import QObject

# Audio configuration
sd.default.dtype = "int16" #type: ignore
sd.default.blocksize = 0
sd.default.latency = "low" #type: ignore

# Models directory
MODELS_DIR = Path(os.getenv("PIPER_MODELS_DIR", "models"))
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# CUDA support detection
_CUDA_AVAILABLE: bool | None = None


def is_cuda_available() -> bool:
    """Check if CUDA is available via ONNX Runtime."""
    global _CUDA_AVAILABLE
    
    if _CUDA_AVAILABLE is not None:
        return _CUDA_AVAILABLE
    
    try:
        import onnxruntime as ort
        providers = ort.get_available_providers()
        _CUDA_AVAILABLE = 'CUDAExecutionProvider' in providers
        return _CUDA_AVAILABLE
    except ImportError:
        _CUDA_AVAILABLE = False
        return False


def get_cuda_info() -> dict[str, str | bool]:
    """Get CUDA information for display."""
    cuda_available = is_cuda_available()
    
    info = {
        "available": cuda_available,
        "status": "Available" if cuda_available else "Not Available",
    }
    
    if cuda_available:
        try:
            import onnxruntime as ort
            # Get CUDA device info if available
            info["device"] = "CUDA GPU"
            info["status"] = "Available (CUDA GPU)"
        except Exception:
            pass
    
    return info


def list_models() -> list[str]:
    """List available voice models."""
    models = sorted(p.name for p in MODELS_DIR.glob("*.onnx"))
    return models or ["No models"]


def get_config_path(model_path: Path) -> Path:
    """Get config path for a model file."""
    return model_path.with_suffix(model_path.suffix + ".json")


def load_voice_model(model_name: str, use_cuda: bool = False) -> tuple[PiperVoice | None, str]:
    """Load a Piper voice model. Returns (voice, status_message)."""
    if model_name == "No models":
        return None, "No models found"

    model_path = MODELS_DIR / model_name
    cfg_path = get_config_path(model_path)

    if not model_path.exists():
        return None, f"Model not found: {model_name}"

    if not cfg_path.exists():
        return None, f"Missing config: {cfg_path.name}"

    try:
        # Load with CUDA if requested and available
        voice = PiperVoice.load(
            str(model_path), 
            config_path=str(cfg_path),
            use_cuda=use_cuda and is_cuda_available()
        )
        
        sr = getattr(getattr(voice, "config", None), "sample_rate", None)
        device = "CUDA" if (use_cuda and is_cuda_available()) else "CPU"
        status = f"Loaded: {model_name} ({device})" + (f" @ {sr} Hz" if sr else "")
        return voice, status
    except Exception as e:
        return None, f"Load error: {e}"


def copy_model_files(file_paths: list[str]) -> int:
    """Copy model files to models directory. Returns count of copied files."""
    copied = 0
    for src in file_paths:
        try:
            shutil.copy2(src, MODELS_DIR / Path(src).name)
            copied += 1
        except Exception:
            pass
    return copied


def download_voice_model(voice_id: str) -> tuple[bool, str]:
    """Download a voice model. Returns (success, message)."""
    argv0, out0, err0 = sys.argv, sys.stdout, sys.stderr
    buf = io.StringIO()
    
    try:
        sys.argv = ["piper.download_voices", voice_id, "--data-dir", str(MODELS_DIR)]
        sys.stdout = sys.stderr = buf
        
        try:
            piper_dl.main()
            ok = True
        except SystemExit as se:
            ok = (se.code or 0) == 0

        text = buf.getvalue().strip()
        if ok:
            return True, f"Downloaded: {voice_id}"
        return False, text or f"Download failed: {voice_id}"
        
    except Exception as e:
        return False, f"Download error: {e}"
    finally:
        sys.argv, sys.stdout, sys.stderr = argv0, out0, err0


def synthesize_to_wav(
    voice: PiperVoice,
    text: str,
    output_path: str,
    volume: float = 1.0,
    speed: float = 1.0,
    noise: float = 0.667,
    noise_w: float = 0.8,
    normalize: bool = False,
) -> tuple[bool, str]:
    """Synthesize text to WAV file. Returns (success, message)."""
    try:
        cfg = SynthesisConfig(
            volume=volume,
            length_scale=speed,
            noise_scale=noise,
            noise_w_scale=noise_w,
            normalize_audio=normalize,
        )
        
        with wave.open(output_path, "wb") as wf:
            voice.synthesize_wav(text, wf, cfg)
        
        return True, f"Saved: {Path(output_path).name}"
    except Exception as e:
        return False, f"Export error: {e}"


def synthesize_to_audio_array(
    voice: PiperVoice,
    text: str,
    volume: float = 1.0,
    speed: float = 1.0,
    noise: float = 0.667,
    noise_w: float = 0.8,
    normalize: bool = False,
) -> tuple[np.ndarray | None, int, str]:
    """Synthesize text to audio array. Returns (audio_data, sample_rate, status_message)."""
    try:
        cfg = SynthesisConfig(
            volume=volume,
            length_scale=speed,
            noise_scale=noise,
            noise_w_scale=noise_w,
            normalize_audio=normalize,
        )
        
        # Synthesize to memory buffer
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            voice.synthesize_wav(text, wf, cfg)

        # Read from memory buffer
        buf.seek(0)
        with wave.open(buf, "rb") as rf:
            sample_rate = rf.getframerate()
            raw = rf.readframes(rf.getnframes())
        
        audio = np.frombuffer(raw, dtype=np.int16)
        return audio, sample_rate, "Success"
        
    except Exception as e:
        return None, 0, f"Synthesis error: {e}"


class AudioPlayer:
    """Simple audio player using sounddevice."""
    
    def __init__(self) -> None:
        self.playing = False
        self.stopped = False
    
    def play(self, audio_data: np.ndarray, sample_rate: int) -> None:
        """Play audio data."""
        self.playing = True
        self.stopped = False
        sd.play(audio_data, samplerate=sample_rate, blocking=False)
    
    def stop(self) -> None:
        """Stop playback."""
        if self.playing:
            self.stopped = True
            sd.stop()
            self.playing = False
    
    def wait(self) -> bool:
        """Wait for playback to finish. Returns True if stopped by user."""
        sd.wait()
        self.playing = False
        return self.stopped
    
    def is_playing(self) -> bool:
        """Check if audio is currently playing."""
        return self.playing
