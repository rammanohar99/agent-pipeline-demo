from textkit import capitalize_words, word_count


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
