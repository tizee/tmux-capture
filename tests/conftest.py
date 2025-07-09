"""Pytest configuration and fixtures for tmux-capture tests."""

import pytest
import sys
import os
import re
from unittest.mock import Mock, MagicMock

# Add the parent directory to sys.path to import the tmux-capture module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the main module (single file script)
import importlib.util
import importlib.machinery

script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tmux-capture")

# Check if the script file exists
if not os.path.exists(script_path):
    raise FileNotFoundError(f"tmux-capture script not found at: {script_path}")

# Create a spec with explicit SourceFileLoader for files without .py extension
loader = importlib.machinery.SourceFileLoader("tmux_capture", script_path)
spec = importlib.util.spec_from_loader("tmux_capture", loader)

tmux_capture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tmux_capture)

@pytest.fixture
def mock_terminal():
    """Create a mock blessed Terminal instance."""
    terminal = Mock()
    # Mock strip_seqs to remove ANSI sequences
    terminal.strip_seqs = Mock(side_effect=lambda x: re.sub(r'\x1b\[[0-9;]*m', '', x))
    # Mock length to return 1 for single characters (terminal display width)
    def mock_length(x):
        if len(x) == 1:
            return 1
        return len(x)
    terminal.length = mock_length
    terminal.height = 24
    terminal.width = 80
    terminal.clear = ''
    terminal.normal = ''
    terminal.move_xy = Mock(return_value='')
    terminal.on_color_rgb = Mock(return_value='')
    terminal.color_rgb = Mock(return_value='')
    terminal.bold = ''
    terminal.dim = ''
    return terminal

@pytest.fixture
def sample_ansi_lines():
    """Sample tmux pane content with ANSI escape sequences."""
    return [
        "Welcome to the terminal!",
        "Visit https://github.com/user/repo for more info",
        "IP address: 192.168.1.100:8080",
        "Email: user@example.com",
        "Git commit: a1b2c3d4e5f6789",
        "\x1b[31mError:\x1b[0m Connection failed",
        "File: /home/user/document.txt",
        "UUID: 550e8400-e29b-41d4-a716-446655440000",
        "Docker: sha256:abcdef123456789abcdef123456789abcdef123456789abcdef123456789abcdef",
        "IPv6: 2001:0db8:85a3:0000:0000:8a2e:0370:7334",
        "Memory: 0xdeadbeef",
        "Large number: 123456789",
        "Hex color: #ff0000",
        "Markdown: [Link](https://example.com)",
        "diff --git a/file.txt b/file.txt",
        "--- a/old_file.txt",
        "+++ b/new_file.txt",
        "MAC: 00:11:22:33:44:55",
        "IPFS: QmYwAPJzv5CZsnAzt8auVNDE7yFbZcyZLfbqUJnRDvfYKL",
    ]

@pytest.fixture
def sample_clean_lines():
    """Sample tmux pane content without ANSI sequences."""
    return [
        "Welcome to the terminal!",
        "Visit https://github.com/user/repo for more info",
        "IP address: 192.168.1.100:8080",
        "Email: user@example.com",
        "Git commit: a1b2c3d4e5f6789",
        "Error: Connection failed",
        "File: /home/user/document.txt",
        "UUID: 550e8400-e29b-41d4-a716-446655440000",
        "Docker: sha256:abcdef123456789abcdef123456789abcdef123456789abcdef123456789abcdef",
        "IPv6: 2001:0db8:85a3:0000:0000:8a2e:0370:7334",
        "Memory: 0xdeadbeef",
        "Large number: 123456789",
        "Hex color: #ff0000",
        "Markdown: [Link](https://example.com)",
        "diff --git a/file.txt b/file.txt",
        "--- a/old_file.txt",
        "+++ b/new_file.txt",
        "MAC: 00:11:22:33:44:55",
        "IPFS: QmYwAPJzv5CZsnAzt8auVNDE7yFbZcyZLfbqUJnRDvfYKL",
    ]

@pytest.fixture
def expected_matches():
    """Expected matches for the sample content."""
    return [
        {"text": "https://github.com/user/repo", "pattern": "URL", "line_idx": 1},
        {"text": "192.168.1.100:8080", "pattern": "IP_ADDRESS", "line_idx": 2},
        {"text": "user@example.com", "pattern": "EMAIL", "line_idx": 3},
        {"text": "a1b2c3d4e5f6789", "pattern": "GIT_COMMIT", "line_idx": 4},
        {"text": "/home/user/document.txt", "pattern": "FILE_PATH", "line_idx": 6},
        {"text": "550e8400-e29b-41d4-a716-446655440000", "pattern": "UUID", "line_idx": 7},
        {"text": "sha256:abcdef123456789abcdef123456789abcdef123456789abcdef123456789abcdef", "pattern": "DOCKER_SHA", "line_idx": 8},
        {"text": "2001:0db8:85a3:0000:0000:8a2e:0370:7334", "pattern": "IPV6", "line_idx": 9},
        {"text": "0xdeadbeef", "pattern": "HEX_ADDRESS", "line_idx": 10},
        {"text": "123456789", "pattern": "LARGE_NUMBER", "line_idx": 11},
        {"text": "#ff0000", "pattern": "HEX_COLOR", "line_idx": 12},
        {"text": "https://example.com", "pattern": "MARKDOWN_URL", "line_idx": 13},
        {"text": "diff --git a/file.txt b/file.txt", "pattern": "DIFF_SUMMARY", "line_idx": 14},
        {"text": "--- a/old_file.txt", "pattern": "DIFF_A", "line_idx": 15},
        {"text": "+++ b/new_file.txt", "pattern": "DIFF_B", "line_idx": 16},
        {"text": "00:11:22:33:44:55", "pattern": "MAC_ADDRESS", "line_idx": 17},
        {"text": "QmYwAPJzv5CZsnAzt8auVNDE7yFbZcyZLfbqUJnRDvfYKL", "pattern": "IPFS_HASH", "line_idx": 18},
    ]