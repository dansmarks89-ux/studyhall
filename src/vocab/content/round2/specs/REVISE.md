# Your job: upgrade existing Word Power vocabulary cards for the new version

Read /tmp/wp/SPEC.md (main + ADDENDUM). Your input file lists existing cards (already fact-checked once). Make three kinds of fix, and ONLY these:

1. **Plain-word definitions.** Cards with `FLAG_hard_words_in_def` use words too rare for their level (a learner who doesn't know the headword wouldn't know them either). Rewrite the `def` in plainer words while keeping it exactly as precise and correct (6–22 words, must not contain the term or a form of it). If a flagged word truly cannot be replaced without losing accuracy, leave the def. Also rewrite any other def on your list that uses a word much harder than the headword even if not flagged. Same for `FLAG_hard_words_in_also` (the part before the parenthesis).
2. **Synonyms and opposites are now tested** ("Which word is closest in meaning to X?" with one `syn` as the right answer; "Which word is the opposite of X?" with one `ant`). Remove any `syn` that is not a true synonym in this sense, or that is so obscure a learner at this level wouldn't recognize it; remove any `ant` that is not a genuine opposite (an empty list is fine). You may add a clearly correct common synonym/opposite if the list would otherwise be empty and one obviously exists.
3. **`also` format.** If present it must be `"<plain definition of a second common sense> (“<short example using the word>”)"`, the definition part correct and not containing the word.

Output: a JSON array of patches, written to your output path: `{"id": "...", "set": {"def": "...", "syn": [...], "ant": [...], "also": "..."}, "why": "short reason"}` — include in `set` only fields you changed (full new value). Validate it loads with python3 and every id exists in your input.
Reply with ONE line: `<output path>: N patches (D defs, S syn/ant, A also)`.
