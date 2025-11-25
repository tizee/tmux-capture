# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.6] - 2025-11-24

### Added
- **tmux-capture**: Broaden FILE_PATH regex pattern to handle escaped spaces in file paths
- Comprehensive test coverage updates and documentation improvements

## [0.1.5] - 2025-08-03

### Fixed
- **regex**: Supercharged FILE_PATH pattern to properly handle spaces and special characters in file paths

## [0.1.4] - 2025-07-19

### Added
- **logging**: DEBUG environment variable support for enhanced debugging capabilities
- **scripts**: ANSI sequence tester script for terminal rendering validation
- **ui**: Vim-style status bar with enhanced color system
- **signals**: Enhanced signal handling for ZLE (Zsh Line Editor) compatibility
- **shell-capture**: Improved terminal rendering and cleanup in render-test.sh
- **ui**: Flash message system with success/error styling
- **vim-compatibility**: Major terminal emulation upgrades for vim support
- Shell-capture script with TUI wrapper and hint-based selection
- Project scaffolding and documentation for shell-capture feature

### Fixed
- **regex**: Handle file paths containing spaces and special characters

### Performance
- **renderer**: Turbocharged terminal rendering with multiple optimizations for better performance

### Documentation
- Major README overhaul with proof-of-concept warnings and performance data

## [0.1.3] - 2025-07-11

### Added
- Advanced pattern overlap resolution algorithm

## [0.1.2] - 2025-07-11

### Added
- **terminal**: Ninja-level terminal control capabilities similar to nvim

### Changed
- **build**: Major project restructuring and cleanup for better maintainability

### Fixed
- Improved error handling and edge case management

### Documentation
- Updated Python version badge in README from 3.6+ to 3.11+

### Tests
- Comprehensive test suite for exception handling and execution flows

## [0.1.1] - 2025-07-10

### Fixed
- **ui**: Small terminal support and edge case handling improvements

## [0.1.0] - 2025-07-10

### Added
- **tmux-capture**: Initial release with window capture functionality
- **hint-generation**: Optimal prefix-free hint generation algorithm with mathematical foundation
- Comprehensive UI test suite

### Documentation
- README with demo showcase and project badges
- Initial project documentation and setup guide

---

[0.1.6]: https://github.com/tizee/tmux-capture/compare/v0.1.5...v0.1.6
[0.1.5]: https://github.com/tizee/tmux-capture/compare/v0.1.4...v0.1.5
[0.1.4]: https://github.com/tizee/tmux-capture/compare/v0.1.3...v0.1.4
[0.1.3]: https://github.com/tizee/tmux-capture/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/tizee/tmux-capture/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/tizee/tmux-capture/compare/0.1.0...v0.1.1
[0.1.0]: https://github.com/tizee/tmux-capture/releases/tag/0.1.0
