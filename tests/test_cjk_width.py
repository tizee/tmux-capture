"""Tests for CJK double-width character handling.

These tests verify that:
1. calculate_visual_positions correctly maps CJK chars to 2 display columns
2. find_text_matches produces correct display-width positions for overlay alignment
3. Overlay highlights align with matched text when CJK chars are present
"""

import pytest
from unittest.mock import Mock
from . import conftest

tmux_capture = conftest.tmux_capture


def make_term_mock(width=80, height=24):
    """Create a mock terminal that handles CJK width via wcwidth."""
    import re
    import wcwidth

    term = Mock()
    term.width = width
    term.height = height
    term.clear = ""
    term.normal = ""
    term.bold = ""
    term.dim = ""
    term.move_xy = Mock(return_value="")
    term.on_color_rgb = Mock(return_value="")
    term.color_rgb = Mock(return_value="")

    # strip_seqs removes ANSI escape sequences
    term.strip_seqs = Mock(
        side_effect=lambda x: re.sub(r"\x1b\[[0-9;]*m", "", x)
    )

    # length should return display width using wcwidth
    def mock_length(s):
        return wcwidth.wcswidth(s) if wcwidth.wcswidth(s) >= 0 else len(s)

    term.length = mock_length
    return term


class TestCJKVisualPositions:
    """Test calculate_visual_positions with CJK double-width characters."""

    def test_cjk_char_occupies_two_columns(self):
        """A single CJK character should map to 2 visual columns."""
        term = make_term_mock()
        line = "中"
        positions = tmux_capture.calculate_visual_positions(line, term)
        # '中' is at char index 0, occupies visual columns 0 and 1
        assert positions[0] == 0
        # Next visual position should be 2 (after the double-width char)
        assert 1 not in positions  # column 1 is occupied by the same char

    def test_cjk_then_ascii(self):
        """CJK followed by ASCII: ASCII starts at visual column 2."""
        term = make_term_mock()
        line = "中a"
        positions = tmux_capture.calculate_visual_positions(line, term)
        assert positions[0] == 0  # '中' at char index 0
        assert positions[2] == 1  # 'a' at char index 1, visual column 2

    def test_mixed_cjk_ascii_positions(self):
        """Mixed CJK and ASCII should have correct visual positions."""
        term = make_term_mock()
        # "使用 scripts" -> 使(2) 用(2) space(1) s(1) c(1) r(1) i(1) p(1) t(1) s(1)
        line = "使用 scripts"
        positions = tmux_capture.calculate_visual_positions(line, term)
        # '使' at char 0 -> visual col 0 (width 2)
        assert positions[0] == 0
        # '用' at char 1 -> visual col 2 (width 2)
        assert positions[2] == 1
        # ' ' at char 2 -> visual col 4 (width 1)
        assert positions[4] == 2
        # 's' at char 3 -> visual col 5
        assert positions[5] == 3

    def test_cjk_with_ansi(self):
        """CJK with ANSI escape sequences should still align correctly."""
        term = make_term_mock()
        # \x1b[31m = 5 chars, "中" = 1 char, \x1b[0m = 4 chars, "abc" = 3 chars
        line = "\x1b[31m中\x1b[0mabc"
        positions = tmux_capture.calculate_visual_positions(line, term)
        # '中' at char index 5, visual col 0 (width 2)
        assert positions[0] == 5
        # 'a' at char index 10, visual col 2
        assert positions[2] == 10
        # 'b' at char index 11, visual col 3
        assert positions[3] == 11


class TestCJKMatchPositions:
    """Test that find_text_matches produces display-width positions for matches."""

    def test_match_after_cjk_has_correct_start_col(self):
        """A match after CJK chars should have start_col in display columns."""
        term = make_term_mock()
        # "使用 https://example.com"
        # 使(2) 用(2) space(1) = 5 display columns before URL
        line = "使用 https://example.com"
        patterns = {"URL": r"https://[^\s]+"}
        matches = tmux_capture.find_text_matches([line], patterns, term)
        assert len(matches) == 1
        # URL starts at char index 3, but display column 5
        assert matches[0]["start_col"] == 5

    def test_match_between_cjk_has_correct_positions(self):
        """A match between CJK text should have correct display positions."""
        term = make_term_mock()
        # "看 192.168.1.1 吧"
        # 看(2) space(1) = 3 display columns before IP
        line = "看 192.168.1.1 吧"
        patterns = {"IP_ADDRESS": r"\d+\.\d+\.\d+\.\d+"}
        matches = tmux_capture.find_text_matches([line], patterns, term)
        assert len(matches) == 1
        assert matches[0]["start_col"] == 3
        # "192.168.1.1" is 11 chars wide (all ASCII)
        assert matches[0]["end_col"] == 14

    def test_match_with_ansi_and_cjk(self):
        """Match position should be correct with both ANSI and CJK."""
        term = make_term_mock()
        # ANSI + CJK + match
        line = "\x1b[31m中文\x1b[0m https://example.com"
        patterns = {"URL": r"https://[^\s]+"}
        matches = tmux_capture.find_text_matches([line], patterns, term)
        assert len(matches) == 1
        # "中文" = 4 display cols, " " = 1 -> URL at display col 5
        assert matches[0]["start_col"] == 5

    def test_multiple_matches_on_cjk_line(self):
        """Multiple matches on a line with CJK should all have correct positions."""
        term = make_term_mock()
        # "中 192.168.1.1 和 10.0.0.1"
        # 中(2) space(1) = 3 before first IP
        # first IP is 11 chars (display cols 3-13), space(1), 和(2), space(1) = 4 more
        # second IP starts at display col 18
        line = "中 192.168.1.1 和 10.0.0.1"
        patterns = {"IP_ADDRESS": r"\d+\.\d+\.\d+\.\d+"}
        matches = tmux_capture.find_text_matches([line], patterns, term)
        assert len(matches) == 2
        matches.sort(key=lambda m: m["start_col"])
        assert matches[0]["start_col"] == 3
        assert matches[0]["end_col"] == 14
        assert matches[1]["start_col"] == 18
        assert matches[1]["end_col"] == 26


class TestCJKOverlayAlignment:
    """Test that overlay rendering aligns highlights with actual text."""

    def test_original_styled_segment_preserved_with_cjk(self):
        """The original_styled_segment should contain the correct text."""
        term = make_term_mock()
        line = "中文 https://example.com 测试"
        patterns = {"URL": r"https://[^\s]+"}
        matches = tmux_capture.find_text_matches([line], patterns, term)
        assert len(matches) == 1
        # The styled segment should be exactly the URL
        assert "https://example.com" in matches[0]["original_styled_segment"]

    def test_cjk_text_not_falsely_matched_by_file_path(self):
        """CJK text should not be falsely matched as file paths or other patterns."""
        term = make_term_mock()
        # "使用 scripts/capture.sh" - only "scripts/capture.sh" should match
        line = "使用 scripts/capture.sh"
        patterns = {"FILE_PATH": tmux_capture.REGEX_PATTERNS["FILE_PATH"]}
        matches = tmux_capture.find_text_matches([line], patterns, term)
        for m in matches:
            # No match should contain CJK characters
            assert not any(
                "\u4e00" <= c <= "\u9fff" for c in m["text"]
            ), f"Match '{m['text']}' contains CJK characters"
