# Reviewer instructions — Word Power reading passages

You are an independent fact-checker and editor. You did NOT write these. The owner requires every item to be 100% correct; find every error. Check EVERY passage.

The writers' brief is /tmp/wp/PASSAGES.md — read it. The level's word cards (the meaning the app teaches for each target word) are in /tmp/wp/levelwords/L<level>.json.

For each passage check:
1. Each target word (ids in `words`) is used in the passage in **the meaning on its card**, correctly and naturally. If not, rewrite that sentence (keep the word) or swap in another word from the level list.
2. The passage reads naturally, is grammatical, suits the level (Starter passages: very simple words and sentences), and every real-world fact is true (confirm with WebSearch if unsure; if a fact can't be confirmed, make it fictional/everyday). No stereotypes, nothing partisan, sexual or gruesome.
3. **Solve each question yourself from the passage alone before looking at `answer`.** Exactly one option must be defensibly correct, `answer` must point to it, `why` must be right. For `word` questions, the right option must match how the word is used in the passage, and no wrong option may also fit. Fix anything ambiguous by rewriting options.

Output: a JSON array of patches written to your output path:
- `{"id": "...", "set": {"text": "...", "qs": [...full 3 questions...], "words": [...]}, "why": "..."}` — `set` replaces those fields entirely.
- `{"id": "...", "drop": true, "why": "..."}` only if it can't be fixed.
After writing, apply your patches to a temporary copy and run `python3 /tmp/wp/validate_passages.py <that copy>`; fix until 0 problems.
Reply with: the patch path, number of patches by type, and the 3 most serious errors (one line each).
