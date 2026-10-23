import pytest

from textkit import capitalize_words, slugify, truncate, word_count


def test_capitalize_words():
    assert capitalize_words("hello big world") == "Hello Big World"


def test_capitalize_words_empty():
    assert capitalize_words("") == ""


def test_word_count():
    assert word_count("hello big world") == 3


def test_word_count_empty():
    assert word_count("") == 0


def test_word_count_whitespace_only():
    assert word_count("   \n\t  ") == 0


def test_word_count_extra_whitespace():
    assert word_count("  hello   world  ") == 2


def test_truncate_fits_unchanged():
    assert truncate("hello world", 11) == "hello world"


def test_truncate_cuts_at_word_boundary():
    assert truncate("The quick brown fox jumps", 15) == "The quick..."


def test_truncate_custom_suffix():
    assert truncate("The quick brown fox jumps", 15, suffix="(more)") == "The quick(more)"


def test_truncate_max_len_equals_suffix_len():
    assert truncate("hello world", 3, suffix="...") == "..."


def test_truncate_no_word_boundary_hard_cuts():
    assert truncate("Supercalifragilisticexpialidocious", 5) == "Su..."


def test_truncate_raises_when_max_len_too_small():
    with pytest.raises(ValueError):
        truncate("hello world", 2, suffix="...")


def test_truncate_fits_unchanged_even_when_max_len_shorter_than_suffix():
    assert truncate("ab", 2) == "ab"
    assert truncate("", 0) == ""


def test_slugify_basic():
    assert slugify("Hello, World!") == "hello-world"


def test_slugify_strips_accents():
    assert slugify("Café") == "cafe"


def test_slugify_collapses_runs_of_non_alphanumeric():
    assert slugify("one   two---three") == "one-two-three"


def test_slugify_trims_leading_and_trailing_hyphens():
    assert slugify("  --Hello World--  ") == "hello-world"


def test_slugify_empty():
    assert slugify("") == ""


def test_slugify_only_punctuation():
    assert slugify("!!!") == ""
