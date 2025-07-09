"""Test clipboard operations with platform-specific mocking."""

import pytest
import subprocess
import sys
from unittest.mock import Mock, patch
from . import conftest
tmux_capture = conftest.tmux_capture


class TestClipboardOperations:
    """Test clipboard operations with mocked platform-specific commands."""
    
    @patch('sys.platform', 'darwin')
    @patch('subprocess.run')
    def test_copy_to_clipboard_macos_success(self, mock_run):
        """Test successful clipboard copy on macOS."""
        mock_run.return_value = Mock()
        
        result = tmux_capture.copy_to_clipboard("test text")
        
        assert result is True
        mock_run.assert_called_once_with(
            ['pbcopy'],
            input=b'test text',
            check=True
        )
    
    @patch('sys.platform', 'darwin')
    @patch('subprocess.run')
    def test_copy_to_clipboard_macos_failure(self, mock_run):
        """Test failed clipboard copy on macOS."""
        mock_run.side_effect = subprocess.CalledProcessError(1, ['pbcopy'])
        
        result = tmux_capture.copy_to_clipboard("test text")
        
        assert result is False
        mock_run.assert_called_once_with(
            ['pbcopy'],
            input=b'test text',
            check=True
        )
    
    @patch('sys.platform', 'darwin')
    @patch('subprocess.run')
    def test_copy_to_clipboard_macos_command_not_found(self, mock_run):
        """Test clipboard copy on macOS when pbcopy is not found."""
        mock_run.side_effect = FileNotFoundError()
        
        result = tmux_capture.copy_to_clipboard("test text")
        
        assert result is False
    
    @patch('sys.platform', 'linux')
    @patch('subprocess.run')
    def test_copy_to_clipboard_linux_xclip_success(self, mock_run):
        """Test successful clipboard copy on Linux with xclip."""
        mock_run.return_value = Mock()
        
        result = tmux_capture.copy_to_clipboard("test text")
        
        assert result is True
        mock_run.assert_called_once_with(
            ['xclip', '-selection', 'clipboard'],
            input=b'test text',
            check=True
        )
    
    @patch('sys.platform', 'linux')
    @patch('subprocess.run')
    def test_copy_to_clipboard_linux_xclip_fallback_to_xsel(self, mock_run):
        """Test clipboard copy on Linux falling back from xclip to xsel."""
        # First call (xclip) fails, second call (xsel) succeeds
        mock_run.side_effect = [
            subprocess.CalledProcessError(1, ['xclip']),
            Mock()  # xsel succeeds
        ]
        
        result = tmux_capture.copy_to_clipboard("test text")
        
        assert result is True
        assert mock_run.call_count == 2
        
        # Check first call was xclip
        first_call = mock_run.call_args_list[0]
        assert first_call[0][0] == ['xclip', '-selection', 'clipboard']
        
        # Check second call was xsel
        second_call = mock_run.call_args_list[1]
        assert second_call[0][0] == ['xsel', '--clipboard', '--input']
    
    @patch('sys.platform', 'linux')
    @patch('subprocess.run')
    def test_copy_to_clipboard_linux_xclip_not_found_fallback_to_xsel(self, mock_run):
        """Test clipboard copy on Linux when xclip is not found, fallback to xsel."""
        # First call (xclip) command not found, second call (xsel) succeeds
        mock_run.side_effect = [
            FileNotFoundError(),
            Mock()  # xsel succeeds
        ]
        
        result = tmux_capture.copy_to_clipboard("test text")
        
        assert result is True
        assert mock_run.call_count == 2
    
    @patch('sys.platform', 'linux')
    @patch('subprocess.run')
    def test_copy_to_clipboard_linux_both_fail(self, mock_run):
        """Test clipboard copy on Linux when both xclip and xsel fail."""
        # Both calls fail
        mock_run.side_effect = [
            subprocess.CalledProcessError(1, ['xclip']),
            subprocess.CalledProcessError(1, ['xsel'])
        ]
        
        result = tmux_capture.copy_to_clipboard("test text")
        
        assert result is False
        assert mock_run.call_count == 2
    
    @patch('sys.platform', 'linux')
    @patch('subprocess.run')
    def test_copy_to_clipboard_linux_both_not_found(self, mock_run):
        """Test clipboard copy on Linux when both xclip and xsel are not found."""
        # Both commands not found
        mock_run.side_effect = [
            FileNotFoundError(),
            FileNotFoundError()
        ]
        
        result = tmux_capture.copy_to_clipboard("test text")
        
        assert result is False
        assert mock_run.call_count == 2
    
    def test_copy_to_clipboard_empty_text(self):
        """Test clipboard copy with empty text."""
        result = tmux_capture.copy_to_clipboard("")
        
        assert result is False
    
    def test_copy_to_clipboard_none_text(self):
        """Test clipboard copy with None text."""
        result = tmux_capture.copy_to_clipboard(None)
        
        assert result is False
    
    @patch('sys.platform', 'darwin')
    @patch('subprocess.run')
    def test_copy_to_clipboard_unicode_text(self, mock_run):
        """Test clipboard copy with unicode text."""
        mock_run.return_value = Mock()
        
        unicode_text = "Hello 世界 🌍"
        result = tmux_capture.copy_to_clipboard(unicode_text)
        
        assert result is True
        mock_run.assert_called_once_with(
            ['pbcopy'],
            input=unicode_text.encode('utf-8'),
            check=True
        )
    
    @patch('sys.platform', 'darwin')
    @patch('subprocess.run')
    def test_copy_to_clipboard_multiline_text(self, mock_run):
        """Test clipboard copy with multiline text."""
        mock_run.return_value = Mock()
        
        multiline_text = "Line 1\nLine 2\nLine 3"
        result = tmux_capture.copy_to_clipboard(multiline_text)
        
        assert result is True
        mock_run.assert_called_once_with(
            ['pbcopy'],
            input=multiline_text.encode('utf-8'),
            check=True
        )
    
    @patch('sys.platform', 'darwin')
    @patch('subprocess.run')
    def test_copy_to_clipboard_special_characters(self, mock_run):
        """Test clipboard copy with special characters."""
        mock_run.return_value = Mock()
        
        special_text = "Special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?"
        result = tmux_capture.copy_to_clipboard(special_text)
        
        assert result is True
        mock_run.assert_called_once_with(
            ['pbcopy'],
            input=special_text.encode('utf-8'),
            check=True
        )
    
    @patch('sys.platform', 'linux')
    @patch('subprocess.run')
    def test_copy_to_clipboard_linux_xsel_parameters(self, mock_run):
        """Test that xsel is called with correct parameters."""
        # xclip fails, xsel succeeds
        mock_run.side_effect = [
            subprocess.CalledProcessError(1, ['xclip']),
            Mock()
        ]
        
        result = tmux_capture.copy_to_clipboard("test text")
        
        assert result is True
        
        # Check xsel call parameters
        xsel_call = mock_run.call_args_list[1]
        assert xsel_call[0][0] == ['xsel', '--clipboard', '--input']
        assert xsel_call[1]['input'] == b'test text'
        assert xsel_call[1]['check'] is True
    
    @patch('sys.platform', 'win32')
    def test_copy_to_clipboard_unsupported_platform(self):
        """Test clipboard copy on unsupported platform."""
        # Should not make any subprocess calls and return False
        result = tmux_capture.copy_to_clipboard("test text")
        
        assert result is False
    
    @patch('sys.platform', 'darwin')
    @patch('subprocess.run')
    def test_copy_to_clipboard_large_text(self, mock_run):
        """Test clipboard copy with large text."""
        mock_run.return_value = Mock()
        
        # Create a large text string
        large_text = "A" * 10000
        result = tmux_capture.copy_to_clipboard(large_text)
        
        assert result is True
        mock_run.assert_called_once_with(
            ['pbcopy'],
            input=large_text.encode('utf-8'),
            check=True
        )
    
    @patch('sys.platform', 'linux')
    @patch('subprocess.run')
    def test_copy_to_clipboard_linux_encoding_handling(self, mock_run):
        """Test that Linux clipboard handles encoding correctly."""
        mock_run.return_value = Mock()
        
        # Text with various encodings
        text_with_encoding = "ASCII text with émojis 🚀 and ñoñó"
        result = tmux_capture.copy_to_clipboard(text_with_encoding)
        
        assert result is True
        mock_run.assert_called_once_with(
            ['xclip', '-selection', 'clipboard'],
            input=text_with_encoding.encode('utf-8'),
            check=True
        )
    
    @patch('sys.platform', 'darwin')
    @patch('subprocess.run')
    def test_copy_to_clipboard_macos_encoding_handling(self, mock_run):
        """Test that macOS clipboard handles encoding correctly."""
        mock_run.return_value = Mock()
        
        # Text with various encodings
        text_with_encoding = "macOS text with émojis 🍎 and special chars"
        result = tmux_capture.copy_to_clipboard(text_with_encoding)
        
        assert result is True
        mock_run.assert_called_once_with(
            ['pbcopy'],
            input=text_with_encoding.encode('utf-8'),
            check=True
        )
    
    def test_copy_to_clipboard_text_types(self):
        """Test clipboard copy with different text types."""
        with patch('sys.platform', 'darwin'):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock()
                
                # Test with string
                assert tmux_capture.copy_to_clipboard("string") is True
                
                # Test with bytes (should fail because bytes don't have encode method)
                with pytest.raises(AttributeError):
                    tmux_capture.copy_to_clipboard(b"bytes")
                
                # Test with number (should fail because numbers don't have encode method)
                with pytest.raises(AttributeError):
                    tmux_capture.copy_to_clipboard(123)
    
    @patch('sys.platform', 'linux')
    @patch('subprocess.run')
    def test_copy_to_clipboard_linux_command_precedence(self, mock_run):
        """Test that Linux tries xclip first, then xsel."""
        mock_run.return_value = Mock()
        
        result = tmux_capture.copy_to_clipboard("test text")
        
        assert result is True
        # Should try xclip first
        mock_run.assert_called_once_with(
            ['xclip', '-selection', 'clipboard'],
            input=b'test text',
            check=True
        )
        
        # Reset mock and test fallback
        mock_run.reset_mock()
        mock_run.side_effect = [
            subprocess.CalledProcessError(1, ['xclip']),
            Mock()
        ]
        
        result = tmux_capture.copy_to_clipboard("test text")
        
        assert result is True
        assert mock_run.call_count == 2
        
        # First call should be xclip
        first_call = mock_run.call_args_list[0]
        assert first_call[0][0] == ['xclip', '-selection', 'clipboard']
        
        # Second call should be xsel
        second_call = mock_run.call_args_list[1]
        assert second_call[0][0] == ['xsel', '--clipboard', '--input']