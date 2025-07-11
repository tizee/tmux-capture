# shell-capture

A minimal terminal wrapper that provides tmux-capture functionality via global hotkeys. Built as a single-file `uv` script with complete terminal emulation and vim compatibility.

## Features

- **Transparent Shell Proxy**: Run any shell command in a transparent wrapper with full terminal emulation
- **Global Hotkey**: Press `Ctrl+E` to enter capture mode with hint overlays
- **Advanced Pattern Matching**: Automatically finds URLs, git commits, emails, file paths, and more
- **Interactive Selection**: Use vim-style hints to select text with progressive typing
- **True Color Support**: Full 24-bit color rendering with Gruvbox theme
- **Vim Compatibility**: Enhanced vim support with alternative screen buffer handling
- **Cross-platform Clipboard**: Automatic clipboard copying (macOS/Linux)
- **Zero Configuration**: Works out of the box with automatic dependency management
- **Complete Terminal Emulation**: Uses `pyte` library for full VT100+ compatibility

## Usage

```bash
# Start with default shell (uv automatically installs dependencies)
./shell-capture

# Start with specific shell
./shell-capture bash
./shell-capture zsh
./shell-capture fish

# Run complex commands
./shell-capture "ssh user@host"
./shell-capture tmux
./shell-capture vim
./shell-capture "python -m http.server"
./shell-capture "top -i1"

# Works with any terminal application
./shell-capture htop
./shell-capture "git log --oneline --graph"
```

## How It Works

1. **Start the wrapper**: `./shell-capture`
2. **Use normally**: The wrapper is transparent, use your shell as usual
3. **Capture text**: Press `Ctrl+E` to enter capture mode
4. **Select with hints**: Type the hint letters to select text
5. **Auto-copy**: Selected text is automatically copied to clipboard
6. **Return to shell**: Automatically returns to normal mode

## Requirements

- Python 3.10+
- `uv` package manager (for automatic dependency installation)
- Dependencies (automatically installed):
  - `blessed >= 1.21.0` - Terminal control and rendering
  - `ptyprocess >= 0.7.0` - PTY process management
  - `pyte >= 0.8.1` - Terminal emulation engine
- Clipboard utilities:
  - macOS: `pbcopy` (built-in)
  - Linux: `xclip` or `xsel`

## Architecture

Shell-capture creates a comprehensive terminal emulation wrapper around your shell command using modern Python libraries:

1. **PTY Management**: Uses `ptyprocess` to spawn and control shell processes
2. **Terminal Emulation**: Employs `pyte` library for complete VT100+ terminal emulation
3. **Real-time Rendering**: Uses `blessed` for cross-platform terminal control and true color support
4. **I/O Multiplexing**: Select-based non-blocking I/O for transparent forwarding
5. **Screen Buffer**: Maintains complete 2D screen state with history scrollback
6. **Pattern Recognition**: Integrates tmux-capture's mature pattern matching engine
7. **Alternative Screen Support**: Full vim/tmux compatibility with screen buffer switching

## Compared to tmux-capture

- **Independence**: No tmux dependency - works standalone
- **Universality**: Works with any shell/terminal combination
- **Enhanced Compatibility**: Full vim support with Enter key handling and alt-screen
- **True Color**: 24-bit color support with Gruvbox theming
- **Terminal Emulation**: Complete terminal emulation vs tmux pane scraping
- **Single File**: Zero-installation `uv` script with automatic dependencies
- **Transparency**: Invisible when not capturing, complete passthrough
- **Debugging**: Comprehensive logging system for troubleshooting

## Technical Highlights

### Terminal Emulation
- **Complete VT100+ Support**: Full ANSI escape sequence processing
- **Character Attributes**: Maintains color, style, and formatting per character
- **Screen Management**: 2D buffer with cursor positioning and scrollback
- **Alternative Screens**: Proper vim/tmux alternative screen buffer handling

### Vim Compatibility
- **Enter Key Handling**: Automatic LF to CR conversion for vim mode
- **Alternative Screen**: Save/restore main screen when entering vim
- **Signal Handling**: Proper SIGWINCH forwarding for terminal resize
- **Terminal Attributes**: Comprehensive termios configuration

### Performance
- **Dirty Line Tracking**: Only renders changed screen regions
- **Select-based I/O**: Non-blocking multiplexed input/output
- **Memory Efficient**: Automatic cleanup and history management
- **Color Optimization**: Efficient RGB color handling

### Development Features
- **Debug Logging**: Detailed debug.log for troubleshooting
- **Monkey Patching**: Fixes for pyte/vim compatibility issues
- **Comprehensive Error Handling**: Graceful degradation on failures
- **Signal Management**: Proper cleanup and terminal restoration

## Production Ready

Built on the mature tmux-capture codebase and enhanced with robust terminal emulation. Features comprehensive vim compatibility testing and detailed logging for production deployment.
