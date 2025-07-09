"""Test hint generation algorithms and keyboard layouts."""

import pytest
from . import conftest
tmux_capture = conftest.tmux_capture


class TestHintGeneration:
    """Test hint generation with different alphabets and counts."""
    
    def test_generate_hints_vim_movement(self):
        """Test hint generation with vim movement keys."""
        hints = tmux_capture.generate_hints(8, "vim-movement")
        expected = ['h', 'j', 'k', 'l', 'w', 'b', 'e', 'f']
        assert hints == expected
    
    def test_generate_hints_vim_movement_overflow(self):
        """Test hint generation when count exceeds single character alphabet."""
        hints = tmux_capture.generate_hints(10, "vim-movement")
        expected = ['h', 'j', 'k', 'l', 'w', 'b', 'e', 'f', 'hh', 'hj']
        assert hints == expected
    
    def test_generate_hints_vim_homerow(self):
        """Test hint generation with vim homerow keys."""
        hints = tmux_capture.generate_hints(5, "vim-homerow")
        expected = ['h', 'j', 'k', 'l', 'a']
        assert hints == expected
    
    def test_generate_hints_qwerty_homerow(self):
        """Test hint generation with qwerty homerow keys."""
        hints = tmux_capture.generate_hints(5, "qwerty-homerow")
        expected = ['a', 's', 'd', 'f', 'j']
        assert hints == expected
    
    def test_generate_hints_numeric(self):
        """Test hint generation with numeric keys."""
        hints = tmux_capture.generate_hints(5, "numeric")
        expected = ['1', '2', '3', '4', '5']
        assert hints == expected
    
    def test_generate_hints_abcd(self):
        """Test hint generation with simple abcd alphabet."""
        hints = tmux_capture.generate_hints(6, "abcd")
        expected = ['a', 'b', 'c', 'd', 'aa', 'ab']
        assert hints == expected
    
    def test_generate_hints_dvorak(self):
        """Test hint generation with dvorak layout."""
        hints = tmux_capture.generate_hints(5, "dvorak")
        expected = ['a', 'o', 'e', 'u', 'q']
        assert hints == expected
    
    def test_generate_hints_colemak(self):
        """Test hint generation with colemak layout."""
        hints = tmux_capture.generate_hints(5, "colemak")
        expected = ['a', 'r', 's', 't', 'q']
        assert hints == expected
    
    def test_generate_hints_empty_count(self):
        """Test hint generation with zero count."""
        hints = tmux_capture.generate_hints(0, "vim-movement")
        assert hints == []
    
    def test_generate_hints_large_count(self):
        """Test hint generation with large count."""
        hints = tmux_capture.generate_hints(100, "vim-movement")
        assert len(hints) == 100
        assert len(set(hints)) == 100  # All hints should be unique
    
    def test_generate_hints_invalid_alphabet(self):
        """Test hint generation with invalid alphabet key."""
        # Should fallback to default alphabet
        hints = tmux_capture.generate_hints(5, "invalid-alphabet")
        expected = tmux_capture.generate_hints(5, tmux_capture.DEFAULT_ALPHABET)
        assert hints == expected
    
    def test_generate_hints_multi_character_expansion(self):
        """Test that multi-character hints are generated correctly."""
        hints = tmux_capture.generate_hints(20, "abcd")
        
        # First 4 should be single characters
        assert hints[:4] == ['a', 'b', 'c', 'd']
        
        # Next 16 should be double characters: aa, ab, ac, ad, ba, bb, bc, bd, etc.
        expected_double = ['aa', 'ab', 'ac', 'ad', 'ba', 'bb', 'bc', 'bd', 
                          'ca', 'cb', 'cc', 'cd', 'da', 'db', 'dc', 'dd']
        assert hints[4:] == expected_double
    
    def test_generate_hints_character_limit(self):
        """Test that hints don't exceed 3 characters."""
        # Use a small alphabet to force long hints
        hints = tmux_capture.generate_hints(100, "abcd")
        
        # No hint should be longer than 3 characters
        max_length = max(len(hint) for hint in hints)
        assert max_length <= 3
    
    def test_alphabet_configurations(self):
        """Test that all alphabet configurations are valid."""
        for alphabet_key in tmux_capture.ALPHABETS:
            alphabet = tmux_capture.ALPHABETS[alphabet_key]
            
            # Each alphabet should be non-empty
            assert len(alphabet) > 0
            
            # Each alphabet should contain only unique characters
            assert len(set(alphabet)) == len(alphabet), f"Duplicate characters in {alphabet_key}: {alphabet}"
            
            # Generate hints should work for each alphabet
            hints = tmux_capture.generate_hints(5, alphabet_key)
            assert len(hints) == 5
    
    def test_vim_movement_priority(self):
        """Test that vim movement keys have correct priority."""
        alphabet = tmux_capture.ALPHABETS["vim-movement"]
        
        # Should start with hjkl (movement keys)
        assert alphabet[:4] == "hjkl"
        
        # Should continue with wbef (word movement keys)
        assert alphabet[4:8] == "wbef"
    
    def test_vim_homerow_priority(self):
        """Test that vim homerow includes movement keys first."""
        alphabet = tmux_capture.ALPHABETS["vim-homerow"]
        
        # Should start with hjkl
        assert alphabet[:4] == "hjkl"
        
        # Should include typical homerow keys
        assert 'a' in alphabet
        assert 's' in alphabet
        assert 'd' in alphabet
        assert 'f' in alphabet
    
    def test_default_alphabet_setting(self):
        """Test that default alphabet is set correctly."""
        assert tmux_capture.DEFAULT_ALPHABET == "vim-movement"
        assert tmux_capture.DEFAULT_ALPHABET in tmux_capture.ALPHABETS
    
    def test_keyboard_layout_completeness(self):
        """Test that keyboard layouts contain expected keys."""
        # QWERTY layouts
        assert 'a' in tmux_capture.ALPHABETS["qwerty"]
        assert 's' in tmux_capture.ALPHABETS["qwerty"]
        assert 'd' in tmux_capture.ALPHABETS["qwerty"]
        assert 'f' in tmux_capture.ALPHABETS["qwerty"]
        
        # Dvorak layouts
        assert 'a' in tmux_capture.ALPHABETS["dvorak"]
        assert 'o' in tmux_capture.ALPHABETS["dvorak"]
        assert 'e' in tmux_capture.ALPHABETS["dvorak"]
        assert 'u' in tmux_capture.ALPHABETS["dvorak"]
        
        # Colemak layouts
        assert 'a' in tmux_capture.ALPHABETS["colemak"]
        assert 'r' in tmux_capture.ALPHABETS["colemak"]
        assert 's' in tmux_capture.ALPHABETS["colemak"]
        assert 't' in tmux_capture.ALPHABETS["colemak"]
    
    def test_hint_uniqueness_large_scale(self):
        """Test hint uniqueness with various alphabets and large counts."""
        test_cases = [
            ("vim-movement", 50),
            ("qwerty-homerow", 100),
            ("numeric", 30),
            ("abcd", 25),
        ]
        
        for alphabet_key, count in test_cases:
            hints = tmux_capture.generate_hints(count, alphabet_key)
            assert len(hints) == count
            assert len(set(hints)) == count, f"Duplicate hints found for {alphabet_key} with count {count}"
    
    def test_hint_generation_consistency(self):
        """Test that hint generation is consistent across calls."""
        for alphabet_key in tmux_capture.ALPHABETS:
            hints1 = tmux_capture.generate_hints(10, alphabet_key)
            hints2 = tmux_capture.generate_hints(10, alphabet_key)
            assert hints1 == hints2, f"Inconsistent hint generation for {alphabet_key}"