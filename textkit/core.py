def capitalize_words(text: str) -> str:
    """Capitalize the first letter of every whitespace-separated word."""
    return " ".join(word[:1].upper() + word[1:] for word in text.split())


def word_count(text: str) -> int:
    """Count the whitespace-separated words in text, 0 for empty or blank input."""
    return len(text.split())
