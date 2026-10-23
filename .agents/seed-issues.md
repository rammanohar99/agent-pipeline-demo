# Starter issues (label each `agent:todo`)

1. **Add `slugify(text)`** - lowercase, strip accents, replace runs of non-alphanumerics with a
   single `-`, trim leading/trailing `-`. `slugify("Hello, World!") == "hello-world"`.
2. **Add `word_count(text)`** - number of whitespace-separated words; `0` for empty or whitespace-only input.
3. **Add `truncate(text, max_len, suffix="...")`** - cut at the last word boundary so the result
   including suffix is <= `max_len`; return text unchanged if it already fits; raise `ValueError`
   if `max_len < len(suffix)`.
