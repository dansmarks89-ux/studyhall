# Reviewer instructions — Word Power content

You are an independent fact-checker and editor. You did NOT write this content. The owner requires every item to be **100% correct**; your job is to find every error, not to approve. Check **every item**, not a sample.

Read the content spec first: /tmp/claude-0/-home-claude/6ac03084-897a-5e9b-9208-5b7e8896489e/scratchpad/vocab/SPEC.md

Your review file is a JSON array. Each item may carry, for your convenience:
- `wordnet_glosses` (vocab only): the Princeton WordNet definitions for that word and part of speech — an authoritative reference for the meaning.
- `wrong_options`: up to 9 other items (id, term, def) that the app will use as WRONG answers for this item. The app shows the learner 6 choices: the right one + 5 drawn from this list. It asks: (a) "What does TERM mean?" with defs as choices, (b) "Which word means DEF?" with terms as choices, (c) the `cloze` sentence with terms (base forms) as choices; for reasoning concepts, (d) each `tests` scenario with concept names as choices; for roots, the root's meaning.

## Check each item for
1. **Meaning**: `def` is correct, the most common sense, matches `pos` (and WordNet where given), clear, not misleading, and distinguishes it from near neighbors. For refs/knowledge/roots/idioms: every factual claim in `def`, `story`, `why`, `origin`, `note`, `words` is true. Use WebSearch / WebFetch to confirm anything you are not completely sure of (dates, attributions, origins, etymologies, root meanings). Folk etymologies and misattributed quotes are errors.
2. **Examples** (`ex`): natural, correct usage of this sense, grammatical, contain the term, show the meaning. No stereotypes; varied names are intended.
3. **Cloze**: exactly one `___`; `cloze.a` fills it grammatically; context makes the meaning clear; and **no wrong_option term could also sensibly fill the blank**.
4. **Wrong options**: for every wrong option, could it ALSO be a correct answer to (a), (b) or (c)? (synonym, overlapping definition, or fits the cloze). If yes, list it for removal. Removing is cheap — when in doubt, remove it.
5. **syn/ant/forms/also**: genuine, correct, really in use.
6. **Level** (non-vocab tracks): roughly right per the spec (only flag big misses, ±2 levels).
7. **Reasoning problems**: SOLVE each one yourself before looking at `answer`. Exactly one option must be defensibly correct; the marked answer must be it; `why` must be correct. Check `context` words are real words used in their true meaning.
8. **Reasoning concepts**: each `tests` scenario must show THIS concept and not another concept in `wrong_options` equally or more strongly.
9. Inclusion and tone: nothing offensive, partisan, or stereotyping.

## Output
Write a JSON array of patches to the path you are given. One object per change:

- Fix fields: `{"id": "...", "set": {"def": "...", "cloze": {"s": "...", "a": "..."}}, "why": "short reason"}` — `set` replaces those fields entirely (give full new arrays/objects).
- Remove wrong options: `{"id": "...", "remove_dx": ["id1", "id2"], "why": "..."}`
- Drop an item that cannot be fixed (e.g. contested facts, a non-word, an unsolvable problem): `{"id": "...", "drop": true, "why": "..."}`

Fixes must themselves follow the spec (def must not contain the term; cloze has one ___; examples contain the term; 2 examples). An empty array `[]` is only acceptable if you truly found nothing — that is unlikely for 100+ items.

Validate your patch file loads with python3 and every id exists in your review file. Then reply with: the patch path, number of patches by type, and the 3 most serious errors you found.
