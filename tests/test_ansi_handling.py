"""Test ANSI escape sequence handling and visual position calculations."""

import pytest
from unittest.mock import Mock
from . import conftest
tmux_capture = conftest.tmux_capture


class TestAnsiHandling:
    """Test ANSI escape sequence processing and visual position mapping."""
    
    def test_hex_to_rgb_valid_colors(self):
        """Test hex to RGB conversion with valid colors."""
        # Test basic colors
        assert tmux_capture.hex_to_rgb("#ff0000") == (255, 0, 0)
        assert tmux_capture.hex_to_rgb("#00ff00") == (0, 255, 0)
        assert tmux_capture.hex_to_rgb("#0000ff") == (0, 0, 255)
        assert tmux_capture.hex_to_rgb("#ffffff") == (255, 255, 255)
        assert tmux_capture.hex_to_rgb("#000000") == (0, 0, 0)
        
        # Test with different cases
        assert tmux_capture.hex_to_rgb("#FF0000") == (255, 0, 0)
        assert tmux_capture.hex_to_rgb("#AbCdEf") == (171, 205, 239)
        
        # Test without # prefix
        assert tmux_capture.hex_to_rgb("ff0000") == (255, 0, 0)
    
    def test_hex_to_rgb_invalid_colors(self):
        """Test hex to RGB conversion with invalid colors."""
        with pytest.raises(ValueError):
            tmux_capture.hex_to_rgb("#ff00")  # Too short
        
        with pytest.raises(ValueError):
            tmux_capture.hex_to_rgb("#ff0000aa")  # Too long
        
        with pytest.raises(ValueError):
            tmux_capture.hex_to_rgb("#gggggg")  # Invalid hex characters
    
    def test_calculate_visual_positions_no_ansi(self):
        """Test visual position calculation with no ANSI sequences."""
        term = Mock()
        term.length = Mock(side_effect=len)
        
        line = "Hello World"
        positions = tmux_capture.calculate_visual_positions(line, term)
        
        # Should have straightforward 1:1 mapping
        expected = {i: i for i in range(len(line))}
        assert positions == expected
    
    def test_calculate_visual_positions_with_ansi(self):
        """Test visual position calculation with ANSI sequences."""
        term = Mock()
        term.length = Mock(side_effect=len)
        
        # Line with ANSI color codes
        line = "\x1b[31mRed\x1b[0m Text"
        positions = tmux_capture.calculate_visual_positions(line, term)
        
        # Visual positions should skip ANSI sequences
        # \x1b[31m is 5 characters but takes 0 visual space
        # \x1b[0m is 4 characters but takes 0 visual space
        expected = {
            0: 5,   # 'R' is at character index 5
            1: 6,   # 'e' is at character index 6
            2: 7,   # 'd' is at character index 7
            3: 12,  # ' ' is at character index 12 (after \x1b[0m)
            4: 13,  # 'T' is at character index 13
            5: 14,  # 'e' is at character index 14
            6: 15,  # 'x' is at character index 15
            7: 16,  # 't' is at character index 16
        }
        assert positions == expected
    
    def test_calculate_visual_positions_multiple_ansi(self):
        """Test visual position calculation with multiple ANSI sequences."""
        term = Mock()
        term.length = Mock(side_effect=len)
        
        # Line with multiple ANSI codes
        line = "\x1b[31mRed\x1b[0m \x1b[32mGreen\x1b[0m"
        positions = tmux_capture.calculate_visual_positions(line, term)
        
        # Should correctly map visual positions
        expected = {
            0: 5,   # 'R'
            1: 6,   # 'e'
            2: 7,   # 'd'
            3: 12,  # ' '
            4: 18,  # 'G'
            5: 19,  # 'r'
            6: 20,  # 'e'
            7: 21,  # 'e'
            8: 22,  # 'n'
        }
        assert positions == expected
    
    def test_calculate_visual_positions_empty_line(self):
        """Test visual position calculation with empty line."""
        term = Mock()
        term.length = Mock(side_effect=len)
        
        line = ""
        positions = tmux_capture.calculate_visual_positions(line, term)
        
        assert positions == {}
    
    def test_calculate_visual_positions_only_ansi(self):
        """Test visual position calculation with only ANSI sequences."""
        term = Mock()
        term.length = Mock(side_effect=len)
        
        line = "\x1b[31m\x1b[0m"
        positions = tmux_capture.calculate_visual_positions(line, term)
        
        assert positions == {}
    
    def test_calculate_visual_positions_complex_ansi(self):
        """Test visual position calculation with complex ANSI sequences."""
        term = Mock()
        term.length = Mock(side_effect=len)
        
        # Line with bold, color, and reset sequences
        line = "\x1b[1m\x1b[31mBold Red\x1b[0m Normal"
        positions = tmux_capture.calculate_visual_positions(line, term)
        
        # Should correctly handle multiple sequences
        expected = {
            0: 9,   # 'B' - after \x1b[1m\x1b[31m
            1: 10,  # 'o'
            2: 11,  # 'l'
            3: 12,  # 'd'
            4: 13,  # ' '
            5: 14,  # 'R'
            6: 15,  # 'e'
            7: 16,  # 'd'
            8: 21,  # ' ' - after \x1b[0m
            9: 22,  # 'N'
            10: 23, # 'o'
            11: 24, # 'r'
            12: 25, # 'm'
            13: 26, # 'a'
            14: 27, # 'l'
        }
        assert positions == expected
    
    def test_calculate_visual_positions_malformed_ansi(self):
        """Test visual position calculation with malformed ANSI sequences."""
        term = Mock()
        term.length = Mock(side_effect=len)
        
        # Line with incomplete ANSI sequence
        line = "\x1b[31Text"
        positions = tmux_capture.calculate_visual_positions(line, term)
        
        # Should treat incomplete sequence as regular characters
        expected = {i: i for i in range(len(line))}
        assert positions == expected
    
    def test_find_text_matches_with_ansi(self, mock_terminal):
        """Test find_text_matches function with ANSI sequences."""
        lines_with_ansi = [
            "Normal text",
            "\x1b[31mRed https://example.com\x1b[0m",
            "IP: \x1b[32m192.168.1.1\x1b[0m",
        ]
        
        patterns = {"URL": r"https://[^\s]+", "IP_ADDRESS": r"\d+\.\d+\.\d+\.\d+"}
        
        matches = tmux_capture.find_text_matches(lines_with_ansi, patterns, mock_terminal)
        
        # Should find matches despite ANSI sequences
        assert len(matches) == 2
        
        # Check URL match
        url_match = next(m for m in matches if m["pattern"] == "URL")
        assert url_match["text"] == "https://example.com"
        assert url_match["line_idx"] == 1
        
        # Check IP match
        ip_match = next(m for m in matches if m["pattern"] == "IP_ADDRESS")
        assert ip_match["text"] == "192.168.1.1"
        assert ip_match["line_idx"] == 2
    
    def test_find_text_matches_preserves_ansi_styling(self, mock_terminal):
        """Test that find_text_matches preserves original ANSI styling."""
        lines_with_ansi = [
            "\x1b[31mhttps://example.com\x1b[0m",
        ]
        
        patterns = {"URL": r"https://[^\s]+"}
        
        matches = tmux_capture.find_text_matches(lines_with_ansi, patterns, mock_terminal)
        
        assert len(matches) == 1
        match = matches[0]
        
        # Should preserve original styled segment (from match start)
        assert match["original_styled_segment"] == "https://example.com\x1b[0m"
        assert match["text"] == "https://example.com"
    
    def test_find_text_matches_position_mapping(self, mock_terminal):
        """Test that find_text_matches correctly maps positions with ANSI."""
        # Mock the visual position calculation
        def mock_calculate_positions(line, term):
            if line == "\x1b[31mURL: https://example.com\x1b[0m":
                # Simulate position mapping: "URL: https://example.com"
                return {
                    0: 5,   # 'U'
                    1: 6,   # 'R'
                    2: 7,   # 'L'
                    3: 8,   # ':'
                    4: 9,   # ' '
                    5: 10,  # 'h' (start of URL)
                    6: 11,  # 't'
                    7: 12,  # 't'
                    8: 13,  # 'p'
                    9: 14,  # 's'
                    10: 15, # ':'
                    11: 16, # '/'
                    12: 17, # '/'
                    13: 18, # 'e'
                    14: 19, # 'x'
                    15: 20, # 'a'
                    16: 21, # 'm'
                    17: 22, # 'p'
                    18: 23, # 'l'
                    19: 24, # 'e'
                    20: 25, # '.'
                    21: 26, # 'c'
                    22: 27, # 'o'
                    23: 28, # 'm'
                    24: 33, # End position after \x1b[0m
                }
            return {}
        
        # Replace the function temporarily
        original_func = tmux_capture.calculate_visual_positions
        tmux_capture.calculate_visual_positions = mock_calculate_positions
        
        try:
            lines_with_ansi = ["\x1b[31mURL: https://example.com\x1b[0m"]
            patterns = {"URL": r"https://[^\s]+"}
            
            matches = tmux_capture.find_text_matches(lines_with_ansi, patterns, mock_terminal)
            
            assert len(matches) == 1
            match = matches[0]
            
            # Should map visual positions to character indices
            assert match["text"] == "https://example.com"
            assert match["start_col"] == 5  # Visual position of 'h'
            assert match["end_col"] == 24   # Visual position after 'm'
            
        finally:
            # Restore original function
            tmux_capture.calculate_visual_positions = original_func
    
    def test_find_text_matches_no_matches(self, mock_terminal):
        """Test find_text_matches with no pattern matches."""
        lines_with_ansi = [
            "No matches here",
            "\x1b[31mStill no matches\x1b[0m",
        ]
        
        patterns = {"URL": r"https://[^\s]+"}
        
        matches = tmux_capture.find_text_matches(lines_with_ansi, patterns, mock_terminal)
        
        assert matches == []
    
    def test_find_text_matches_multiple_patterns(self, mock_terminal):
        """Test find_text_matches with multiple patterns."""
        lines_with_ansi = [
            "Visit https://example.com",
            "Email: user@example.com",
            "IP: 192.168.1.1",
        ]
        
        patterns = {
            "URL": r"https://[^\s]+",
            "EMAIL": r"[^\s]+@[^\s]+",
            "IP": r"\d+\.\d+\.\d+\.\d+"
        }
        
        matches = tmux_capture.find_text_matches(lines_with_ansi, patterns, mock_terminal)
        
        assert len(matches) == 3
        
        # Check all patterns were found
        patterns_found = {match["pattern"] for match in matches}
        assert patterns_found == {"URL", "EMAIL", "IP"}
    
    def test_find_text_matches_overlapping_patterns(self, mock_terminal):
        """Test find_text_matches with overlapping pattern matches."""
        lines_with_ansi = [
            "Contact: user@github.com or https://github.com/user",
        ]
        
        patterns = {
            "EMAIL": r"[^\s]+@[^\s]+",
            "URL": r"https://[^\s]+",
            "GITHUB": r"github\.com[^\s]*"
        }
        
        matches = tmux_capture.find_text_matches(lines_with_ansi, patterns, mock_terminal)
        
        # Should find all overlapping matches
        assert len(matches) >= 3
        
        # Check that we get the expected matches
        texts = [match["text"] for match in matches]
        assert "user@github.com" in texts
        assert "https://github.com/user" in texts
        assert any("github.com" in text for text in texts)