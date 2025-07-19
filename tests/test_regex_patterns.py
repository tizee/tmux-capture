"""Test regex patterns matching functionality."""

import pytest
import re
from . import conftest
tmux_capture = conftest.tmux_capture


class TestRegexPatterns:
    """Test all regex patterns for accuracy and coverage."""
    
    def test_git_commit_pattern(self):
        """Test git commit hash pattern matching."""
        pattern = tmux_capture.REGEX_PATTERNS["GIT_COMMIT"]
        
        # Valid git commits
        assert re.search(pattern, "commit a1b2c3d") is not None
        assert re.search(pattern, "a1b2c3d4e5f6789") is not None
        assert re.search(pattern, "abc123def456789012345678901234567890abcd") is not None
        
        # Invalid commits
        assert re.search(pattern, "abc123") is None  # Too short
        assert re.search(pattern, "g1b2c3d4e5f6789") is None  # Contains 'g'
        assert re.search(pattern, "123456") is None  # Too short
    
    def test_url_pattern(self):
        """Test URL pattern matching."""
        pattern = tmux_capture.REGEX_PATTERNS["URL"]
        
        # Valid URLs
        assert re.search(pattern, "https://example.com") is not None
        assert re.search(pattern, "http://test.org/path") is not None
        assert re.search(pattern, "git@github.com:user/repo.git") is not None
        assert re.search(pattern, "ssh://user@server.com/path") is not None
        assert re.search(pattern, "ftp://ftp.example.com/file") is not None
        assert re.search(pattern, "file:///home/user/file") is not None
        
        # Invalid URLs
        assert re.search(pattern, "not-a-url") is None
        assert re.search(pattern, "mailto:user@example.com") is None
    
    def test_email_pattern(self):
        """Test email pattern matching."""
        pattern = tmux_capture.REGEX_PATTERNS["EMAIL"]
        
        # Valid emails
        assert re.search(pattern, "user@example.com") is not None
        assert re.search(pattern, "test.user+tag@domain.co.uk") is not None
        assert re.search(pattern, "user123@test-domain.org") is not None
        
        # Invalid emails
        assert re.search(pattern, "invalid.email") is None
        assert re.search(pattern, "@example.com") is None
        assert re.search(pattern, "user@") is None
    
    def test_ip_address_pattern(self):
        """Test IP address pattern matching."""
        pattern = tmux_capture.REGEX_PATTERNS["IP_ADDRESS"]
        
        # Valid IP addresses (simple pattern matches IP format)
        assert re.search(pattern, "192.168.1.1") is not None
        assert re.search(pattern, "10.0.0.1") is not None
        assert re.search(pattern, "255.255.255.255") is not None
        assert re.search(pattern, "127.0.0.1") is not None
        assert re.search(pattern, "999.999.999.999") is not None  # Pattern doesn't validate ranges
        
        # Valid IP addresses with ports
        assert re.search(pattern, "192.168.1.1:8080") is not None
        assert re.search(pattern, "10.0.0.1:3000") is not None
        assert re.search(pattern, "127.0.0.1:80") is not None
        
        # Invalid IP addresses (pattern won't match these)
        assert re.search(pattern, "192.168.1") is None
        assert re.search(pattern, "192.168") is None
        
        # This will match the first valid IP part in "192.168.1.1.1"
        assert re.search(pattern, "192.168.1.1.1") is not None
    
    def test_ipv6_pattern(self):
        """Test IPv6 address pattern matching."""
        pattern = tmux_capture.REGEX_PATTERNS["IPV6"]
        
        # Valid IPv6 addresses
        assert re.search(pattern, "2001:0db8:85a3:0000:0000:8a2e:0370:7334") is not None
        assert re.search(pattern, "2001:db8:85a3::8a2e:370:7334") is not None
        assert re.search(pattern, "::1") is not None
        assert re.search(pattern, "fe80::1%lo0") is not None
        
        # Invalid IPv6 addresses
        assert re.search(pattern, "192.168.1.1") is None
        # This will match "::an" which is a valid IPv6 pattern
        assert re.search(pattern, "not::an::ipv6") is not None
    
    def test_mac_address_pattern(self):
        """Test MAC address pattern matching."""
        pattern = tmux_capture.REGEX_PATTERNS["MAC_ADDRESS"]
        
        # Valid MAC addresses
        assert re.search(pattern, "00:11:22:33:44:55") is not None
        assert re.search(pattern, "aa-bb-cc-dd-ee-ff") is not None
        assert re.search(pattern, "AA:BB:CC:DD:EE:FF") is not None
        
        # Invalid MAC addresses
        assert re.search(pattern, "00:11:22:33:44") is None  # Too short
        assert re.search(pattern, "gg:11:22:33:44:55") is None  # Invalid hex
        # This will match the first valid MAC part "00:11:22:33:44:55"
        assert re.search(pattern, "00:11:22:33:44:55:66") is not None
    
    def test_uuid_pattern(self):
        """Test UUID pattern matching."""
        pattern = tmux_capture.REGEX_PATTERNS["UUID"]
        
        # Valid UUIDs
        assert re.search(pattern, "550e8400-e29b-41d4-a716-446655440000") is not None
        assert re.search(pattern, "6ba7b810-9dad-11d1-80b4-00c04fd430c8") is not None
        assert re.search(pattern, "00000000-0000-0000-0000-000000000000") is not None
        
        # Invalid UUIDs
        assert re.search(pattern, "550e8400-e29b-41d4-a716") is None  # Too short
        # This will match the valid UUID part "550e8400-e29b-41d4-a716-446655440000"
        assert re.search(pattern, "550e8400-e29b-41d4-a716-446655440000-extra") is not None
        assert re.search(pattern, "550e8400-e29b-41d4-a716-44665544000g") is None  # Invalid hex
    
    def test_hex_color_pattern(self):
        """Test hex color pattern matching."""
        pattern = tmux_capture.REGEX_PATTERNS["HEX_COLOR"]
        
        # Valid hex colors
        assert re.search(pattern, "#ff0000") is not None
        assert re.search(pattern, "#00FF00") is not None
        assert re.search(pattern, "#123abc") is not None
        
        # Invalid hex colors
        assert re.search(pattern, "#ff00") is None  # Too short
        assert re.search(pattern, "#ff0000aa") is None  # Too long
        assert re.search(pattern, "#gggggg") is None  # Invalid hex
        assert re.search(pattern, "ff0000") is None  # Missing #
    
    def test_file_path_pattern(self):
        """Test file path pattern matching."""
        pattern = tmux_capture.REGEX_PATTERNS["FILE_PATH"]
        
        # Valid file paths without spaces
        assert re.search(pattern, "/home/user/document.txt") is not None
        assert re.search(pattern, "./relative/path/file.py") is not None
        assert re.search(pattern, "~/Documents/file.pdf") is not None
        assert re.search(pattern, "/usr/local/bin/command") is not None
        assert re.search(pattern, "src/main.rs") is not None
        
        # Valid file paths with spaces
        assert re.search(pattern, "/home/user/My Documents/file.txt") is not None
        assert re.search(pattern, "./path with spaces/file.py") is not None
        assert re.search(pattern, "~/Desktop/Project Files/readme.md") is not None
        assert re.search(pattern, "/Applications/My App.app/Contents/Resources") is not None
        assert re.search(pattern, "src/test files/main.rs") is not None
        
        # Valid paths with multiple consecutive spaces
        assert re.search(pattern, "/path/with  multiple/spaces") is not None
        assert re.search(pattern, "./test   spaces/file.txt") is not None
        
        # Valid paths with spaces at various positions
        assert re.search(pattern, "/path/ space at start/file") is not None
        assert re.search(pattern, "/path/space at end /file") is not None
        assert re.search(pattern, "/path/ both ends /file") is not None
        
        # Complex real-world scenarios
        assert re.search(pattern, "/Users/john/Library/Application Support/MyApp/config.json") is not None
        assert re.search(pattern, "C:/Program Files (x86)/Software/app.exe") is not None
        assert re.search(pattern, "./My Project/src/utils/helper functions.py") is not None
        
        # Edge cases with special characters and spaces
        assert re.search(pattern, "/path/file with @symbol and spaces.txt") is not None
        assert re.search(pattern, "~/test-folder/file with $var and spaces") is not None
        assert re.search(pattern, "./folder[test]/file with [brackets] and spaces.log") is not None
        
        # Invalid file paths
        assert re.search(pattern, "just-a-filename") is None
        assert re.search(pattern, "no-slash-here") is None
    
    def test_docker_sha_pattern(self):
        """Test Docker SHA256 pattern matching."""
        pattern = tmux_capture.REGEX_PATTERNS["DOCKER_SHA"]
        
        # Valid Docker SHA
        valid_sha = "sha256:abcdef123456789abcdef123456789abcdef123456789abcdef123456789abcdef"
        assert re.search(pattern, valid_sha) is not None
        
        # Invalid Docker SHA
        assert re.search(pattern, "sha256:abc123") is None  # Too short
        assert re.search(pattern, "md5:abcdef123456789") is None  # Wrong algorithm
        assert re.search(pattern, "abcdef123456789") is None  # Missing prefix
    
    def test_hex_address_pattern(self):
        """Test hexadecimal memory address pattern matching."""
        pattern = tmux_capture.REGEX_PATTERNS["HEX_ADDRESS"]
        
        # Valid hex addresses
        assert re.search(pattern, "0xdeadbeef") is not None
        assert re.search(pattern, "0x12345678") is not None
        assert re.search(pattern, "0xABCDEF") is not None
        
        # Invalid hex addresses
        assert re.search(pattern, "0xgggg") is None  # Invalid hex
        assert re.search(pattern, "deadbeef") is None  # Missing 0x
        assert re.search(pattern, "0x") is None  # No digits
    
    def test_large_number_pattern(self):
        """Test large number pattern matching."""
        pattern = tmux_capture.REGEX_PATTERNS["LARGE_NUMBER"]
        
        # Valid large numbers
        assert re.search(pattern, "123456789") is not None
        assert re.search(pattern, "1234") is not None
        assert re.search(pattern, "999999999999") is not None
        
        # Invalid large numbers
        assert re.search(pattern, "123") is None  # Too short
        assert re.search(pattern, "12a34") is None  # Contains letters
    
    def test_markdown_url_pattern(self):
        """Test markdown URL pattern matching."""
        pattern = tmux_capture.REGEX_PATTERNS["MARKDOWN_URL"]
        
        # Valid markdown URLs
        assert re.search(pattern, "[Link](https://example.com)") is not None
        assert re.search(pattern, "[Text](./relative/path)") is not None
        assert re.search(pattern, "[Text](x)") is not None  # At least one character required
        
        # Invalid markdown URLs
        assert re.search(pattern, "[Empty]()") is None  # Empty URL not matched by [^)]+ 
        assert re.search(pattern, "[No closing paren](https://example.com") is None
        assert re.search(pattern, "No brackets(https://example.com)") is None
    
    def test_diff_patterns(self):
        """Test git diff patterns matching."""
        diff_summary = tmux_capture.REGEX_PATTERNS["DIFF_SUMMARY"]
        diff_a = tmux_capture.REGEX_PATTERNS["DIFF_A"]
        diff_b = tmux_capture.REGEX_PATTERNS["DIFF_B"]
        
        # Valid diff patterns
        assert re.search(diff_summary, "diff --git a/file.txt b/file.txt") is not None
        assert re.search(diff_a, "--- a/old_file.txt") is not None
        assert re.search(diff_b, "+++ b/new_file.txt") is not None
        
        # Invalid diff patterns
        assert re.search(diff_summary, "diff --git file.txt") is None
        assert re.search(diff_a, "--- old_file.txt") is None
        assert re.search(diff_b, "+++ new_file.txt") is None
    
    def test_ipfs_hash_pattern(self):
        """Test IPFS hash pattern matching."""
        pattern = tmux_capture.REGEX_PATTERNS["IPFS_HASH"]
        
        # Valid IPFS hashes
        assert re.search(pattern, "QmYwAPJzv5CZsnAzt8auVNDE7yFbZcyZLfbqUJnRDvfYKL") is not None
        assert re.search(pattern, "QmT78zSuBmuS2z925AEH9pSq8mBzfCUfpEqKTcEejqkfKe") is not None
        
        # Invalid IPFS hashes
        assert re.search(pattern, "QmTooShort") is None  # Too short
        assert re.search(pattern, "NotQmHash") is None  # Doesn't start with Qm
        assert re.search(pattern, "QmYwAPJzv5CZsnAzt8auVNDE7yFbZcyZLfbqUJnRDvfYKL123") is None  # Too long
    
    def test_github_repo_pattern(self):
        """Test GitHub repository pattern matching."""
        pattern = tmux_capture.REGEX_PATTERNS["GITHUB_REPO"]
        
        # Valid GitHub repos
        assert re.search(pattern, "https://github.com/user/repo") is not None
        assert re.search(pattern, "git@github.com:user/repo.git") is not None
        assert re.search(pattern, "ssh@github.com:user/repo") is not None
        assert re.search(pattern, "https://github.com/user/repo.git") is not None
        
        # Invalid GitHub repos
        assert re.search(pattern, "https://gitlab.com/user/repo") is None
        assert re.search(pattern, "github.com/user/repo") is None  # Missing protocol