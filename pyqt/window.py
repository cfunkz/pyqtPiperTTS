### window.py ###
"""Main application window."""
from __future__ import annotations

import threading
from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt, QObject, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from .widgets import Card, FloatSlider, SliderConfig
from functions import (
    list_models,
    load_voice_model,
    copy_model_files,
    download_voice_model,
    synthesize_to_wav,
    synthesize_to_audio_array,
    AudioPlayer,
    is_cuda_available,
    get_cuda_info,
)

if TYPE_CHECKING:
    from PyQt6.QtGui import QCloseEvent
    from piper import PiperVoice


class WorkerSignals(QObject):
    """Signals for background worker threads."""
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    status = pyqtSignal(str)


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Piper TTS Speaker")
        self.setMinimumSize(900, 600)
        self.resize(1000, 650)

        self.voice: PiperVoice | None = None
        self.audio_player = AudioPlayer()
        self.workers: list[QObject] = []
        self.use_cuda = False  # CUDA preference

        self._build_ui()
        self._check_cuda()
        self._load_initial_model()

    def _build_ui(self) -> None:
        """Build complete UI."""
        root = QWidget()
        root.setObjectName("Root")
        self.setCentralWidget(root)

        layout = QVBoxLayout(root)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        layout.addLayout(self._build_header())
        layout.addWidget(self._build_text_area(), 1)
        layout.addWidget(self._build_controls())
        layout.addWidget(self._build_status())

    def _build_header(self) -> QHBoxLayout:
        """Build header section with model selection."""
        header = QHBoxLayout()
        header.setSpacing(8)

        title = QLabel("Voice Model")
        title.setObjectName("AppTitle")
        header.addWidget(title)

        self.model_combo = QComboBox()
        self.model_combo.setMinimumWidth(300)
        self.model_combo.addItems(list_models())
        self.model_combo.currentTextChanged.connect(self._on_model_changed)
        header.addWidget(self.model_combo)

        add_btn = QToolButton()
        add_btn.setText("＋")
        add_btn.setToolTip("Add model files")
        add_btn.clicked.connect(self._add_models)
        header.addWidget(add_btn)

        dl_btn = QToolButton()
        dl_btn.setText("☁")
        dl_btn.setToolTip("Download voice")
        dl_btn.clicked.connect(self._download_voice)
        header.addWidget(dl_btn)

        refresh_btn = QToolButton()
        refresh_btn.setText("⟳")
        refresh_btn.setToolTip("Refresh models")
        refresh_btn.clicked.connect(self._refresh_models)
        header.addWidget(refresh_btn)

        # CUDA toggle
        self.cuda_checkbox = QCheckBox("Use CUDA")
        self.cuda_checkbox.setToolTip("Use GPU acceleration (requires CUDA)")
        self.cuda_checkbox.stateChanged.connect(self._on_cuda_toggled)
        header.addWidget(self.cuda_checkbox)

        header.addStretch()

        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("DimText")
        header.addWidget(self.status_label)

        return header

    def _build_text_area(self) -> Card:
        """Build text input area."""
        card = Card("Text to Speak")

        self.text_edit = QTextEdit()
        self.text_edit.setAcceptRichText(False)
        self.text_edit.setPlaceholderText("Type or paste text here...")
        self.text_edit.setPlainText("Type or paste text here.")
        card.add_widget(self.text_edit)

        return card

    def _build_controls(self) -> Card:
        """Build control panel with sliders and buttons."""
        card = Card("Speech Settings")

        # Sliders
        self.volume = FloatSlider(SliderConfig("Volume", 0.0, 1.0, 1.0))
        self.speed = FloatSlider(SliderConfig("Speed", 0.5, 2.0, 1.0))
        self.noise = FloatSlider(SliderConfig("Noise", 0.0, 1.5, 0.667))
        self.noise_w = FloatSlider(SliderConfig("Noise W", 0.0, 1.5, 0.8))

        for slider in (self.volume, self.speed, self.noise, self.noise_w):
            card.add_widget(slider)

        # Bottom row with checkbox and buttons
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(10)

        self.normalize = QCheckBox("Normalize audio")
        bottom_row.addWidget(self.normalize)

        bottom_row.addStretch()

        self.export_btn = QPushButton("💾 Export WAV")
        self.export_btn.setFixedHeight(40)
        self.export_btn.setMinimumWidth(140)
        self.export_btn.clicked.connect(self._export_wav)
        bottom_row.addWidget(self.export_btn)

        self.play_btn = QPushButton("▶ Play")
        self.play_btn.setFixedHeight(40)
        self.play_btn.setMinimumWidth(140)
        self.play_btn.clicked.connect(self._play_stop)
        bottom_row.addWidget(self.play_btn)

        card.add_layout(bottom_row)

        return card

    def _build_status(self) -> Card:
        """Build status log panel."""
        card = Card("Status Log")

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        copy_btn = QPushButton("Copy")
        copy_btn.setFixedHeight(30)
        copy_btn.clicked.connect(self._copy_log)
        btn_row.addWidget(copy_btn)

        clear_btn = QPushButton("Clear")
        clear_btn.setFixedHeight(30)
        clear_btn.clicked.connect(self._clear_log)
        btn_row.addWidget(clear_btn)

        btn_row.addStretch()
        card.add_layout(btn_row)

        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setMinimumHeight(80)
        self.log.setMaximumHeight(100)
        self.log.setObjectName("LogView")
        card.add_widget(self.log)

        return card

    def _set_status(self, text: str) -> None:
        """Update status label and log."""
        self.status_label.setText(text)
        self.log.appendPlainText(text)

    def _copy_log(self) -> None:
        """Copy log to clipboard."""
        from PyQt6.QtWidgets import QApplication
        cb = QApplication.clipboard()
        if cb:
            cb.setText(self.log.toPlainText())

    def _clear_log(self) -> None:
        """Clear status log."""
        self.log.clear()

    def _check_cuda(self) -> None:
        """Check CUDA availability and update UI."""
        cuda_info = get_cuda_info()
        
        if cuda_info["available"]:
            self.cuda_checkbox.setEnabled(True)
            device_info = cuda_info.get("device", "Unknown GPU")
            self.cuda_checkbox.setToolTip(f"Use GPU acceleration ({device_info})")
            self._set_status(f"CUDA: {cuda_info['status']}")
        else:
            self.cuda_checkbox.setEnabled(False)
            self.cuda_checkbox.setChecked(False)
            self.cuda_checkbox.setToolTip("CUDA not available (requires PyTorch with CUDA)")

    def _on_cuda_toggled(self) -> None:
        """Handle CUDA checkbox toggle."""
        self.use_cuda = self.cuda_checkbox.isChecked()
        
        # Reload current model with new CUDA setting
        if self.voice:
            current_model = self.model_combo.currentText()
            self._set_status(f"Reloading with {'CUDA' if self.use_cuda else 'CPU'}...")
            self._on_model_changed(current_model)

    def _load_initial_model(self) -> None:
        """Load the first available model."""
        if self.model_combo.count() > 0:
            self._on_model_changed(self.model_combo.currentText())

    def _on_model_changed(self, model_name: str) -> None:
        """Handle model selection change."""
        self._set_status(f"Loading: {model_name}...")

        use_cuda = self.use_cuda

        def worker():
            voice, status = load_voice_model(model_name, use_cuda)
            return voice, status

        signals = WorkerSignals()
        signals.finished.connect(self._on_model_loaded)
        
        def run_worker():
            try:
                result = worker()
                signals.finished.emit(result)
            except Exception as e:
                signals.error.emit(str(e))

        self.workers.append(signals)
        threading.Thread(target=run_worker, daemon=True).start()

    def _on_model_loaded(self, result: tuple) -> None:
        """Handle model loading completion."""
        voice, status = result
        self.voice = voice
        self._set_status(status)

    def _refresh_models(self) -> None:
        current = self.model_combo.currentText()
        models = list_models()
        self.model_combo.blockSignals(True)
        self.model_combo.clear()
        self.model_combo.addItems(models)

        if current in models:
            self.model_combo.setCurrentText(current)
        self.model_combo.blockSignals(False)

        if self.model_combo.currentText() not in ("", "No models"):
            self._on_model_changed(self.model_combo.currentText())
        self._set_status("Models refreshed")


    def _add_models(self) -> None:
        """Add model files via file dialog."""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Piper model files",
            "",
            "Piper models (*.onnx *.json);;All files (*.*)"
        )
        
        if not files:
            return

        copied = copy_model_files(files)
        self._set_status(f"Added {copied} file(s)")
        self._refresh_models()

    def _download_voice(self) -> None:
        """Download a voice model."""
        voice_id, ok = QInputDialog.getText(
            self,
            "Download Voice",
            "Enter voice ID (e.g., en_GB-cori-high):"
        )
        
        if not ok or not voice_id.strip():
            return

        voice_id = voice_id.strip()
        self._set_status(f"Downloading: {voice_id}...")

        def worker():
            return download_voice_model(voice_id)

        signals = WorkerSignals()
        signals.finished.connect(self._on_download_complete)
        
        def run_worker():
            try:
                result = worker()
                signals.finished.emit(result)
            except Exception as e:
                signals.error.emit(str(e))

        self.workers.append(signals)
        threading.Thread(target=run_worker, daemon=True).start()

    def _on_download_complete(self, result: tuple) -> None:
        """Handle download completion."""
        success, message = result
        self._set_status(message)
        if success:
            self._refresh_models()

    def _export_wav(self) -> None:
        """Export speech to WAV file."""
        if not self.voice:
            self._set_status("Load a voice model first")
            return

        text = self.text_edit.toPlainText().strip()
        if not text:
            self._set_status("Enter text to speak")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save WAV",
            "speech.wav",
            "WAV files (*.wav)"
        )

        if not file_path:
            return

        self._set_status("Generating WAV...")

        voice = self.voice
        volume = self.volume.value()
        speed = self.speed.value()
        noise = self.noise.value()
        noise_w = self.noise_w.value()
        normalize = self.normalize.isChecked()

        def worker():
            return synthesize_to_wav(
                voice, text, file_path,
                volume, speed, noise, noise_w, normalize
            )

        signals = WorkerSignals()
        signals.finished.connect(lambda r: self._set_status(r[1]))
        
        def run_worker():
            try:
                result = worker()
                signals.finished.emit(result)
            except Exception as e:
                signals.error.emit(str(e))

        self.workers.append(signals)
        threading.Thread(target=run_worker, daemon=True).start()

    def _play_stop(self) -> None:
        """Play or stop audio."""
        if self.audio_player.is_playing():
            self._stop_playback()
        else:
            self._play_audio()

    def _play_audio(self) -> None:
        """Synthesize and play audio."""
        if not self.voice:
            self._set_status("Load a voice model first")
            return

        text = self.text_edit.toPlainText().strip()
        if not text:
            self._set_status("Enter text to speak")
            return

        self._set_status("Synthesizing...")
        self.play_btn.setText("■ Stop")
        self.play_btn.setEnabled(True)

        voice = self.voice
        volume = self.volume.value()
        speed = self.speed.value()
        noise = self.noise.value()
        noise_w = self.noise_w.value()
        normalize = self.normalize.isChecked()

        def worker():
            # Synthesize
            audio, sample_rate, status = synthesize_to_audio_array(
                voice, text, volume, speed, noise, noise_w, normalize
            )
            
            if audio is None:
                return False, status

            # Play
            self.audio_player.play(audio, sample_rate)
            stopped = self.audio_player.wait()
            
            return stopped, "Stopped" if stopped else "Playback complete"

        signals = WorkerSignals()
        signals.status.connect(self._set_status)
        signals.finished.connect(self._on_playback_complete)
        
        def run_worker():
            try:
                signals.status.emit("Playing...")
                result = worker()
                signals.finished.emit(result)
            except Exception as e:
                signals.error.emit(str(e))
                signals.finished.emit((True, f"Playback error: {e}"))

        self.workers.append(signals)
        threading.Thread(target=run_worker, daemon=True).start()

    def _stop_playback(self) -> None:
        """Stop audio playback."""
        self.audio_player.stop()
        self._set_status("Stopping...")

    def _on_playback_complete(self, result: tuple) -> None:
        """Handle playback completion."""
        _, message = result
        self._set_status(message)
        self.play_btn.setText("▶ Play")

    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle window close event."""
        self.audio_player.stop()
        event.accept()
