import os
import pytest
import winzy_screencapture as w
import tempfile
from unittest.mock import patch, MagicMock
from argparse import Namespace, ArgumentParser
from datetime import datetime


@pytest.fixture
def mock_scap_plugin():
    """Fixture to provide a mocked scap_plugin instance."""
    with patch("winzy_screencapture.HelloWorld") as MockHelloWorld:
        instance = MockHelloWorld.return_value
        instance.__name__ = "scap"  # Ensure the name attribute is set
        yield instance


def test_create_parser():
    subparser = ArgumentParser().add_subparsers()
    parser = w.create_parser(subparser)

    assert parser is not None

    result = parser.parse_known_args()[0]
    assert result.path == tempfile.gettempdir()


@patch("winzy_screencapture.datetime")
def test_get_filename_as_current_time(mock_datetime):
    mock_now = MagicMock()
    mock_now.strftime.side_effect = lambda fmt: {
        "%b": "OCT",
        "%d": "21",
        "%Y": "2025",
        "%H": "10",
        "%M": "30",
        "%S": "45",
    }.get(fmt, "")
    mock_now.hour = 10
    mock_datetime.now.return_value = mock_now

    expected_filename = "OCT_21_2025_10_30_45_AM.png"
    assert w.get_filename_as_current_time() == expected_filename

    mock_now.hour = 14  # 2 PM
    mock_datetime.now.return_value = mock_now
    mock_now.strftime.side_effect = lambda fmt: {
        "%b": "OCT",
        "%d": "21",
        "%Y": "2025",
        "%H": "14",
        "%M": "30",
        "%S": "45",
    }.get(fmt, "")
    expected_filename_pm = "OCT_21_2025_14_30_45_PM.png"
    assert w.get_filename_as_current_time() == expected_filename_pm


@patch("winzy_screencapture.ImageGrab.grab")
@patch("winzy_screencapture.print")
def test_get_screenimage(mock_print, mock_grab):
    mock_image = MagicMock()
    mock_grab.return_value = mock_image
    test_filename = "test_screenshot.png"

    w.get_screenimage(test_filename)

    mock_grab.assert_called_once()
    mock_image.save.assert_called_once_with(test_filename)
    mock_print.assert_called_once_with(test_filename)


@patch("winzy_screencapture.get_screenimage")
@patch(
    "winzy_screencapture.get_filename_as_current_time", return_value="mock_filename.png"
)
def test_screen_method(mock_get_filename, mock_get_screenimage):
    args = Namespace(path="/tmp")

    # Create an instance of the actual HelloWorld class for testing its methods
    # We are testing the method 'screen' of the actual class, not the mocked one
    actual_plugin_instance = w.HelloWorld()
    actual_plugin_instance.screen(args)

    mock_get_filename.assert_called_once()
    mock_get_screenimage.assert_called_once_with(
        os.path.join("/tmp", "mock_filename.png")
    )

    # Ensure the register_commands hook is called and sets the func
    subparser = ArgumentParser().add_subparsers()
    actual_plugin_instance.register_commands(subparser)
    parser = subparser.choices["scap"]
    assert parser.get_default("func") == actual_plugin_instance.screen
