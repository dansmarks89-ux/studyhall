# Your job: add new cards to one Word Power track

1. Read /tmp/wp/SPEC.md (main spec + ADDENDUM; the addendum's plain-word and "synonyms/opposites tested" rules apply to every track that has `def`, `syn`, `ant`). Accuracy is the top priority: every fact, origin, story, date and attribution must be correct. Use WebSearch/WebFetch to confirm anything you are not completely sure of. If a claim can't be confirmed, leave it out.
2. See the exact format: first 3 items of the matching file in /tmp/wp/raw_old/ (idioms-A.json, refs-A.json, knowledge-A.json, roots.json, reasoning-concepts.json, reasoning-problems.json).
3. Do NOT repeat anything already in the app: /tmp/wp/existing_terms.txt lists every existing card (track, level, term). Also avoid near-duplicates (same idiom in another wording). Other writers are working on other levels of the same track in parallel; stay inside YOUR level's difficulty so you don't collide.
4. Definitions in plain, common words that a learner at that level understands (never define a hard term with another hard term).
5. Write one JSON array to your output path. Then run `python3 /tmp/wp/validate_track.py <output path>` and fix every PROBLEM. Re-run until clean.
6. Reply with ONE line only: `<output path>: N cards, P problems left`.

## New levels (this round)
- **Roots levels 4–5**: rarer but genuine Greek/Latin elements that still appear in several real English words an educated reader meets (e.g. level 4: "-cracy"-type is level 3 already; level 4 like "ortho", "pseudo", "-algia", "noct", "pyr"; level 5 like "eu-", "-phagy", "ichthy", "lith", "-cide" if not already present). Every example word must really contain that element with that meaning (no false friends) — check etymology.
- **Reasoning levels 4–5**: harder. Concepts (`c-`): e.g. regression to the mean, Simpson's paradox, affirming the consequent, denying the antecedent, motte-and-bailey, Goodhart's law, Bayesian updating, p-hacking, ecological fallacy, Chesterton's fence (only if not already present). Problems (`p-`): multi-step logic (quantifiers, "only if", contrapositives), statistics and evidence reasoning, harder analogies with abstract relations, inference from denser passages, context clues for genuinely rare real words. Exactly one defensibly correct option; SOLVE each problem yourself twice.
