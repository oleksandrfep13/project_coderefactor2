import pytest
from unittest.mock import MagicMock
from src.ui.main import main


def test_ui_main_init():
    mock_page = MagicMock()

    try:
        main(mock_page)
    except AttributeError:
        pass

    assert mock_page.add.called