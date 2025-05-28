"""
Webcam nodes for NodeGraphQt integration.

This module provides nodes for selecting a webcam and displaying its live feed, with the ability to capture PNG images at a user-defined interval.

- WebcamSelectorNode: Lists available webcams and outputs the selected device index.
- WebcamDisplayNode: Shows live feed from the selected webcam and saves PNG images at intervals.

Tested on Linux with OpenCV and PySide6.
"""

import cv2
import os
import time
from typing import Dict, Optional
from PySide6.QtCore import QTimer, Signal, Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QComboBox,
    QLabel,
    QSpinBox,
    QPushButton,
    QFileDialog,
)
from PySide6.QtGui import QImage, QPixmap
from airunner.vendor.nodegraphqt import NodeBaseWidget, Port
from airunner.vendor.nodegraphqt.constants import NodePropWidgetEnum
from airunner.gui.widgets.nodegraph.nodes.core.base_workflow_node import (
    BaseWorkflowNode,
)


def list_available_webcams(max_devices: int = 10):
    """Return a list of available webcam indices and names."""
    available = []
    for idx in range(max_devices):
        cap = cv2.VideoCapture(idx)
        if cap.isOpened():
            available.append((idx, f"Webcam {idx}"))
            cap.release()
    return available


class WebcamSelectorWidget(NodeBaseWidget):
    value_changed = Signal(str, object)

    def __init__(self, parent=None, name="webcam_selector", label="Webcam Selector"):
        super().__init__(parent, name, label)
        self.combo = QComboBox()
        self.refresh_button = QPushButton("Refresh")
        self.combo.setObjectName("webcam_selector_combo")
        self.refresh_button.setObjectName("webcam_selector_refresh")
        self.combo.currentIndexChanged.connect(self._on_selection_changed)
        self.refresh_button.clicked.connect(self._refresh)
        layout = QVBoxLayout()
        layout.addWidget(self.combo)
        layout.addWidget(self.refresh_button)
        self.set_custom_widget(QWidget())
        self.get_custom_widget().setLayout(layout)
        self._refresh()

    def _refresh(self):
        self.combo.clear()
        webcams = list_available_webcams()
        if not webcams:
            self.combo.addItem(
                "No webcams detected (If using WSL2, webcam access is not supported)",
                None,
            )
            self.combo.setEnabled(False)
        else:
            for idx, name in webcams:
                self.combo.addItem(name, idx)
            self.combo.setEnabled(True)
        self.value_changed.emit(self._name, self.get_value())

    def _on_selection_changed(self, _):
        self.value_changed.emit(self._name, self.get_value())

    def get_value(self):
        return self.combo.currentData()

    def set_value(self, value):
        idx = self.combo.findData(value)
        if idx >= 0:
            self.combo.setCurrentIndex(idx)


class WebcamSelectorNode(BaseWorkflowNode):
    __identifier__ = "Webcam"
    NODE_NAME = "Webcam Selector"
    _output_ports = [dict(name="webcam_index", display_name=True)]
    _properties = [
        dict(
            name="webcam_index",
            value=0,
            widget_type=NodePropWidgetEnum.INT,
            tab="settings",
        )
    ]

    def __init__(self):
        super().__init__()
        self.widget = WebcamSelectorWidget(self.view, name="webcam_selector")
        self.add_custom_widget(self.widget)
        self.widget.value_changed.connect(self._on_widget_changed)

    def _on_widget_changed(self, name, value):
        self.set_property("webcam_index", value)

    def execute(self, input_data: Dict):
        idx = self.get_property("webcam_index")
        return {"webcam_index": idx}


class WebcamDisplayWidget(NodeBaseWidget):
    value_changed = Signal(str, object)

    def __init__(self, parent=None, name="webcam_display", label="Webcam Display"):
        super().__init__(parent, name, label)
        self.label = QLabel("No feed")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setObjectName("webcam_display_label")
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 60)
        self.interval_spin.setValue(5)
        self.interval_spin.setSuffix(" s")
        self.interval_spin.setObjectName("webcam_display_interval")
        self.save_button = QPushButton("Save Snapshot")
        self.save_button.setObjectName("webcam_display_save")
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.interval_spin)
        layout.addWidget(self.save_button)
        self.set_custom_widget(QWidget())
        self.get_custom_widget().setLayout(layout)
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_frame)
        self.save_timer = QTimer()
        self.save_timer.timeout.connect(self._save_frame)
        self.save_button.clicked.connect(self._save_frame)
        self._current_frame = None
        self._webcam_index = 0
        self._save_dir = os.getcwd()
        self.interval_spin.valueChanged.connect(self._on_interval_changed)
        self._on_interval_changed()

    def set_webcam_index(self, idx):
        if self.cap:
            self.cap.release()
        self.cap = cv2.VideoCapture(idx)
        self._webcam_index = idx
        if self.cap.isOpened():
            self.timer.start(30)
        else:
            self.label.setText("Webcam not available")
            self.timer.stop()

    def _update_frame(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb.shape
                bytes_per_line = ch * w
                qimg = QImage(
                    rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888
                )
                pixmap = QPixmap.fromImage(qimg).scaled(
                    320, 240, Qt.AspectRatioMode.KeepAspectRatio
                )
                self.label.setPixmap(pixmap)
                self._current_frame = frame
            else:
                self.label.setText("No frame")

    def _on_interval_changed(self):
        self.save_timer.stop()
        interval = self.interval_spin.value()
        self.save_timer.start(interval * 1000)

    def _save_frame(self):
        if self._current_frame is not None:
            fname = time.strftime("webcam_%Y%m%d_%H%M%S.png")
            path, _ = QFileDialog.getSaveFileName(
                self.get_custom_widget(),
                "Save Image",
                os.path.join(self._save_dir, fname),
                "PNG Files (*.png)",
            )
            if path:
                cv2.imwrite(path, self._current_frame)

    def get_value(self):
        return self._webcam_index

    def set_value(self, value):
        self.set_webcam_index(value)

    def cleanup(self):
        if self.cap:
            self.cap.release()
        self.timer.stop()
        self.save_timer.stop()


class WebcamDisplayNode(BaseWorkflowNode):
    __identifier__ = "Webcam"
    NODE_NAME = "Webcam Display"
    _input_ports = [dict(name="webcam_index", display_name=True)]
    _properties = [
        dict(
            name="webcam_index",
            value=0,
            widget_type=NodePropWidgetEnum.INT,
            tab="settings",
        )
    ]

    def __init__(self):
        super().__init__()
        self.widget = WebcamDisplayWidget(self.view, name="webcam_display")
        self.add_custom_widget(self.widget)

    def on_input_connected(self, in_port: Port, out_port: Port):
        super().on_input_connected(in_port, out_port)
        if in_port.name() == "webcam_index":
            from_node = out_port.node()
            if from_node:
                value = from_node.execute({})
                idx = value.get(out_port.name())
                if idx is not None:
                    self.widget.set_webcam_index(idx)

    def execute(self, input_data: Dict):
        idx = input_data.get("webcam_index") or self.get_property("webcam_index")
        self.widget.set_webcam_index(idx)
        return {"webcam_index": idx}

    def on_node_deleted(self):
        if hasattr(self, "widget"):
            self.widget.cleanup()
        super().on_node_deleted()


def register_nodes(registry):
    registry.register_node("Webcam", WebcamSelectorNode)
    registry.register_node("Webcam", WebcamDisplayNode)
