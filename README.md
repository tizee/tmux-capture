# tmux-capture

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Dependency manager: uv](https://img.shields.io/badge/dependency%20manager-uv-blue.svg)](https://github.com/astral-sh/uv)
[![tmux](https://img.shields.io/badge/tmux-compatible-green.svg)](https://github.com/tmux/tmux)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux-lightgrey.svg)](https://github.com/tizee/tmux-capture)

A modern Python-based text selection tool for tmux, inspired by tmux-thumbs but designed for better usability and maintenance.

<video src="https://github.com/user-attachments/assets/a1b7d9fb-36c5-494d-8dca-8cc84d8e2196" controls width="100%"></video>

## Motivation

While [tmux-thumbs](https://github.com/fcsonline/tmux-thumbs) pioneered the concept of hint-based text selection in tmux, it has several limitations:
- Requires external Rust compilation and installation
- Complex setup process
- Hasn't been actively maintained
- Limited customization options

tmux-capture solves these issues by:
- Using Python with minimal dependencies (just `blessed`)
- Self-contained script with dependency management via `uv`
- Simple installation and configuration

## Features

- **Pattern Detection**: Automatically finds URLs, git commits, email addresses, and GitHub repositories
- **Optimal Keyboard Hints**: Advanced hint generation using greedy algorithm with optimal substructure
- **Cross-platform**: Works on macOS and Linux
- **Gruvbox Theme**: Beautiful color scheme for better visibility
- **ANSI Support**: Preserves terminal colors and formatting
- **Clipboard Integration**: Automatic copying to system clipboard

## Installation

1. Clone or download this repository
2. Install uv if not already installed:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
3. Run the installation script:
   ```bash
   ./install.sh
   ```
4. Reload tmux configuration:
   ```bash
   tmux source-file ~/.tmux.conf
   ```

## CLI Integration

### Add to PATH (Optional)

For convenient CLI usage, add tmux-capture to your PATH:

```bash
# Add to ~/.zshrc or ~/.bashrc
export PATH="/path/to/tmux-capture:$PATH"
alias tc='tmux-capture'
```

### Zsh Plugin (Optional)

For zsh users, enable command-line hotkey support:

```bash
# Add to ~/.zshrc
source "/path/to/tmux-capture/tmux-capture.plugin.zsh"
```

This provides:
- **Ctrl+E** - Launch tmux-capture from command line (configurable)
- **tmux-capture-help** - Show plugin help

### Customize Hotkey

The default hotkey is `Ctrl+E`, but you can customize it:

```bash
# Set custom hotkey before sourcing the plugin
export TMUX_CAPTURE_HOTKEY='^O'  # Ctrl+O
source "/path/to/tmux-capture/tmux-capture.plugin.zsh"
```

Common hotkey formats:
- `^E` - Ctrl+E
- `^O` - Ctrl+O
- `^X^E` - Ctrl+X, Ctrl+E
- `\e[` - Alt+key combinations

## Usage

### In tmux (Recommended)

1. In any tmux pane, press `Prefix + y` (default tmux prefix is `Ctrl-b`)
2. A new window opens showing the original pane content with highlighted matches
3. Type the hint characters (a, b, c, etc.) to select text
4. Selected text is automatically copied to clipboard
5. Press any key to close the selection window

### As CLI tool

The tool can also be used as a standalone CLI application:

```bash
# Capture content from current tmux pane
./tmux-capture

# Capture content from specific tmux pane
./tmux-capture %1

# Using uv (recommended)
uv run tmux-capture

# Works outside tmux too - will show error if no tmux session
python3 tmux-capture
```

**Note**: While the tool can run outside tmux, it's designed for tmux environments and requires a tmux session to capture pane content.

## Key Bindings

Default binding: `Prefix + y`

To customize, edit your `~/.tmux.conf`:
```bash
# Use different key combination
bind-key C-y run-shell '/path/to/tmux-capture-window.sh'  # Prefix + Ctrl+y
bind-key -n M-y run-shell '/path/to/tmux-capture-window.sh'  # Alt+y (no prefix)
```

## Pattern Recognition

tmux-capture automatically detects and prioritizes 18 different text patterns:

### Supported Patterns
- **URLs**: `https://example.com/path`, `git@github.com:user/repo.git`
- **Git commits**: `a1b2c3d4e5f6789` (7-40 hex characters)
- **Email addresses**: `user@example.com`, `user+tag@domain.co.uk`
- **GitHub repositories**: `https://github.com/user/repo`, `git@github.com:user/repo.git`
- **IP addresses**: `192.168.1.1`, `10.0.0.1:8080` (with optional port)
- **IPv6 addresses**: `2001:db8::1`, `::1`
- **File paths**: `/home/user/file.txt`, `./relative/path`
- **MAC addresses**: `aa:bb:cc:dd:ee:ff`, `AA-BB-CC-DD-EE-FF`
- **UUIDs**: `550e8400-e29b-41d4-a716-446655440000`
- **Hex colors**: `#ff0000`, `#1a2b3c`
- **Docker SHA**: `sha256:abcd1234...` (64 hex characters)
- **Memory addresses**: `0x7fff12345678`
- **IPFS hashes**: `QmX1eWnvmPiYT...` (44 characters)
- **Large numbers**: `12345` (4+ digits)
- **Markdown links**: `[text](url)` (extracts URL)
- **Git diff files**: `diff --git a/file b/file`, `--- a/file`, `+++ b/file`

## Overlap Resolution Algorithm

When multiple patterns match the same text region, tmux-capture uses an intelligent overlap resolution algorithm to ensure only the most relevant match is displayed and copied.

### Priority Rules

The algorithm applies the following rules in order:

1. **Length Priority**: Longer matches are preferred over shorter ones
   ```
   "33030965+user@example.com" → EMAIL (full match) wins over LARGE_NUMBER (partial)
   ```

2. **Pattern Specificity**: More specific patterns win over generic ones
   ```
   Priority levels (1 = highest, 20 = lowest):
   - EMAIL, URL: 1 (highest priority)
   - GITHUB_REPO: 2  
   - GIT_COMMIT: 3
   - UUID: 4
   - IP_ADDRESS, IPV6: 5
   - MAC_ADDRESS: 6
   - HEX_COLOR: 7
   - DOCKER_SHA: 8
   - FILE_PATH: 9
   - MARKDOWN_URL: 10
   - DIFF_*: 11
   - HEX_ADDRESS: 12
   - IPFS_HASH: 13
   - LARGE_NUMBER: 20 (lowest priority - very generic)
   ```

3. **Pattern Declaration Order**: Earlier patterns in the regex dictionary win ties

### Algorithm Behavior

- **Non-overlapping matches** are all preserved
- **Cross-line matches** are handled independently (no interference between lines)
- **Adjacent matches** (touching but not overlapping) are both kept
- **Partial overlaps** are resolved using the priority rules above

### Examples

```text
Input: "Contact user@github.com or visit https://github.com/user"

Without overlap resolution:
- "user@github.com" (EMAIL)
- "github.com" (partial GITHUB pattern)  
- "https://github.com/user" (URL)

With overlap resolution:
- "user@github.com" (EMAIL wins over partial GITHUB)
- "https://github.com/user" (URL, no overlap with EMAIL)
```

This ensures that users see intuitive, non-redundant matches where the highlighted text exactly matches what gets copied to the clipboard.

## Requirements

- **tmux with capture-panel support** (required for pane content capture)
- **Python >= 3.6+**
- **uv** (for dependency management)
- **System clipboard utility**:
  - macOS: `pbcopy` (built-in)
  - Linux: `xclip` or `xsel`

The tool is designed primarily for tmux environments but can be used as a standalone CLI application when a tmux session is available.

## How It Works

1. When triggered, the script captures the current pane ID
2. Creates a new tmux window running the capture tool
3. The tool captures content from the original pane (not the new window)
4. Displays interactive hints overlaid on the captured content
5. User selects text using keyboard hints
6. Selected text is copied to clipboard
7. Window closes after user confirmation

## Supported Keyboard Layouts

tmux-capture supports multiple keyboard layouts, maintaining compatibility with tmux-thumbs configurations to ease migration:

- **vim-movement**: `hjklwbef` (default) - Vim navigation keys
- **vim-homerow**: `hjklasdfg` - Vim keys + homerow
- **qwerty-homerow**: `asdfjklgh` - QWERTY homerow keys
- **dvorak**: `aoeuqjkx...` - Dvorak keyboard layout
- **colemak**: `arstqwfp...` - Colemak keyboard layout
- **numeric**: `1234567890` - Number keys only

These layouts are designed to be familiar to tmux-thumbs users, allowing for seamless migration while providing optimal hint generation using an advanced greedy algorithm.

## License

MIT License - see LICENSE file for details.

## Development

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager

### Setup

```bash
# Clone the repository
git clone https://github.com/user/tmux-capture.git
cd tmux-capture

# Install dependencies
uv sync --group dev
```

### Running Tests

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# Run linting
make lint

# Format code
make format

# Run all checks
make check

# Clean generated files
make clean
```

Or use uv directly:

```bash
# Install dev dependencies
uv sync --group dev

# Run tests
uv run pytest tests

# Run tests with coverage
uv run pytest tests --cov=tmux-capture --cov-report=term-missing --cov-report=html:htmlcov

# Run linting
uv run ruff check .

# Format code
uv run ruff format .
```

### Test Coverage

The project maintains **100% test coverage** with 147 comprehensive tests covering:

- **Regex pattern matching** - Tests for all 18 supported patterns
- **Overlap resolution** - 15 tests covering priority rules, edge cases, and complex scenarios
- **Hint generation** - Tests for optimal algorithm with all keyboard layouts
- **Content grouping** - Tests for reducing hint count with duplicate content
- **ANSI handling** - Tests for terminal escape sequence processing
- **Tmux integration** - Mocked tests for tmux command execution
- **Clipboard operations** - Cross-platform clipboard functionality tests
- **Terminal control** - Tests for TTY detection and /dev/tty fallback logic
- **Edge cases** - Comprehensive coverage of boundary conditions and error scenarios

## Contributing

Issues and pull requests are welcome. This project aims to be a simple, maintainable alternative to tmux-thumbs.
