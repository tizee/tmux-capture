"""Tests for overlapping match resolution."""

import pytest
from unittest.mock import Mock
from . import conftest
tmux_capture = conftest.tmux_capture


class TestOverlapResolution:
    """Test cases for overlapping match resolution."""

    def test_resolve_overlapping_matches_email_vs_large_number(self):
        """Test that EMAIL pattern wins over LARGE_NUMBER for email addresses."""
        matches = [
            {
                "text": "33030965+tizee@users.noreply.github.com",
                "line_idx": 0,
                "start_col": 0,
                "end_col": 39,
                "pattern": "EMAIL",
                "original_styled_segment": "33030965+tizee@users.noreply.github.com",
            },
            {
                "text": "33030965",
                "line_idx": 0,
                "start_col": 0,
                "end_col": 8,
                "pattern": "LARGE_NUMBER",
                "original_styled_segment": "33030965",
            },
        ]
        
        result = tmux_capture._resolve_overlapping_matches(matches)
        
        # Should keep only the EMAIL match (longer and higher priority)
        assert len(result) == 1
        assert result[0]["pattern"] == "EMAIL"
        assert result[0]["text"] == "33030965+tizee@users.noreply.github.com"

    def test_resolve_overlapping_matches_longer_wins(self):
        """Test that longer matches win over shorter ones."""
        matches = [
            {
                "text": "short",
                "line_idx": 0,
                "start_col": 0,
                "end_col": 5,
                "pattern": "GIT_COMMIT",
                "original_styled_segment": "short",
            },
            {
                "text": "longertext",
                "line_idx": 0,
                "start_col": 0,
                "end_col": 10,
                "pattern": "LARGE_NUMBER", 
                "original_styled_segment": "longertext",
            },
        ]
        
        result = tmux_capture._resolve_overlapping_matches(matches)
        
        # Should keep the longer match even if it has lower priority
        assert len(result) == 1
        assert result[0]["text"] == "longertext"

    def test_resolve_overlapping_matches_priority_for_same_length(self):
        """Test that higher priority patterns win for same-length matches."""
        matches = [
            {
                "text": "test",
                "line_idx": 0,
                "start_col": 0,
                "end_col": 4,
                "pattern": "LARGE_NUMBER",
                "original_styled_segment": "test",
            },
            {
                "text": "test",
                "line_idx": 0,
                "start_col": 0,
                "end_col": 4,
                "pattern": "EMAIL",
                "original_styled_segment": "test",
            },
        ]
        
        result = tmux_capture._resolve_overlapping_matches(matches)
        
        # Should keep EMAIL (higher priority)
        assert len(result) == 1
        assert result[0]["pattern"] == "EMAIL"

    def test_resolve_overlapping_matches_no_overlap(self):
        """Test that non-overlapping matches are all kept."""
        matches = [
            {
                "text": "first",
                "line_idx": 0,
                "start_col": 0,
                "end_col": 5,
                "pattern": "EMAIL",
                "original_styled_segment": "first",
            },
            {
                "text": "second",
                "line_idx": 0,
                "start_col": 10,
                "end_col": 16,
                "pattern": "LARGE_NUMBER",
                "original_styled_segment": "second",
            },
        ]
        
        result = tmux_capture._resolve_overlapping_matches(matches)
        
        # Should keep both matches
        assert len(result) == 2
        assert {m["text"] for m in result} == {"first", "second"}

    def test_resolve_overlapping_matches_different_lines(self):
        """Test that matches on different lines don't interfere."""
        matches = [
            {
                "text": "samecol",
                "line_idx": 0,
                "start_col": 0,
                "end_col": 7,
                "pattern": "EMAIL",
                "original_styled_segment": "samecol",
            },
            {
                "text": "samecol",
                "line_idx": 1,
                "start_col": 0,
                "end_col": 7,
                "pattern": "LARGE_NUMBER",
                "original_styled_segment": "samecol",
            },
        ]
        
        result = tmux_capture._resolve_overlapping_matches(matches)
        
        # Should keep both matches (different lines)
        assert len(result) == 2

    def test_resolve_overlapping_matches_empty_input(self):
        """Test handling of empty input."""
        result = tmux_capture._resolve_overlapping_matches([])
        assert result == []

    def test_resolve_overlapping_matches_multiple_overlaps(self):
        """Test resolution with multiple overlapping matches."""
        matches = [
            {
                "text": "abc",
                "line_idx": 0,
                "start_col": 0,
                "end_col": 3,
                "pattern": "LARGE_NUMBER",
                "original_styled_segment": "abc",
            },
            {
                "text": "abcdef",
                "line_idx": 0,
                "start_col": 0,
                "end_col": 6,
                "pattern": "EMAIL",
                "original_styled_segment": "abcdef",
            },
            {
                "text": "def",
                "line_idx": 0,
                "start_col": 3,
                "end_col": 6,
                "pattern": "GIT_COMMIT",
                "original_styled_segment": "def",
            },
        ]
        
        result = tmux_capture._resolve_overlapping_matches(matches)
        
        # Should keep only the EMAIL match (longest)
        assert len(result) == 1
        assert result[0]["pattern"] == "EMAIL"
        assert result[0]["text"] == "abcdef"

    def test_resolve_overlapping_matches_unknown_pattern_priority(self):
        """Test handling of patterns not in priority dictionary."""
        matches = [
            {
                "text": "test",
                "line_idx": 0,
                "start_col": 0,
                "end_col": 4,
                "pattern": "UNKNOWN_PATTERN",
                "original_styled_segment": "test",
            },
            {
                "text": "test",
                "line_idx": 0,
                "start_col": 0,
                "end_col": 4,
                "pattern": "EMAIL",
                "original_styled_segment": "test",
            },
        ]
        
        result = tmux_capture._resolve_overlapping_matches(matches)
        
        # Should keep EMAIL (known priority vs default priority 15)
        assert len(result) == 1
        assert result[0]["pattern"] == "EMAIL"

    def test_resolve_overlapping_matches_partial_overlap(self):
        """Test handling of partial overlaps."""
        matches = [
            {
                "text": "abcde",
                "line_idx": 0,
                "start_col": 0,
                "end_col": 5,
                "pattern": "EMAIL",
                "original_styled_segment": "abcde",
            },
            {
                "text": "cdefg",
                "line_idx": 0,
                "start_col": 2,
                "end_col": 7,
                "pattern": "LARGE_NUMBER",
                "original_styled_segment": "cdefg",
            },
        ]
        
        result = tmux_capture._resolve_overlapping_matches(matches)
        
        # Should keep EMAIL (higher priority, same length)
        assert len(result) == 1
        assert result[0]["pattern"] == "EMAIL"

    def test_resolve_overlapping_matches_adjacent_no_overlap(self):
        """Test that adjacent matches (touching but not overlapping) are both kept."""
        matches = [
            {
                "text": "first",
                "line_idx": 0,
                "start_col": 0,
                "end_col": 5,
                "pattern": "EMAIL",
                "original_styled_segment": "first",
            },
            {
                "text": "second",
                "line_idx": 0,
                "start_col": 5,
                "end_col": 11,
                "pattern": "LARGE_NUMBER",
                "original_styled_segment": "second",
            },
        ]
        
        result = tmux_capture._resolve_overlapping_matches(matches)
        
        # Should keep both (end_col=5 and start_col=5 means no overlap)
        assert len(result) == 2
        assert {m["text"] for m in result} == {"first", "second"}

    def test_resolve_overlapping_matches_complex_priority_order(self):
        """Test complex priority ordering with multiple pattern types."""
        matches = [
            {
                "text": "pattern1",
                "line_idx": 0,
                "start_col": 0,
                "end_col": 8,
                "pattern": "LARGE_NUMBER",
                "original_styled_segment": "pattern1",
            },
            {
                "text": "pattern2",
                "line_idx": 0,
                "start_col": 0,
                "end_col": 8,
                "pattern": "GIT_COMMIT",
                "original_styled_segment": "pattern2",
            },
            {
                "text": "pattern3",
                "line_idx": 0,
                "start_col": 0,
                "end_col": 8,
                "pattern": "URL",
                "original_styled_segment": "pattern3",
            },
        ]
        
        result = tmux_capture._resolve_overlapping_matches(matches)
        
        # Should keep URL (highest priority: 1)
        assert len(result) == 1
        assert result[0]["pattern"] == "URL"

    def test_resolve_overlapping_matches_preserve_order_when_no_conflicts(self):
        """Test that original order is preserved for non-conflicting matches."""
        matches = [
            {
                "text": "third",
                "line_idx": 0,
                "start_col": 20,
                "end_col": 25,
                "pattern": "EMAIL",
                "original_styled_segment": "third",
            },
            {
                "text": "first", 
                "line_idx": 0,
                "start_col": 0,
                "end_col": 5,
                "pattern": "LARGE_NUMBER",
                "original_styled_segment": "first",
            },
            {
                "text": "second",
                "line_idx": 0,
                "start_col": 10,
                "end_col": 16,
                "pattern": "GIT_COMMIT",
                "original_styled_segment": "second",
            },
        ]
        
        result = tmux_capture._resolve_overlapping_matches(matches)
        
        # Should have all 3 matches, sorted by start position
        assert len(result) == 3
        result_by_position = sorted(result, key=lambda x: x["start_col"])
        assert [m["text"] for m in result_by_position] == ["first", "second", "third"]

    def test_resolve_overlapping_matches_single_match(self):
        """Test handling of single match input."""
        matches = [
            {
                "text": "single",
                "line_idx": 0,
                "start_col": 0,
                "end_col": 6,
                "pattern": "EMAIL",
                "original_styled_segment": "single",
            },
        ]
        
        result = tmux_capture._resolve_overlapping_matches(matches)
        
        # Should return the single match unchanged
        assert len(result) == 1
        assert result[0] == matches[0]

    def test_resolve_overlapping_matches_multiple_lines_complex(self):
        """Test complex scenario with overlaps across multiple lines.""" 
        matches = [
            # Line 0: overlap between EMAIL and LARGE_NUMBER
            {
                "text": "user123@example.com",
                "line_idx": 0,
                "start_col": 0,
                "end_col": 19,
                "pattern": "EMAIL",
                "original_styled_segment": "user123@example.com",
            },
            {
                "text": "123",
                "line_idx": 0,
                "start_col": 4,
                "end_col": 7,
                "pattern": "LARGE_NUMBER",
                "original_styled_segment": "123",
            },
            # Line 1: separate match
            {
                "text": "separate",
                "line_idx": 1,
                "start_col": 0,
                "end_col": 8,
                "pattern": "GIT_COMMIT",
                "original_styled_segment": "separate",
            },
            # Line 0: another separate match
            {
                "text": "other",
                "line_idx": 0,
                "start_col": 25,
                "end_col": 30,
                "pattern": "UUID",
                "original_styled_segment": "other",
            },
        ]
        
        result = tmux_capture._resolve_overlapping_matches(matches)
        
        # Should keep EMAIL (line 0), other (line 0), and separate (line 1)
        assert len(result) == 3
        line_0_matches = [m for m in result if m["line_idx"] == 0]
        line_1_matches = [m for m in result if m["line_idx"] == 1]
        
        assert len(line_0_matches) == 2
        assert len(line_1_matches) == 1
        
        # Verify EMAIL won over LARGE_NUMBER on line 0
        email_match = next(m for m in line_0_matches if m["pattern"] == "EMAIL")
        assert email_match["text"] == "user123@example.com"

    def test_readme_documented_example(self):
        """Test the specific example documented in README.md."""
        # This is the exact case mentioned in the issue and documented in README
        matches = [
            {
                "text": "33030965+tizee@users.noreply.github.com",
                "line_idx": 0,
                "start_col": 0,
                "end_col": 39,
                "pattern": "EMAIL",
                "original_styled_segment": "33030965+tizee@users.noreply.github.com",
            },
            {
                "text": "33030965",
                "line_idx": 0,
                "start_col": 0,
                "end_col": 8,
                "pattern": "LARGE_NUMBER",
                "original_styled_segment": "33030965",
            },
        ]
        
        result = tmux_capture._resolve_overlapping_matches(matches)
        
        # Should keep only EMAIL (longer and higher priority)
        # This ensures highlighted text matches copied text exactly
        assert len(result) == 1
        assert result[0]["pattern"] == "EMAIL"
        assert result[0]["text"] == "33030965+tizee@users.noreply.github.com"
        
        # Verify this solves the original issue where highlight != copied text
        assert result[0]["text"] == result[0]["original_styled_segment"].strip()