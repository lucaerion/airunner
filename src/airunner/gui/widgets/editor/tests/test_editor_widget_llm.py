import pytest
from unittest.mock import MagicMock
from airunner.gui.widgets.editor.editor_widget import EditorWidget
from airunner.enums import SignalCode


@pytest.fixture
def mock_api():
    api = MagicMock()
    api.llm = MagicMock()
    api.register = MagicMock()
    return api


@pytest.fixture
def editor_widget_with_api(qtbot, mock_api):
    widget = EditorWidget(api=mock_api)
    qtbot.addWidget(widget)
    return widget


def test_send_content_to_llm(editor_widget_with_api, mock_api):
    editor_widget_with_api.set_content_from_llm("print('test')")
    editor_widget_with_api.ui.languageComboBox.setCurrentText("Python")
    editor_widget_with_api.send_content_to_llm()
    assert mock_api.llm.send_request.called


def test_on_llm_response_streamed(editor_widget_with_api):
    response_data = {"response": {"message": "LLM output"}}
    editor_widget_with_api.on_llm_response_streamed(response_data)
    assert editor_widget_with_api.get_content_for_llm() == "LLM output"
