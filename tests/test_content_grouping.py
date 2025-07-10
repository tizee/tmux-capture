"""Test content grouping and hint assignment functionality."""

import pytest
from . import conftest
tmux_capture = conftest.tmux_capture


class TestContentGrouping:
    """Test content grouping and hint assignment for reducing hint count."""

    def test_group_matches_by_content_basic(self):
        """Test basic content grouping functionality."""
        matches = [
            {"text": "https://example.com", "line_idx": 0, "start_col": 0, "end_col": 18},
            {"text": "user@example.com", "line_idx": 1, "start_col": 0, "end_col": 16},
            {"text": "https://example.com", "line_idx": 2, "start_col": 5, "end_col": 23},
            {"text": "192.168.1.1", "line_idx": 3, "start_col": 0, "end_col": 11},
        ]

        groups = tmux_capture.group_matches_by_content(matches)

        # Should have 3 unique content groups
        assert len(groups) == 3

        # https://example.com should have 2 matches
        assert len(groups["https://example.com"]) == 2

        # user@example.com should have 1 match
        assert len(groups["user@example.com"]) == 1

        # 192.168.1.1 should have 1 match
        assert len(groups["192.168.1.1"]) == 1

    def test_group_matches_by_content_empty(self):
        """Test content grouping with empty input."""
        matches = []
        groups = tmux_capture.group_matches_by_content(matches)
        assert groups == {}

    def test_group_matches_by_content_single(self):
        """Test content grouping with single match."""
        matches = [
            {"text": "single-match", "line_idx": 0, "start_col": 0, "end_col": 12},
        ]

        groups = tmux_capture.group_matches_by_content(matches)

        assert len(groups) == 1
        assert len(groups["single-match"]) == 1
        assert groups["single-match"][0]["text"] == "single-match"

    def test_group_matches_by_content_all_same(self):
        """Test content grouping when all matches have same content."""
        matches = [
            {"text": "duplicate", "line_idx": 0, "start_col": 0, "end_col": 9},
            {"text": "duplicate", "line_idx": 1, "start_col": 5, "end_col": 14},
            {"text": "duplicate", "line_idx": 2, "start_col": 10, "end_col": 19},
            {"text": "duplicate", "line_idx": 3, "start_col": 15, "end_col": 24},
        ]

        groups = tmux_capture.group_matches_by_content(matches)

        assert len(groups) == 1
        assert len(groups["duplicate"]) == 4

        # All matches should be in the same group
        for i, match in enumerate(groups["duplicate"]):
            assert match["text"] == "duplicate"
            assert match["line_idx"] == i

    def test_group_matches_by_content_preserves_metadata(self):
        """Test that content grouping preserves match metadata."""
        matches = [
            {
                "text": "test-content",
                "line_idx": 5,
                "start_col": 10,
                "end_col": 22,
                "pattern": "URL",
                "original_styled_segment": "\x1b[32mtest-content\x1b[0m"
            },
            {
                "text": "test-content",
                "line_idx": 8,
                "start_col": 3,
                "end_col": 15,
                "pattern": "URL",
                "original_styled_segment": "test-content"
            },
        ]

        groups = tmux_capture.group_matches_by_content(matches)

        assert len(groups) == 1
        assert len(groups["test-content"]) == 2

        # Check that metadata is preserved
        first_match = groups["test-content"][0]
        assert first_match["line_idx"] == 5
        assert first_match["start_col"] == 10
        assert first_match["end_col"] == 22
        assert first_match["pattern"] == "URL"
        assert first_match["original_styled_segment"] == "\x1b[32mtest-content\x1b[0m"

        second_match = groups["test-content"][1]
        assert second_match["line_idx"] == 8
        assert second_match["start_col"] == 3
        assert second_match["end_col"] == 15
        assert second_match["pattern"] == "URL"
        assert second_match["original_styled_segment"] == "test-content"

    def test_assign_hints_to_groups_basic(self):
        """Test basic hint assignment to content groups."""
        content_groups = {
            "https://example.com": [{"text": "https://example.com"}],
            "user@example.com": [{"text": "user@example.com"}],
            "192.168.1.1": [{"text": "192.168.1.1"}],
        }

        content_to_hint = tmux_capture.assign_hints_to_groups(content_groups, "vim-movement")

        # Should have 3 unique hints
        assert len(content_to_hint) == 3

        # Should assign vim movement keys
        expected_hints = ['h', 'j', 'k']
        assigned_hints = list(content_to_hint.values())
        assert set(assigned_hints) == set(expected_hints)

        # Each content should have a unique hint
        assert len(set(assigned_hints)) == len(assigned_hints)

    def test_assign_hints_to_groups_empty(self):
        """Test hint assignment with empty content groups."""
        content_groups = {}
        content_to_hint = tmux_capture.assign_hints_to_groups(content_groups)
        assert content_to_hint == {}

    def test_assign_hints_to_groups_single(self):
        """Test hint assignment with single content group."""
        content_groups = {
            "single-content": [{"text": "single-content"}],
        }

        content_to_hint = tmux_capture.assign_hints_to_groups(content_groups, "vim-movement")

        assert len(content_to_hint) == 1
        assert content_to_hint["single-content"] == "h"

    def test_assign_hints_to_groups_many_contents(self):
        """Test hint assignment with many content groups."""
        # Create 15 unique content groups
        content_groups = {}
        for i in range(15):
            content_groups[f"content-{i}"] = [{"text": f"content-{i}"}]

        content_to_hint = tmux_capture.assign_hints_to_groups(content_groups, "vim-movement")

        assert len(content_to_hint) == 15

        # All hints should be unique
        hints = list(content_to_hint.values())
        assert len(set(hints)) == 15

        # With 15 hints needed from an 8-character alphabet, the optimal
        # distribution is 7 single-character hints and 8 two-character hints.
        # n_short = floor((8^2 - 15) / (8 - 1)) = 7

        # The first 7 characters of the alphabet should be present as hints.
        short_hints = ['h', 'j', 'k', 'l', 'w', 'b', 'e']
        for hint in short_hints:
            assert hint in hints

        # The 8th character, 'f', is reserved as a prefix for the longer hints
        # and should not exist as a standalone hint.
        prefix_char = 'f'
        assert prefix_char not in hints

        # There should be 8 two-character hints starting with the prefix.
        long_hints_count = sum(1 for h in hints if h.startswith(prefix_char))
        assert long_hints_count == 8

    def test_assign_hints_to_groups_different_alphabets(self):
        """Test hint assignment with different alphabet configurations."""
        content_groups = {
            "content-1": [{"text": "content-1"}],
            "content-2": [{"text": "content-2"}],
            "content-3": [{"text": "content-3"}],
        }

        # Test with different alphabets
        alphabets_to_test = ["vim-movement", "qwerty-homerow", "numeric", "abcd"]

        for alphabet_key in alphabets_to_test:
            content_to_hint = tmux_capture.assign_hints_to_groups(content_groups, alphabet_key)

            assert len(content_to_hint) == 3

            # All hints should be unique
            hints = list(content_to_hint.values())
            assert len(set(hints)) == 3

            # Hints should come from the specified alphabet
            alphabet = tmux_capture.ALPHABETS[alphabet_key]
            for hint in hints:
                assert all(char in alphabet for char in hint)

    def test_assign_hints_to_groups_deterministic(self):
        """Test that hint assignment is deterministic."""
        content_groups = {
            "alpha": [{"text": "alpha"}],
            "beta": [{"text": "beta"}],
            "gamma": [{"text": "gamma"}],
        }

        # Run multiple times and check consistency
        results = []
        for _ in range(5):
            content_to_hint = tmux_capture.assign_hints_to_groups(content_groups, "vim-movement")
            results.append(content_to_hint)

        # All results should be identical
        for result in results[1:]:
            assert result == results[0]

    def test_content_grouping_integration_with_matches(self):
        """Test integration of content grouping with actual match data."""
        # Simulate matches from find_text_matches
        matches = [
            {
                "text": "https://github.com/user/repo",
                "line_idx": 0,
                "start_col": 0,
                "end_col": 29,
                "pattern": "GITHUB_REPO",
                "original_styled_segment": "https://github.com/user/repo"
            },
            {
                "text": "192.168.1.1",
                "line_idx": 1,
                "start_col": 12,
                "end_col": 23,
                "pattern": "IP_ADDRESS",
                "original_styled_segment": "192.168.1.1"
            },
            {
                "text": "https://github.com/user/repo",
                "line_idx": 2,
                "start_col": 5,
                "end_col": 34,
                "pattern": "GITHUB_REPO",
                "original_styled_segment": "https://github.com/user/repo"
            },
            {
                "text": "user@example.com",
                "line_idx": 3,
                "start_col": 0,
                "end_col": 16,
                "pattern": "EMAIL",
                "original_styled_segment": "user@example.com"
            },
            {
                "text": "192.168.1.1",
                "line_idx": 4,
                "start_col": 8,
                "end_col": 19,
                "pattern": "IP_ADDRESS",
                "original_styled_segment": "192.168.1.1"
            },
        ]

        # Group matches by content
        content_groups = tmux_capture.group_matches_by_content(matches)

        # Should have 3 unique content groups
        assert len(content_groups) == 3

        # GitHub repo appears twice
        assert len(content_groups["https://github.com/user/repo"]) == 2

        # IP address appears twice
        assert len(content_groups["192.168.1.1"]) == 2

        # Email appears once
        assert len(content_groups["user@example.com"]) == 1

        # Assign hints to groups
        content_to_hint = tmux_capture.assign_hints_to_groups(content_groups, "vim-movement")

        # Should assign 3 hints for 3 unique contents
        assert len(content_to_hint) == 3

        # Add hints to matches
        for match in matches:
            match["hint"] = content_to_hint[match["text"]]

        # Check that same content has same hint
        github_matches = [m for m in matches if m["text"] == "https://github.com/user/repo"]
        assert len(github_matches) == 2
        assert github_matches[0]["hint"] == github_matches[1]["hint"]

        ip_matches = [m for m in matches if m["text"] == "192.168.1.1"]
        assert len(ip_matches) == 2
        assert ip_matches[0]["hint"] == ip_matches[1]["hint"]

        # All hints should be different
        all_hints = [content_to_hint[content] for content in content_groups.keys()]
        assert len(set(all_hints)) == len(all_hints)

    def test_content_grouping_preserves_order(self):
        """Test that content grouping preserves order of matches within groups."""
        matches = [
            {"text": "duplicate", "line_idx": 5, "start_col": 0, "end_col": 9},
            {"text": "unique", "line_idx": 1, "start_col": 0, "end_col": 6},
            {"text": "duplicate", "line_idx": 2, "start_col": 10, "end_col": 19},
            {"text": "duplicate", "line_idx": 8, "start_col": 5, "end_col": 14},
        ]

        groups = tmux_capture.group_matches_by_content(matches)

        # Check that order is preserved within groups
        duplicate_group = groups["duplicate"]
        assert len(duplicate_group) == 3

        # Should be in the same order as they appeared in original matches
        assert duplicate_group[0]["line_idx"] == 5
        assert duplicate_group[1]["line_idx"] == 2
        assert duplicate_group[2]["line_idx"] == 8
