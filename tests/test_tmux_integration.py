"""Test tmux integration with mocking for external calls."""

import pytest
import subprocess
import re
from unittest.mock import Mock, patch, MagicMock
from . import conftest
tmux_capture = conftest.tmux_capture


class TestTmuxIntegration:
    """Test tmux integration functionality with mocked external calls."""

    @patch('subprocess.run')
    def test_get_tmux_pane_content_success(self, mock_run):
        """Test successful tmux pane content capture."""
        # Mock successful subprocess call
        mock_result = Mock()
        mock_result.stdout = "line1\nline2\nline3\n"
        mock_run.return_value = mock_result

        result = tmux_capture.get_tmux_pane_content()

        # Should call tmux with correct arguments
        mock_run.assert_called_once_with(
            ['tmux', 'capture-pane', '-p', '-e', '-J'],
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8'
        )

        # Should return lines split by newlines
        assert result == ["line1", "line2", "line3"]

    @patch('subprocess.run')
    def test_get_tmux_pane_content_with_pane_id(self, mock_run):
        """Test tmux pane content capture with specific pane ID."""
        mock_result = Mock()
        mock_result.stdout = "pane content\n"
        mock_run.return_value = mock_result

        result = tmux_capture.get_tmux_pane_content("%1")

        # Should include pane ID in command
        mock_run.assert_called_once_with(
            ['tmux', 'capture-pane', '-p', '-e', '-J', '-t', '%1'],
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8'
        )

        assert result == ["pane content"]

    @patch('subprocess.run')
    def test_get_tmux_pane_content_tmux_not_found(self, mock_run):
        """Test tmux pane content capture when tmux is not found."""
        mock_run.side_effect = FileNotFoundError()

        result = tmux_capture.get_tmux_pane_content()

        assert result == ["Error: 'tmux' command not found."]

    @patch('subprocess.run')
    def test_get_tmux_pane_content_tmux_error(self, mock_run):
        """Test tmux pane content capture when tmux returns error."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, ['tmux'], stderr="no session found"
        )

        result = tmux_capture.get_tmux_pane_content()

        assert result == ["Error capturing tmux pane: no session found"]

    @patch('subprocess.run')
    def test_get_tmux_pane_content_empty_output(self, mock_run):
        """Test tmux pane content capture with empty output."""
        mock_result = Mock()
        mock_result.stdout = ""
        mock_run.return_value = mock_result

        result = tmux_capture.get_tmux_pane_content()

        assert result == []

    @patch('subprocess.run')
    def test_get_tmux_pane_content_multiline_output(self, mock_run):
        """Test tmux pane content capture with multiline output."""
        mock_result = Mock()
        mock_result.stdout = "line1\nline2\n\nline4\n"
        mock_run.return_value = mock_result

        result = tmux_capture.get_tmux_pane_content()

        # Should preserve empty lines
        assert result == ["line1", "line2", "", "line4"]

    @patch('subprocess.run')
    def test_get_tmux_pane_content_with_ansi_sequences(self, mock_run):
        """Test tmux pane content capture with ANSI escape sequences."""
        mock_result = Mock()
        mock_result.stdout = "\x1b[31mRed text\x1b[0m\n\x1b[32mGreen text\x1b[0m\n"
        mock_run.return_value = mock_result

        result = tmux_capture.get_tmux_pane_content()

        # Should preserve ANSI sequences
        assert result == ["\x1b[31mRed text\x1b[0m", "\x1b[32mGreen text\x1b[0m"]

    @patch('subprocess.run')
    def test_main_function_tmux_running_check_success(self, mock_run):
        """Test main function tmux running check success."""
        # Mock successful tmux session check
        mock_run.return_value = Mock()

        # Mock get_tmux_pane_content to return matches
        with patch.object(tmux_capture, 'get_tmux_pane_content') as mock_get_content:
            mock_get_content.return_value = ["https://example.com"]

            # Mock the UI components
            with patch.object(tmux_capture, 'run_blessed_app') as mock_ui:
                mock_ui.return_value = "https://example.com"

                with patch.object(tmux_capture, 'copy_to_clipboard') as mock_copy:
                    mock_copy.return_value = True

                    with patch('builtins.print') as mock_print:
                        with patch.object(tmux_capture, 'blessed') as mock_blessed:
                            mock_terminal = Mock()
                            mock_terminal.strip_seqs = Mock(side_effect=lambda x: re.sub(r'\x1b\[[0-9;]*m', '', x))
                            def mock_length(x):
                                if len(x) == 1:
                                    return 1
                                return len(x)
                            mock_terminal.length = mock_length
                            mock_blessed.Terminal.return_value = mock_terminal

                            # Should not raise any exceptions
                            tmux_capture.main()

                            # Should check if tmux is running
                            mock_run.assert_called_with(
                                ['tmux', 'display-message', '-p', '#S'],
                                check=True,
                                capture_output=True
                            )

    @patch('subprocess.run')
    def test_main_function_tmux_not_running(self, mock_run):
        """Test main function when tmux is not running."""
        # Mock failed tmux session check
        mock_run.side_effect = subprocess.CalledProcessError(1, ['tmux'])

        with patch('sys.exit') as mock_exit:
            mock_exit.side_effect = SystemExit(1)  # Make sys.exit raise SystemExit
            with patch('builtins.print') as mock_print:
                with pytest.raises(SystemExit):
                    tmux_capture.main()

                # Should exit with error
                mock_exit.assert_called_with(1)
                mock_print.assert_called_with(
                    "Error: tmux is not running or not found.",
                    file=tmux_capture.sys.stderr
                )

    @patch('subprocess.run')
    def test_main_function_tmux_not_found(self, mock_run):
        """Test main function when tmux command is not found."""
        # Mock tmux command not found
        mock_run.side_effect = FileNotFoundError()

        with patch('sys.exit') as mock_exit:
            mock_exit.side_effect = SystemExit(1)  # Make sys.exit raise SystemExit
            with patch('builtins.print') as mock_print:
                with pytest.raises(SystemExit):
                    tmux_capture.main()

                # Should exit with error
                mock_exit.assert_called_with(1)
                mock_print.assert_called_with(
                    "Error: tmux is not running or not found.",
                    file=tmux_capture.sys.stderr
                )

    @patch('subprocess.run')
    def test_main_function_with_pane_argument(self, mock_run):
        """Test main function with pane ID argument."""
        # Mock successful tmux session check
        mock_run.return_value = Mock()

        with patch('sys.argv', ['tmux-capture', '%1']):
            with patch.object(tmux_capture, 'get_tmux_pane_content') as mock_get_content:
                mock_get_content.return_value = ["test content"]

                with patch.object(tmux_capture, 'run_blessed_app') as mock_ui:
                    mock_ui.return_value = "test content"

                    with patch.object(tmux_capture, 'copy_to_clipboard') as mock_copy:
                        mock_copy.return_value = True

                        with patch('sys.exit') as mock_exit:
                            mock_exit.side_effect = SystemExit(0)  # Make sys.exit raise SystemExit
                            with patch('builtins.print'):
                                with patch.object(tmux_capture, 'blessed') as mock_blessed:
                                    mock_terminal = Mock()
                                    mock_terminal.strip_seqs = Mock(side_effect=lambda x: re.sub(r'\x1b\[[0-9;]*m', '', x))
                                    def mock_length(x):
                                        if len(x) == 1:
                                            return 1
                                        return len(x)
                                    mock_terminal.length = mock_length
                                    mock_blessed.Terminal.return_value = mock_terminal

                                    with pytest.raises(SystemExit):
                                        tmux_capture.main()

                                # Should call get_tmux_pane_content with pane ID
                                mock_get_content.assert_called_with('%1')

    @patch('subprocess.run')
    def test_main_function_no_matches_found(self, mock_run):
        """Test main function when no matches are found."""
        # Mock successful tmux session check
        mock_run.return_value = Mock()

        with patch.object(tmux_capture, 'get_tmux_pane_content') as mock_get_content:
            mock_get_content.return_value = ["no matches here"]

            with patch.object(tmux_capture, 'find_text_matches') as mock_find:
                mock_find.return_value = []  # No matches

                with patch('sys.exit') as mock_exit:
                    mock_exit.side_effect = SystemExit(0)  # Make sys.exit raise SystemExit
                    with patch('builtins.print') as mock_print:
                        with patch.object(tmux_capture, 'blessed') as mock_blessed:
                            mock_terminal = Mock()
                            mock_terminal.strip_seqs = Mock(side_effect=lambda x: re.sub(r'\x1b\[[0-9;]*m', '', x))
                            def mock_length(x):
                                if len(x) == 1:
                                    return 1
                                return len(x)
                            mock_terminal.length = mock_length
                            mock_blessed.Terminal.return_value = mock_terminal

                            with pytest.raises(SystemExit):
                                tmux_capture.main()

                            # Should exit with success but print no matches message
                            mock_exit.assert_called_with(0)
                            mock_print.assert_called_with(
                                "No matches found in the target pane.",
                                file=tmux_capture.sys.stderr
                            )

    @patch('subprocess.run')
    def test_main_function_pane_content_error(self, mock_run):
        """Test main function when pane content capture fails."""
        # Mock successful tmux session check
        mock_run.return_value = Mock()

        with patch.object(tmux_capture, 'get_tmux_pane_content') as mock_get_content:
            mock_get_content.return_value = ["Error: failed to capture"]

            with patch('sys.exit') as mock_exit:
                mock_exit.side_effect = SystemExit(1)  # Make sys.exit raise SystemExit
                with patch('builtins.print') as mock_print:
                    with patch.object(tmux_capture, 'blessed') as mock_blessed:
                        mock_terminal = Mock()
                        mock_terminal.strip_seqs = Mock(side_effect=lambda x: re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', x))
                        def mock_length(x):
                            if len(x) == 1:
                                return 1
                            return len(x)
                        mock_terminal.length = mock_length
                        mock_blessed.Terminal.return_value = mock_terminal

                        with pytest.raises(SystemExit):
                            tmux_capture.main()

                        # Should exit with error
                        mock_exit.assert_called_with(1)
                        mock_print.assert_called_with(
                            "Error: failed to capture",
                            file=tmux_capture.sys.stderr
                        )

    @patch('subprocess.run')
    def test_main_function_user_cancellation(self, mock_run):
        """Test main function when user cancels selection."""
        # Mock successful tmux session check
        mock_run.return_value = Mock()

        with patch.object(tmux_capture, 'get_tmux_pane_content') as mock_get_content:
            mock_get_content.return_value = ["https://example.com"]

            with patch.object(tmux_capture, 'run_blessed_app') as mock_ui:
                mock_ui.return_value = None  # User cancelled

                with patch('builtins.print') as mock_print:
                    with patch.object(tmux_capture, 'blessed') as mock_blessed:
                        mock_terminal = Mock()
                        mock_terminal.strip_seqs = Mock(side_effect=lambda x: re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', x))
                        def mock_length(x):
                            if len(x) == 1:
                                return 1
                            return len(x)
                        mock_terminal.length = mock_length
                        mock_blessed.Terminal.return_value = mock_terminal

                        tmux_capture.main()

                        # Should print cancellation message
                        mock_print.assert_called_with("Operation cancelled.")

    @patch('subprocess.run')
    def test_main_function_clipboard_copy_success(self, mock_run):
        """Test main function with successful clipboard copy."""
        # Mock successful tmux session check
        mock_run.return_value = Mock()

        with patch.object(tmux_capture, 'get_tmux_pane_content') as mock_get_content:
            mock_get_content.return_value = ["https://example.com"]

            with patch.object(tmux_capture, 'run_blessed_app') as mock_ui:
                mock_ui.return_value = "https://example.com"

                with patch.object(tmux_capture, 'copy_to_clipboard') as mock_copy:
                    mock_copy.return_value = True

                    with patch('builtins.print') as mock_print:
                        with patch.object(tmux_capture, 'blessed') as mock_blessed:
                            mock_terminal = Mock()
                            mock_terminal.strip_seqs = Mock(side_effect=lambda x: re.sub(r'\x1b\[[0-9;]*m', '', x))
                            def mock_length(x):
                                if len(x) == 1:
                                    return 1
                                return len(x)
                            mock_terminal.length = mock_length
                            mock_blessed.Terminal.return_value = mock_terminal

                            tmux_capture.main()

                            # Should print success message
                            mock_print.assert_called_with("Copied 'https://example.com' to clipboard.")

    @patch('subprocess.run')
    def test_main_function_clipboard_copy_failure(self, mock_run):
        """Test main function with failed clipboard copy."""
        # Mock successful tmux session check
        mock_run.return_value = Mock()

        with patch.object(tmux_capture, 'get_tmux_pane_content') as mock_get_content:
            mock_get_content.return_value = ["https://example.com"]

            with patch.object(tmux_capture, 'run_blessed_app') as mock_ui:
                mock_ui.return_value = "https://example.com"

                with patch.object(tmux_capture, 'copy_to_clipboard') as mock_copy:
                    mock_copy.return_value = False  # Copy failed

                    with patch('builtins.print') as mock_print:
                        with patch.object(tmux_capture, 'blessed') as mock_blessed:
                            mock_terminal = Mock()
                            mock_terminal.strip_seqs = Mock(side_effect=lambda x: re.sub(r'\x1b\[[0-9;]*m', '', x))
                            def mock_length(x):
                                if len(x) == 1:
                                    return 1
                                return len(x)
                            mock_terminal.length = mock_length
                            mock_blessed.Terminal.return_value = mock_terminal

                            tmux_capture.main()

                            # Should print failure message
                            mock_print.assert_called_with(
                                "Failed to copy to clipboard. Ensure xclip or xsel is installed on Linux.",
                                file=tmux_capture.sys.stderr
                            )

    def test_tmux_command_structure(self):
        """Test that tmux command structure is correct."""
        # Test the command structure without actually running tmux
        expected_base_cmd = ['tmux', 'capture-pane', '-p', '-e', '-J']

        # Mock subprocess.run to capture the command
        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.stdout = "test output"
            mock_run.return_value = mock_result

            # Test without pane ID
            tmux_capture.get_tmux_pane_content()
            mock_run.assert_called_with(
                expected_base_cmd,
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8'
            )

            # Test with pane ID
            tmux_capture.get_tmux_pane_content("%2")
            mock_run.assert_called_with(
                expected_base_cmd + ['-t', '%2'],
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8'
            )

    def test_tmux_session_check_command(self):
        """Test that tmux session check command is correct."""
        expected_cmd = ['tmux', 'display-message', '-p', '#S']

        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock()

            # Mock other dependencies to prevent full main execution
            with patch.object(tmux_capture, 'get_tmux_pane_content') as mock_get_content:
                mock_get_content.return_value = []

                with patch('sys.exit') as mock_exit:
                    mock_exit.side_effect = SystemExit(0)  # Make sys.exit raise SystemExit
                    with patch('builtins.print'):
                        with patch.object(tmux_capture, 'blessed') as mock_blessed:
                            mock_terminal = Mock()
                            mock_terminal.strip_seqs = Mock(side_effect=lambda x: re.sub(r'\x1b\[[0-9;]*m', '', x))
                            def mock_length(x):
                                if len(x) == 1:
                                    return 1
                                return len(x)
                            mock_terminal.length = mock_length
                            mock_blessed.Terminal.return_value = mock_terminal

                            with pytest.raises(SystemExit):
                                tmux_capture.main()

                            # Should call session check with correct command
                            mock_run.assert_called_with(
                                expected_cmd,
                                check=True,
                                capture_output=True
                            )
