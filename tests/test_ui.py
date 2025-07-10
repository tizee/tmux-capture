"""Tests for the terminal UI logic in run_blessed_app."""

import pytest
from unittest.mock import Mock, patch
from . import conftest
tmux_capture = conftest.tmux_capture

class BlessedKey:
    """A mock for blessed's Key object for testing."""
    def __init__(self, value, is_sequence=False, name=None):
        self._value = value
        self.is_sequence = is_sequence
        self.name = name

    def lower(self):
        return self._value.lower()

    def __str__(self):
        return self._value

class MockTerminal:
    """A mock blessed.Terminal for testing UI interactions."""
    def __init__(self, height=24, width=80):
        self.height = height
        self.width = width
        self.clear = "<clear>"
        self.normal = "</normal>"
        self.last_move = None
        self.inkey_sequences = []

    def move_xy(self, x, y):
        self.last_move = (x, y)
        return f"<move_xy({x},{y})>"

    def inkey(self, timeout=None):
        if self.inkey_sequences:
            return self.inkey_sequences.pop(0)
        return ""

    def fullscreen(self):
        return self # Return self to allow use in 'with' statements

    def cbreak(self):
        return self

    def hidden_cursor(self):
        return self

    def __enter__(self):
        return self


    def __exit__(self, type, value, traceback):
        pass

@pytest.fixture
def mock_ui_terminal():
    """Fixture to provide a mock terminal for UI tests."""
    terminal = MockTerminal()
    # Mock blessed functions that return styles
    terminal.on_color_rgb = Mock(return_value="<on_color_rgb>")
    terminal.color_rgb = Mock(return_value="<color_rgb>")
    terminal.bold = "<bold>"
    terminal.dim = "<dim>"
    return terminal

class TestUI:
    """Test cases for the run_blessed_app UI function."""

    def test_user_selects_match(self, mock_ui_terminal):
        """Test a complete user interaction flow where a match is selected."""
        matches = [
            {"text": "https://example.com", "line_idx": 0, "start_col": 0, "end_col": 19, "pattern": "URL", "original_styled_segment": "https://example.com"},
            {"text": "192.168.1.1", "line_idx": 1, "start_col": 0, "end_col": 11, "pattern": "IP_ADDRESS", "original_styled_segment": "192.168.1.1"}
        ]
        lines = ["https://example.com", "192.168.1.1"]

        # Simulate user typing 'j' to select the second hint
        mock_ui_terminal.inkey_sequences = [BlessedKey('j')]

        with patch.object(tmux_capture, 'blessed') as mock_blessed:
            mock_blessed.Terminal.return_value = mock_ui_terminal
            selected_text = tmux_capture.run_blessed_app(mock_ui_terminal, lines, matches)

        assert selected_text == "192.168.1.1"

    def test_user_cancels_with_escape(self, mock_ui_terminal):
        """Test that the UI exits gracefully when the user presses Escape."""
        matches = [{"text": "https://example.com", "line_idx": 0, "start_col": 0, "end_col": 19, "pattern": "URL", "original_styled_segment": "https://example.com"}]
        lines = ["https://example.com"]

        # Simulate user pressing Escape
        mock_ui_terminal.inkey_sequences = [BlessedKey('KEY_ESCAPE', is_sequence=True, name='KEY_ESCAPE')]

        with patch.object(tmux_capture, 'blessed') as mock_blessed:
            mock_blessed.Terminal.return_value = mock_ui_terminal
            selected_text = tmux_capture.run_blessed_app(mock_ui_terminal, lines, matches)

        assert selected_text is None

    def test_user_cancels_with_ctrl_c(self, mock_ui_terminal):
        """Test that the UI exits gracefully when the user presses Ctrl+C."""
        matches = [{"text": "https://example.com", "line_idx": 0, "start_col": 0, "end_col": 19, "pattern": "URL", "original_styled_segment": "https://example.com"}]
        lines = ["https://example.com"]

        # Simulate user pressing Ctrl+C
        mock_ui_terminal.inkey_sequences = [BlessedKey('KEY_CTRL_C', is_sequence=True, name='KEY_CTRL_C')]

        with patch.object(tmux_capture, 'blessed') as mock_blessed:
            mock_blessed.Terminal.return_value = mock_ui_terminal
            selected_text = tmux_capture.run_blessed_app(mock_ui_terminal, lines, matches)

        assert selected_text is None

    def test_user_backspace(self, mock_ui_terminal):
        """Test that backspace correctly removes characters from the input."""
        matches = [{"text": "https://example.com", "line_idx": 0, "start_col": 0, "end_col": 19, "pattern": "URL",
     "original_styled_segment": "https://example.com"}]
        lines = ["https://example.com"]

        # Simulate user typing 'j' (invalid), backspace, then 'h' (valid)
        mock_ui_terminal.inkey_sequences = [
            BlessedKey('j'),  # Invalid hint
            BlessedKey('KEY_BACKSPACE', is_sequence=True, name='KEY_BACKSPACE'),  # Clear input
            BlessedKey('h')  # Valid hint
        ]

        with patch.object(tmux_capture, 'blessed') as mock_blessed:
            mock_blessed.Terminal.return_value = mock_ui_terminal
            selected_text = tmux_capture.run_blessed_app(mock_ui_terminal, lines, matches)

        assert selected_text == "https://example.com"

    def test_user_backspace_with_multi_char_hints(self, mock_ui_terminal):
        """Test backspace with multi-character hints and partial input correction."""
        # Create enough matches to force multi-character hints
        matches = [
            {"text": f"match_{i}", "line_idx": i, "start_col": 0, "end_col": 10,
             "pattern": "URL", "original_styled_segment": f"match_{i}"}
            for i in range(10)  # This will generate hints: h, j, k, l, w, b, e, f, hh, hj
        ]
        lines = [f"match_{i}" for i in range(10)]

        # Simulate user workflow:
        # 1. Start typing 'k'
        # 2. Realize mistake and backspace twice
        # 3. Type 'hj' (for match_9)
        mock_ui_terminal.inkey_sequences = [
            BlessedKey('h'),  # First character of hh
            BlessedKey('KEY_BACKSPACE', is_sequence=True, name='KEY_BACKSPACE'),  # Delete second h
            BlessedKey('h'),  # First character of hj
            BlessedKey('j'),  # Second character of hj
        ]

        with patch.object(tmux_capture, 'blessed') as mock_blessed:
            mock_blessed.Terminal.return_value = mock_ui_terminal
            selected_text = tmux_capture.run_blessed_app(mock_ui_terminal, lines, matches)

        assert selected_text == "match_9"  # Should select the 10th match with 'hj' hint


    def test_invalid_color_configuration(self, mock_ui_terminal):
        """Test that the app exits if color configuration is invalid."""
        matches = [{"text": "https://example.com", "line_idx": 0, "start_col": 0, "end_col": 19, "pattern": "URL", "original_styled_segment": "https://example.com"}]
        lines = ["https://example.com"]

        # Mock hex_to_rgb to raise a ValueError
        with patch.object(tmux_capture, 'hex_to_rgb', side_effect=ValueError("Invalid color")):
            with pytest.raises(SystemExit) as e:
                tmux_capture.run_blessed_app(mock_ui_terminal, lines, matches)
            assert e.value.code == 1

    def test_skip_outside_visible_area(self, mock_ui_terminal):
        """Test that matches outside visible terminal area are skipped."""
        # Create matches inside and outside terminal bounds
        matches = [
            # This match should be visible
            {"text": "visible_match", "line_idx": 5, "start_col": 10, "end_col": 22,
             "pattern": "URL", "original_styled_segment": "visible_match"},
            # This match should be skipped (y position exceeds terminal height)
            {"text": "y_outside_match", "line_idx": 30, "start_col": 10, "end_col": 23,
             "pattern": "URL", "original_styled_segment": "y_outside_match"},
            # This match should be skipped (x position exceeds terminal width)
            {"text": "x_outside_match", "line_idx": 5, "start_col": 90, "end_col": 104,
             "pattern": "URL", "original_styled_segment": "x_outside_match"}
        ]
        lines = ["" for _ in range(35)]  # Create enough lines to have some outside view
        lines[5] = "visible_match x_outside_match"
        lines[30] = "y_outside_match"

        # Mock terminal dimensions (default 24x80)
        mock_ui_terminal.height = 24
        mock_ui_terminal.width = 80

        # Simulate user pressing Escape immediately
        mock_ui_terminal.inkey_sequences = [BlessedKey('KEY_ESCAPE', is_sequence=True, name='KEY_ESCAPE')]

        with patch.object(tmux_capture, 'blessed') as mock_blessed:
            mock_blessed.Terminal.return_value = mock_ui_terminal
            with patch('builtins.print') as mock_print:
                tmux_capture.run_blessed_app(mock_ui_terminal, lines, matches)

                # Verify only the visible match was printed
                printed_output = ''.join([call.args[0] for call in mock_print.call_args_list])
                assert "visible_match" in printed_output
                # Verify y_outside_match hint was not printed
                assert f"move_xy(10, 30)" not in printed_output
                # Verify x_outside_match hint was not printed
                assert f"move_xy(90, 5)" not in printed_output
