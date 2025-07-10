"""Tests for the main function and its exception handling."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import termios
from . import conftest
tmux_capture = conftest.tmux_capture


class TestMainExceptionHandling:
    """Test cases for main function exception handling."""

    @patch('sys.argv', ['tmux-capture'])
    @patch.object(tmux_capture.subprocess, 'run')
    @patch.object(tmux_capture, 'get_tmux_pane_content')
    @patch.object(tmux_capture, 'find_text_matches')
    @patch.object(tmux_capture, 'run_blessed_app')
    def test_main_keyboard_interrupt_handling(self, mock_run_blessed_app, mock_find_matches, mock_get_content, mock_subprocess_run):
        """Test that main function handles KeyboardInterrupt gracefully."""
        # Setup mocks for successful preconditions
        mock_subprocess_run.return_value = Mock(returncode=0)
        mock_get_content.return_value = ["test line 1", "test line 2"]
        mock_find_matches.return_value = [{"text": "test", "line_idx": 0, "start_col": 0, "end_col": 4, "pattern": "test", "original_styled_segment": "test"}]
        
        # Mock run_blessed_app to raise KeyboardInterrupt
        mock_run_blessed_app.side_effect = KeyboardInterrupt("User interrupted")
        
        # Mock blessed.Terminal
        with patch.object(tmux_capture, 'blessed') as mock_blessed:
            mock_terminal = Mock()
            mock_blessed.Terminal.return_value = mock_terminal
            
            with pytest.raises(SystemExit) as e:
                tmux_capture.main()
            
            # Should exit with code 0 for KeyboardInterrupt
            assert e.value.code == 0

    @patch('sys.argv', ['tmux-capture'])
    @patch.object(tmux_capture.subprocess, 'run')
    @patch.object(tmux_capture, 'get_tmux_pane_content')
    @patch.object(tmux_capture, 'find_text_matches')
    @patch.object(tmux_capture, 'run_blessed_app')
    def test_main_general_exception_handling(self, mock_run_blessed_app, mock_find_matches, mock_get_content, mock_subprocess_run):
        """Test that main function handles general exceptions gracefully."""
        # Setup mocks for successful preconditions
        mock_subprocess_run.return_value = Mock(returncode=0)
        mock_get_content.return_value = ["test line 1", "test line 2"]
        mock_find_matches.return_value = [{"text": "test", "line_idx": 0, "start_col": 0, "end_col": 4, "pattern": "test", "original_styled_segment": "test"}]
        
        # Mock run_blessed_app to raise a general exception
        mock_run_blessed_app.side_effect = RuntimeError("Terminal error occurred")
        
        # Mock blessed.Terminal
        with patch.object(tmux_capture, 'blessed') as mock_blessed:
            mock_terminal = Mock()
            mock_blessed.Terminal.return_value = mock_terminal
            
            with pytest.raises(SystemExit) as e:
                tmux_capture.main()
            
            # Should exit with code 1 for general exceptions
            assert e.value.code == 1

    @patch('sys.argv', ['tmux-capture'])
    @patch.object(tmux_capture.subprocess, 'run')
    @patch.object(tmux_capture, 'get_tmux_pane_content')
    @patch.object(tmux_capture, 'find_text_matches')
    @patch.object(tmux_capture, 'run_blessed_app')
    @patch.object(tmux_capture, 'copy_to_clipboard')
    def test_main_successful_execution_flow(self, mock_copy, mock_run_blessed_app, mock_find_matches, mock_get_content, mock_subprocess_run):
        """Test the complete main function execution flow with successful selection."""
        # Setup mocks for successful execution
        mock_subprocess_run.return_value = Mock(returncode=0)
        mock_get_content.return_value = ["https://example.com"]
        mock_find_matches.return_value = [{"text": "https://example.com", "line_idx": 0, "start_col": 0, "end_col": 19, "pattern": "URL", "original_styled_segment": "https://example.com"}]
        mock_run_blessed_app.return_value = "https://example.com"
        mock_copy.return_value = True
        
        # Mock blessed.Terminal
        with patch.object(tmux_capture, 'blessed') as mock_blessed:
            mock_terminal = Mock()
            mock_blessed.Terminal.return_value = mock_terminal
            
            # Capture print output
            with patch('builtins.print') as mock_print:
                tmux_capture.main()
                
                # Verify success message was printed
                mock_print.assert_called_with("Copied 'https://example.com' to clipboard.")

    @patch('sys.argv', ['tmux-capture'])
    @patch.object(tmux_capture.subprocess, 'run')
    @patch.object(tmux_capture, 'get_tmux_pane_content')
    @patch.object(tmux_capture, 'find_text_matches')
    @patch.object(tmux_capture, 'run_blessed_app')
    def test_main_operation_cancelled(self, mock_run_blessed_app, mock_find_matches, mock_get_content, mock_subprocess_run):
        """Test main function when user cancels operation."""
        # Setup mocks for successful preconditions
        mock_subprocess_run.return_value = Mock(returncode=0)
        mock_get_content.return_value = ["https://example.com"]
        mock_find_matches.return_value = [{"text": "https://example.com", "line_idx": 0, "start_col": 0, "end_col": 19, "pattern": "URL", "original_styled_segment": "https://example.com"}]
        mock_run_blessed_app.return_value = None  # User cancelled
        
        # Mock blessed.Terminal
        with patch.object(tmux_capture, 'blessed') as mock_blessed:
            mock_terminal = Mock()
            mock_blessed.Terminal.return_value = mock_terminal
            
            # Capture print output
            with patch('builtins.print') as mock_print:
                tmux_capture.main()
                
                # Verify cancellation message was printed
                mock_print.assert_called_with("Operation cancelled.")


class TestEnsureTerminalControl:
    """Test cases for ensure_terminal_control function."""

    @patch('sys.stdin')
    @patch('os.isatty')
    @patch('termios.tcgetattr')
    def test_ensure_terminal_control_already_tty_success(self, mock_tcgetattr, mock_isatty, mock_stdin):
        """Test when stdin is already a proper TTY with terminal attributes."""
        mock_stdin.fileno.return_value = 0
        mock_isatty.return_value = True
        mock_tcgetattr.return_value = None  # No exception means success
        
        result = tmux_capture.ensure_terminal_control()
        
        assert result is True
        mock_isatty.assert_called_once_with(0)  # sys.stdin.fileno()
        mock_tcgetattr.assert_called_once_with(0)

    @patch('sys.stdin')
    @patch('os.isatty')
    @patch('termios.tcgetattr')
    @patch('os.open')
    @patch('os.dup2')
    @patch('os.close')
    @patch('builtins.print')
    def test_ensure_terminal_control_tty_no_attributes_success(
        self, mock_print, mock_close, mock_dup2, mock_open, mock_tcgetattr, mock_isatty, mock_stdin
    ):
        """Test when stdin is TTY but lacks attributes, successfully opens /dev/tty."""
        mock_stdin.fileno.return_value = 0
        # First call: stdin is TTY but lacks attributes
        mock_isatty.side_effect = [True, True]  # First for initial check, second for verification
        # First call raises error, second and third succeed
        mock_tcgetattr.side_effect = [termios.error("No attributes"), None, None]
        mock_open.return_value = 5  # Mock file descriptor
        
        result = tmux_capture.ensure_terminal_control()
        
        assert result is True
        mock_open.assert_called_once_with('/dev/tty', os.O_RDWR)
        mock_dup2.assert_called_once_with(5, 0)  # Replace stdin
        mock_close.assert_called_once_with(5)

    @patch('sys.stdin')
    @patch('os.isatty')
    @patch('termios.tcgetattr')
    @patch('os.open')
    @patch('builtins.print')
    def test_ensure_terminal_control_cannot_open_dev_tty(
        self, mock_print, mock_open, mock_tcgetattr, mock_isatty, mock_stdin
    ):
        """Test when cannot open /dev/tty."""
        mock_stdin.fileno.return_value = 0
        mock_isatty.return_value = True
        mock_tcgetattr.side_effect = termios.error("No attributes")
        mock_open.side_effect = OSError("Permission denied")
        
        result = tmux_capture.ensure_terminal_control()
        
        assert result is False
        mock_print.assert_any_call("Warning: Could not establish terminal control: Permission denied", file=sys.stderr)
        mock_print.assert_any_call("The application may not respond to keyboard input properly.", file=sys.stderr)

    @patch('sys.stdin')
    @patch('os.isatty')
    @patch('termios.tcgetattr')
    @patch('os.open')
    @patch('os.dup2')
    @patch('os.close')
    @patch('builtins.print')
    def test_ensure_terminal_control_tcgetattr_fails_after_replacement(
        self, mock_print, mock_close, mock_dup2, mock_open, mock_tcgetattr, mock_isatty, mock_stdin
    ):
        """Test when /dev/tty opens but tcgetattr fails during verification."""
        mock_stdin.fileno.return_value = 0
        mock_isatty.side_effect = [True, True]  # Both calls return True
        # First fails, second succeeds for /dev/tty, third fails for verification
        mock_tcgetattr.side_effect = [termios.error("No attributes"), None, OSError("Failed")]
        mock_open.return_value = 5
        
        result = tmux_capture.ensure_terminal_control()
        
        assert result is False
        mock_open.assert_called_once_with('/dev/tty', os.O_RDWR)
        mock_dup2.assert_called_once_with(5, 0)
        mock_close.assert_called_once_with(5)

    @patch('sys.stdin')
    @patch('os.isatty')
    @patch('termios.tcgetattr')
    @patch('os.open')
    @patch('os.dup2')
    @patch('os.close')
    @patch('builtins.print')
    def test_ensure_terminal_control_isatty_fails_after_replacement(
        self, mock_print, mock_close, mock_dup2, mock_open, mock_tcgetattr, mock_isatty, mock_stdin
    ):
        """Test when /dev/tty opens but isatty fails during verification."""
        mock_stdin.fileno.return_value = 0
        mock_isatty.side_effect = [True, False]  # Second call returns False
        mock_tcgetattr.side_effect = [termios.error("No attributes"), None]
        mock_open.return_value = 5
        
        result = tmux_capture.ensure_terminal_control()
        
        assert result is False
        mock_open.assert_called_once_with('/dev/tty', os.O_RDWR)
        mock_dup2.assert_called_once_with(5, 0)
        mock_close.assert_called_once_with(5)

    @patch('sys.stdin')
    @patch('builtins.print')
    def test_ensure_terminal_control_unexpected_exception(self, mock_print, mock_stdin):
        """Test handling of unexpected exceptions."""
        mock_stdin.fileno.side_effect = RuntimeError("Unexpected error")
        
        result = tmux_capture.ensure_terminal_control()
        
        assert result is False
        mock_print.assert_called_once_with("Warning: Terminal control setup failed: Unexpected error", file=sys.stderr)

    @patch('sys.stdin')
    @patch('os.isatty')
    def test_ensure_terminal_control_not_tty_fallback(self, mock_isatty, mock_stdin):
        """Test when stdin is not a TTY, should return False without further attempts."""
        mock_stdin.fileno.return_value = 0
        mock_isatty.return_value = False
        
        result = tmux_capture.ensure_terminal_control()
        
        assert result is False
        mock_isatty.assert_called_once_with(0)