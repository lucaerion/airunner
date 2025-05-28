"""
Unit tests for webcam_nodes.py (WebcamSelectorNode and WebcamDisplayNode).

These tests use pytest and pytest-qt for GUI and node logic validation.
"""

import pytest
from unittest.mock import patch, MagicMock
from PySide6.QtWidgets import QApplication
from airunner.gui.widgets.nodegraph.nodes.video.webcam_nodes import (
    WebcamSelectorWidget,
    WebcamDisplayWidget,
    WebcamSelectorNode,
    WebcamDisplayNode,
)


@pytest.fixture(scope="module")
def app():
    import sys

    app = QApplication.instance() or QApplication(sys.argv)
    yield app


def test_webcam_selector_lists_devices(qtbot):
    with patch(
        "airunner.gui.widgets.nodegraph.nodes.video.webcam_nodes.list_available_webcams",
        return_value=[(0, "Webcam 0"), (1, "Webcam 1")],
    ):
        widget = WebcamSelectorWidget()
        qtbot.addWidget(widget.get_custom_widget())
        assert widget.combo.count() == 2
        assert widget.combo.itemText(0) == "Webcam 0"
        assert widget.combo.itemData(0) == 0
        assert widget.combo.itemText(1) == "Webcam 1"
        assert widget.combo.itemData(1) == 1


def test_webcam_selector_set_value(qtbot):
    with patch(
        "airunner.gui.widgets.nodegraph.nodes.video.webcam_nodes.list_available_webcams",
        return_value=[(0, "Webcam 0"), (1, "Webcam 1")],
    ):
        widget = WebcamSelectorWidget()
        qtbot.addWidget(widget.get_custom_widget())
        widget.set_value(1)
        assert widget.get_value() == 1


def test_webcam_display_set_webcam_index(qtbot):
    widget = WebcamDisplayWidget()
    qtbot.addWidget(widget.get_custom_widget())
    with patch("cv2.VideoCapture") as mock_cap:
        mock_instance = MagicMock()
        mock_instance.isOpened.return_value = True
        mock_cap.return_value = mock_instance
        widget.set_webcam_index(0)
        assert widget._webcam_index == 0
        assert widget.cap.isOpened()


def test_webcam_display_save_frame(qtbot, tmp_path):
    widget = WebcamDisplayWidget()
    qtbot.addWidget(widget.get_custom_widget())
    widget._current_frame = MagicMock()
    with patch("cv2.imwrite") as mock_imwrite, patch(
        "PySide6.QtWidgets.QFileDialog.getSaveFileName",
        return_value=(str(tmp_path / "test.png"), "PNG Files (*.png)"),
    ):
        widget._save_frame()
        mock_imwrite.assert_called()
