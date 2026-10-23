from textkit import capitalize_words


def test_capitalize_words():
    assert capitalize_words("hello big world") == "Hello Big World"


def test_capitalize_words_empty():
    assert capitalize_words("") == ""
