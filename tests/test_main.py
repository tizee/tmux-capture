"""Tests for the main function and its exception handling."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
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