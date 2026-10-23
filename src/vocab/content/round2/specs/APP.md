# Your job: upgrade the Word Power app (one HTML file) — expert-quality code

Files (work ONLY in /tmp/wp/app/): `app.html` (the app; read ALL of it first, ~1,200 lines), `build.py` (inlines data), `sw.js` (Study Hall's shared service worker). Interim content to test with: /tmp/wp/pipe/all_dx.json (all cards; the field `_old` must be stripped at build), /tmp/wp/pas/L*.json (reading passages; schema in /tmp/wp/PASSAGES.md). Content is still being reviewed; the schema won't change.

Standard: the owner requires code audited to an expert engineer's standard — no dead code, no redundancy, nothing unnecessary; match the existing style (vanilla JS, `$`, `esc`, template strings, existing CSS tokens). Escape every piece of content with `esc`. Keep every existing feature working, and **keep existing saved progress valid** (ids, `R` format, `ST.lv`, `ST.pl` from the old placement must still load and display).

## 1. Data out of the HTML
Content grew to ~9,000 cards + 390 passages (~11 MB). Change `build.py` to write `vocab/data.<10-hex-sha256>.json` (cards + passages, compact JSON) and inject its file name into `vocab/index.html` in place of `__DATA__` (the app then `fetch`es it and starts). The tap-to-define dictionary goes to `vocab/gloss.<hash>.json` the same way (`__GLOSS__`), fetched lazily on first tap. Old hashed files in `vocab/` are deleted by the build. Show a short "Loading…" state until data arrives and a clear retry message if the fetch fails. In `sw.js`, serve same-origin URLs whose path matches `/\.[0-9a-f]{10}\.json$/` cache-first (they never change); everything else stays network-first. build.py takes the gloss from `src/vocab/data/gloss.json` and passages from `src/vocab/data/passages.json` (for testing, create those from the interim files; a small hand-made gloss is fine for testing).

## 2. Levels
- Vocabulary now runs from level -2 to 10: names `Starter 1` (-2), `Starter 2` (-1), `Foundations` (0), `Level 1`…`Level 10`. Short icon labels S1, S2, F, 1…10. Roots and Reasoning now go to level 5.
- Anywhere code assumes vocab level 0 is the minimum or uses `-1` as "nothing passed", use `TR[t].min` / `TR[t].min - 1`. An old saved `ST.pl.vocab.P === -1` (meant "start at Foundations") must still start at Foundations — handle that explicitly (old placements have no version field; give new ones `v: 2`).

## 3. Placement test (vocabulary part) — more accurate
- Before part 1, ask one question: "Is English your first language, or are you still learning it?" → native/fluent: start the sweep at Level 2; learning: start at Starter 1.
- Sweep: blocks of 5 "what does it mean" questions per level. ≥4/5 → go up one level. Fail before any pass → go down (stop at the minimum). 
- Confirm the boundary: once a level P is passed and P+1 failed (or the top/bottom is reached), ask 10 MORE words at P+1 and at P (so each has 15). A level counts as passed at ≥80% of all its questions (≥4/5 for a lone block, ≥12/15 when confirmed). If confirming changes the picture (P+1 now passes, or P fails), move the boundary and confirm again (never ask the same word twice; never confirm a level twice).
- Probe above: after confirming, keep testing 5-word blocks upward from P+2 while the previous level scored ≥40% (to find partly-known higher levels), up to Level 10.
- Final: P = highest level that passed with no failed tested level beneath it; start = P+1 (capped at max). Untested levels below the lowest tested one count as known. Save per-level [right, asked].
- Results screen: the bar list covers Starter 1 to Level 10; show right/asked for each tested level; update the explanatory text (5-word blocks, 15 words where confirmed, 80% = pass). Update the intro estimate on Today ("about 100–130 questions, 25–35 minutes").
- The "Skip — I'll choose" dialog gains a first option: Starter 1 — "New to English: the most common everyday words".
- Other tracks keep 3 questions per level (roots and reasoning now have levels 4–5).

## 4. New question types (more active practice)
In `qtypesFor`/`makeQ`/feedback:
- `syn`: "Which word is closest in meaning to TERM?" — right: one random entry of `x.syn`; wrong: 5 `dx` terms. Only when `x.syn` has an entry.
- `ant`: "Which word means the opposite of TERM?" — right: one entry of `x.ant`; wrong: 5 `dx` terms. Only when `x.ant` has an entry.
- `also`: "Besides its main meaning, what else can TERM mean?" — right: the part of `x.also` before " (“" (trimmed); wrong: 5 `dx` defs. Only when `x.also` exists.
- `sent`: "Use TERM in a sentence of your own" — typed, graded by the existing `aiSentence` (good → correct, awkward → partly right, wrong → wrong), with the same "Graded by Claude / override" pattern and self-grade fallback as typed definitions. It now COUNTS. Offered for vocab, idioms, refs, knowledge at stage ≥4 when typed answers aren't off (more often when "often"). Keep the unscored practice box on study cards.
- Schedule: stage ≤1 mean; 2 cloze; 3 word / cloze / syn / ant (those available); ≥4 cloze, mean, word, syn, ant, also + typed (tdef, tword, sent per setting). Level tests: pick from mean, cloze, word, syn, ant (available ones). Feedback for a wrong syn/ant pick says what the chosen word means.
- Settings text for typed answers mentions sentences.

## 5. Reading practice
Passages (`track: "reading"`, ids `g-…`) are NOT cards: keep them out of LIST/BY-based card code, search and counts. Add on Today a button "Read a passage · 3 questions". Pick: level = current vocab level, then lower levels, then higher; prefer unread passages where at least half the target words have been studied, else any unread at that level. Screen: title, the passage (with a play button that reads it aloud), target words shown in bold. Then the 3 questions one at a time (6 options + "I don't know", feedback shows `why`). Store `R[g-id] = [ok3 ? 1 : 0, due, ...]` like reasoning problems (all correct → not offered again for 60 days; otherwise back after 1 day). A wrong word-question on a word the learner has already studied → `grade(wordId, false)` so it returns to review. Progress page: "passages read" count.

## 6. Tap any word to look it up
- Text containers get class `tap`: card definitions, examples, notes, stories, "why", scenario/fix, roots word meanings, cloze sentences, question prompts, passage text, feedback text. NOT answer-option buttons, NOT the `.term` heading of the card being asked about.
- On tap (click), find the word under the finger with `document.caretRangeFromPoint` (fallback `caretPositionFromPoint`), expand to word boundaries (letters, internal apostrophes/hyphens), ignore taps not on a word. Briefly highlight it.
- Load the gloss lazily. Format: `{"f": {"<lowercased surface form>": ["<key>", ...]}, "d": {"<key>": {"w": "<base word>", "p": "noun|verb|adjective|adverb|...", "s": ["sense 1", "sense 2"], "i": "<card id, optional>"}}}`. Show a bottom sheet (reuse `dialog` styling, mobile-friendly) listing each matching entry: word, part of speech, 1–3 plain senses; a play button; if `i` is a card: its status + "Open card" + (if not yet studied) "Add to my next session" (same as `pinit`). If nothing matches: "No dictionary entry for “x”."
- Guard against revealing answers: while a question is unanswered, tapping a word that IS the asked card's term or one of its forms, or (in reading) a target word of an unanswered word-question, shows "Answer first — you can look this up afterwards."
- The sheet must not break the session (no answer recorded, keyboard shortcuts unaffected while it's open).

## 7. Testing (required)
Build into /tmp/wp/app/out/ (adapt build.py paths via an env var or argument so the real repo layout is unchanged: repo root = two levels above build.py by default). Serve /tmp/wp/app/out with `python3 -m http.server` alongside copies of the repo's `shared/`, `icons/`, `manifest.webmanifest` from /tmp/studyhall, and test in a real headless browser (install playwright + chromium via pip/npm if possible; if browsers can't be downloaded, say so and test logic with Node). Test at 390px width: load, placement (both start paths, the confirm logic incl. edge cases at top and bottom), each new question type, reading flow, tap-to-define (incl. the answer guard), level tests, old saved progress (construct an old `wp:state` with `pl.vocab = {P: 6, start: 7, res: {...}}` and `P: -1`). No console errors.

Reply with: a short list of what you changed, what you tested and how, and anything you couldn't do. Don't paste code.
