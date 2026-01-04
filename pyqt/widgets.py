### widgets.py ###
"""Reusable PyQt6 UI widgets."""
from __future__ import annotations

from dataclasses import dataclass

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QSlider,
    QVBoxLayout,
    QWidget,
)


@dataclass(frozen=True)
class SliderConfig:
    """Configuration for a float slider."""

    label: str
    min_val: float
    max_val: float
    default: float
    step: float = 0.01


class FloatSlider(QWidget):
    """Horizontal slider for float values with label and display."""

    valueChanged = pyqtSignal(float)

    def __init__(self, config: SliderConfig, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.config = config

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        label = QLabel(config.label)
        label.setMinimumWidth(60)
        layout.addWidget(label)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        steps = int((config.max_val - config.min_val) / config.step)
        self.slider.setRange(0, steps)
        self.slider.valueChanged.connect(self._on_change)
        layout.addWidget(self.slider, 1)

        self.display = QLabel()
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display.setFixedWidth(40)
        layout.addWidget(self.display)

        self.set_value(config.default)

    def value(self) -> float:
        """Get current float value."""
        return self.config.min_val + (self.slider.value() * self.config.step)

    def set_value(self, val: float) -> None:
        """Set float value."""
        val = max(self.config.min_val, min(self.config.max_val, val))
        steps = int((val - self.config.min_val) / self.config.step)
        self.slider.blockSignals(True)
        self.slider.setValue(steps)
        self.slider.blockSignals(False)
        self._update_display()

    def _on_change(self) -> None:
        """Handle slider value change."""
        self._update_display()
        self.valueChanged.emit(self.value())

    def _update_display(self) -> None:
        """Update value display label."""
        self.display.setText(f"{self.value():.2f}")


class Card(QFrame):
    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("Card")

        self._card_layout = QVBoxLayout(self)
        self._card_layout.setContentsMargins(10, 10, 10, 10)
        self._card_layout.setSpacing(8)

        title_label = QLabel(title)
        title_label.setObjectName("CardTitle")
        self._card_layout.addWidget(title_label)

    def add_widget(self, widget: QWidget) -> None:
        """Add widget to card layout."""
        self._card_layout.addWidget(widget)

    def add_layout(self, layout: QHBoxLayout | QVBoxLayout) -> None:
        """Add layout to card layout."""
        self._card_layout.addLayout(layout)
