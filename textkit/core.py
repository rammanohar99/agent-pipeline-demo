def capitalize_words(text: str) -> str:
    """Capitalize the first letter of every whitespace-separated word."""
    return " ".join(word[:1].upper() + word[1:] for word in text.split())
