def capitalize_words(text: str) -> str:
    """Capitalize the first letter of every whitespace-separated word."""
    return " ".join(word[:1].upper() + word[1:] for word in text.split())


def word_count(text: str) -> int:
    """Count the whitespace-separated words in text, 0 for empty or blank input."""
    return len(text.split())


def truncate(text: str, max_len: int, suffix: str = "...") -> str:
    """Shorten text to max_len characters, cutting at a word boundary and appending suffix."""
    if len(text) <= max_len:
        return text
    if max_len < len(suffix):
        raise ValueError("max_len must be at least as long as suffix")

    available = max_len - len(suffix)
    truncated = text[:available]
    if available > 0 and available < len(text) and text[available] != " ":
        last_space = truncated.rfind(" ")
        if last_space != -1:
            truncated = truncated[:last_space]
    return truncated.rstrip() + suffix
