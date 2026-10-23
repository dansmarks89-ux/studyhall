# Word Power upgrade: independent audit

Scope: `app.html`, `build.py` and `sw.js` compared with the originals in `/tmp/studyhall`, checked against `APP.md`. Each bug was confirmed by reading the code around it. Most were also run in headless Chromium at 390px against `/tmp/wp/app/out`, with `sh.js` stubbed and the service worker blocked. I also ran the vocabulary placement algorithm (`vocabNext`) in Node through 200,000 simulated learners. It always finished. It never confirmed a level twice, never asked more than 15 words at one level, and always confirmed the boundary. At most it asked 135 vocabulary questions. A typical learner gets 30, 45 or 65 (10th, 50th and 90th percentile).

Summary: **9 bugs, 0 spec gaps, 8 cleanliness or minor items.** One data problem that is not a code problem is listed at the end.

Things that checked out (no finding):
- **Escaping.** Every new content string goes through `esc`.
- **Old saved data.** Old `R` entries, `ST.lv`, old `ST.pl` with `P:6` and `P:-1`, and an old in-progress `RUN` (with `extra` set and no `conf`) all load. The `P:-1` case starts at Foundations and shows its results correctly. The old run resumes and goes on to confirm the boundary.
- **Passages stay out of card code.** They are absent from `BY`, `LIST`, search and counts. `R` entries with a `g-` id are skipped everywhere that `BY` is checked.
- **AI grading after the learner leaves.** The `SESSION !== S0` check covers the `sent` question type.
- **Service worker for other apps.** The hashed-file rule only matches `*.<10 hex>.json`, so the other Study Hall apps are unaffected. Old versions of a hashed file are removed only after the new one has been fetched, so the cache does not grow without limit.

---

## Bugs

### B1. The answer guard misses reasoning problems, and "Open card" in the sheet can show the answer (high)
**Where:** `guarded()`: `return ids.some(id => isFormOf(word, BY[id]) || ents.some(e => e.i === id));` and `glEntry()`: `data-glopen=…`.

**What's wrong:**
- For a problem (`p-…`) the stored `term` is something like `"Context: famished"` or `"Opposite: generous"`, so `isFormOf` never matches the key word in the question.
- Example: *p-context-famished* asks "What does famished most likely mean?". Tapping *famished* before answering opens a sheet that says "extremely hungry, usually after a long time without food", and the correct option is "extremely hungry". I confirmed this in the browser.
- 44 of the 78 context problems have their key word in the dictionary.
- For 29 of the 51 Opposite/Similar problems, the answer is listed under "Similar" or "Opposite" on the card that "Open card" shows (for example, generous shows stingy and enormous shows huge). In 6 more, the answer word appears in the dictionary senses themselves.
- The same prompts are tappable in the placement test's reasoning part, so this also skews placement.
- More generally, "Open card" works while a question is unanswered. The card it opens shows Similar, Opposite and examples. In 251 vocabulary "Which word fits this meaning?" questions, the definition contains a word whose card lists the answer as Similar (remain → *stay*, essential → *necessary*, accurate → *correct*).

**Fix:**
1. In `guarded()`, block every lookup while a problem is unanswered. Context and Opposite/Similar problems are vocabulary questions in disguise, and the others have no hard words to look up. After `if (!S) return false;` add:
   `const st = S.steps[S.i]; if (st.t === "q" && !S.locked && isProb(st.id)) return true;`
2. While any question is unanswered, show dictionary entries without the "Open card" button. In `lookUp()`, compute
   `const live = SESSION && !SESSION.locked && ["q", "pq", "read"].includes(SESSION.steps[SESSION.i].t);`
   pass it to `glEntry(e, live)`, and leave out the `data-glopen` button when `live`. Keep the status chip and "Add to my next session".

### B2. Learners without a placement now start at Starter 1, which pushes existing users back a level (high)
**Where:** `startLv()`: `return p ? Math.min(TR[t].max, p.P + 1) : TR[t].min;`

**What's wrong:**
- The old app could be used without the placement test: "Start today's session" and "Learn 5 more" always work.
- For those users `ST.pl` is null. The old code started them at Foundations (level 0). The new code starts them at Starter 1 (level -2).
- I loaded an old state with no placement and some Foundations progress. The track list showed "Starter 1", and `pickNew(5)` returned `v-order`, `v-head` and `v-man` (all level -2).
- New native speakers who skip the test and press "Start today's session" also get the most basic words.
- `APP.md` requires that existing progress stays valid. The Starter levels are meant to be reached on purpose, through "I'm still learning English" or the first Skip option.

**Fix:** `return p ? Math.min(TR[t].max, p.P + 1) : t === "vocab" ? 0 : TR[t].min;`. Add a comment: "with no placement, vocabulary starts at Foundations, as it always has; English learners reach the Starter levels through the placement question or the Skip dialog". The owner needs to confirm this, because §2 says to use `TR[t].min` everywhere.

### B3. Tapping a non-vocabulary card's synonym or antonym question gives the answer away (medium; follows the spec literally)
**Where:** `makeQ()` for `syn` and `ant`: `opts: shuffle([{ label: pickOne(x[qt]), ok: true }, ...ds.map(d => ({ label: d.term, …`. The same applies to `qtypesFor()` and `startTest()` through `canAsk`.

**What's wrong:**
- For idioms and references, the right answer is a plain word, but the distractors are the `dx` *terms*, which are long multi-word phrases. Examples:
  - "land of milk and honey": the answer is *paradise*; the distractors include "between Scylla and Charybdis" and "Streisand effect".
  - "Iago": the answer is *traitor*; the distractors include "tikkun olam" and "Munchausen syndrome".
- I counted the cases where the right answer is the only single word among the options:

  | Track | Giveaway answers |
  |---|---|
  | Idioms | 706 of 1,399 |
  | References | 108 of 923 |
  | Knowledge | 3 of 264 |
  | Vocabulary | 0 of 26,337 |

- These types also appear in the level tests, so pass rates for those tracks are inflated (passing needs above 90%).

**Fix:** Offer `syn` and `ant` only for vocabulary. In `canAsk`, use `qt === "syn" || qt === "ant" ? x.track === "vocab" && !!(x[qt] && x[qt].length) : …`. The alternative, if the owner wants them on other tracks: use one `syn` entry from each `dx` card as the wrong option instead of `d.term`, so every option has the same shape.

### B4. Hyphenated words are never found in the dictionary (medium)
**Where:** `WORD = /(\p{L}+(?:['’-]\p{L}+)*)/gu`, used by `wordAt()`, and `lookUp()`: `const ents = (G.f[w] || G.f[w.replace(/'s$/, "")] || [])…`.

**What's wrong:**
- A tap expands to the whole hyphenated word, but the dictionary has only 5 hyphenated keys.
- Of the 828 hyphenated words in definitions, examples and passages, 827 come back as "No dictionary entry for “long-term”" (also *old-fashioned*, *self-important*, *well-known*, and so on). Each part has its own entry.

**Fix:**
- In `wordAt()`, also return the hyphen segment under the finger: `part: m[0].split("-")[m[0].slice(0, off - m.index).split("-").length - 1]`.
- Call `lookUp(hit.word, hit.part)`.
- In `lookUp`, try the whole word first, then the part. For example, `const find = k => …; const ents = find(w) || find(part) || [];`, and name the looked-up form in the "no entry" message.

### B5. On iPhone, many taps on text do nothing (medium, mobile)
**Where:** `wordAt()`: `return [...range.getClientRects()].some(b => x >= b.left && x <= b.right && y >= b.top && y <= b.bottom) ? … : null;`

**What's wrong:**
- `caretRangeFromPoint` already picks the right line. The strict rectangle check then rejects any tap in the space between lines.
- In the passage text (line height 29.6px, glyph height 20px), a tap 2px below "Omar" returned `null`.
- Only 53% of the points over the passage text count as being on a word. That includes the gaps between lines, which are about a third of every line's height.
- A fingertip lands about ±5px from where the person aims, so near-miss taps fail silently.

**Fix:** Allow some slack, since the line has already been chosen: `const s = 6; … x >= b.left - 2 && x <= b.right + 2 && y >= b.top - s && y <= b.bottom + s`. The rectangles of other lines are never tested, so this can't pick a word on the wrong line.

### B6. "Add to my next session" throws the learner off a results screen (low–medium)
**Where:** `pin()`: `function pin(id) { R[id] = [...]; save("srs"); if (!SESSION) render(); }`

**What's wrong:**
- On a non-tab screen (session summary, test results, placement results), `SESSION` is null and `VIEW.name` is "screen". `render()` then resets the view to Today.
- I confirmed it: open a missed card from the summary, tap a word, then "Add to my next session". The summary is replaced by Today behind the sheet.
- The old `pinit` did the same, but the dictionary sheet makes this much easier to reach.

**Fix:** `if (!SESSION && TABVIEWS.includes(VIEW.name)) render();`. This is the same check that `connect()` and the `visibilitychange` handler already use.

### B7. Any error during startup is reported as a download failure, and "Try again" duplicates the content (low)
**Where:** `start()`: `.then(d => { index(d); render(); connect(); }).catch(() => { … "Word Power didn't load" …`

**What's wrong:**
- The `.catch` also catches exceptions thrown by `index()`, `render()` or `connect()`. A code or data error shows "Check your internet connection".
- "Try again" then calls `index()` a second time, which pushes every id into `LIST`, `PROB` and `PASLV` twice.

**Fix:** Catch only the fetch and JSON parse: `fetch(DATA_URL).then(r => {…}).then(d => { index(d); render(); connect(); }, () => { …retry screen… });`

### B8. Words that are built-in JavaScript names crash the lookup (low)
**Where:** `lookUp()`: `(G.f[w] || G.f[w.replace(/'s$/, "")] || []).map(…)`

**What's wrong:**
- `G.f` is a plain object, so the word "constructor" finds `Object.prototype.constructor` (a function), and `.map` then throws a TypeError. The same applies to `toString`, `valueOf`, `hasOwnProperty` and similar names.
- The sheet stays on "Looking up…". I confirmed this in the browser.
- These words aren't in the current content, but tappable text includes the learner's own typing ("You wrote: …" inside `.fb.tap`) and the AI's feedback.

**Fix:** `const get = k => Object.hasOwn(G.f, k) ? G.f[k] : null;`, and do the same for `G.d[k]`. Alternatively, in `loadGloss`, call `Object.setPrototypeOf(g.f, null)` and `Object.setPrototypeOf(g.d, null)`.

### B9. A missing `gloss.json` breaks the published site (low)
**Where:** In `build.py`, the gloss file is loaded only inside the final `page = src.replace(... write("gloss", load("gloss.json")))` line, after the old hashed files have been deleted and the new data file written.

**What's wrong:** If `gloss.json` is missing or invalid, the build stops with the old hashed files already deleted. The old `vocab/index.html` still points to them, so the published app is broken until the next successful build.

**Fix:** Load `gloss = load("gloss.json")` next to `items` and `passages`, before any deletion. Then write with `write("gloss", gloss)`.

---

## Spec gaps

None found. Every item in `APP.md` §1–6 is implemented as described:
- Language question and start levels.
- 5-word sweep, confirmation at 15 words with 80% to pass, re-confirmation that never repeats a level, and the probe while the level below scored ≥40%.
- Per-level `[right, asked]`, the results text, the Today estimate, and the Starter 1 option in the Skip dialog.
- The `syn`, `ant`, `also` and scored `sent` question types, the schedule, level-test question types and the wrong-pick feedback.
- Reading: picking order, screen, 3 questions, `R` record, regrading a missed studied word, and the "passages read" count.
- The `.tap` targets, the lazy dictionary, the bottom sheet, the guard (gaps listed in B1), and no interference with keyboard shortcuts.
- Hashed data files, the loading and retry states, and cache-first for hashed files in the service worker.

The one deliberate deviation is fine: a reading passage that is due again is offered first. This is how "back after 1 day" is implemented.

---

## Cleanliness and minor items

1. **Duplicated fetch-JSON code.**
   - **Where:** `loadGloss` and `start()` both contain `fetch(url).then(r => { if (!r.ok) throw new Error(r.status); return r.json(); })`.
   - **Fix:** Add one helper, `const getJSON = url => fetch(url).then(r => { if (!r.ok) throw new Error(r.status); return r.json(); });`, and use it in both places.
2. **`feedback()` reads a missing card for reading questions.**
   - **Where:** `const x = BY[q.id];`. A `pq` question has no `id`, so `x` is `undefined`.
   - **Problem:** It works only because every later use of `x` is short-circuited by `q.qt === "pq"` checks. Any edit that changes the order will throw.
   - **Fix:** Handle `pq` first with an early branch (title + `why`), or give `passageQ` an explicit `id: step.g` and guard `x` uses.
3. **The status chip and "Add" button are written twice.**
   - **Where:** `glEntry()` repeats `openCard()`'s chip and "Add to my next session" markup.
   - **Fix:** Add a shared `statusRow(id, extraButtons)` helper.
4. **The reading hint promises lookups that are then blocked.**
   - **Where:** The read step says "Words in bold are from your vocabulary levels. Tap any word to look it up."
   - **Problem:** The bold words are exactly the ones blocked with "Answer first".
   - **Fix:** Reword to: "Tap any word to look it up (words in bold open after the questions)."
5. **`vocabNext()` changes the run it is computing from.**
   - **Where:** `conf = v.conf = v.conf || {}`.
   - **Problem:** A function that works out the next step quietly upgrades old runs, and `vocabBlock` relies on that having happened.
   - **Fix:** Upgrade an old run once, in `startPlacement`: `if (RUN && !RUN.v.conf) RUN.v.conf = {};`. Make `vocabNext` read-only.
6. **Small touch targets in the sheet (mobile).**
   - **Where:** The sheet's play button (`.play.icon`, about 31×32px) and the `.btn.small` actions (38px tall).
   - **Problem:** Both are below the 44pt iOS minimum. These are existing styles, but the sheet is used one-handed at the bottom of the screen.
   - **Fix:** Add `dialog.sheet .btn.small, dialog.sheet .play{min-height:44px}`.
7. **The keyboard doesn't come back after a lookup in a typed question (iOS).**
   - **Problem:** Tapping a prompt word blurs `#tans`, which closes the keyboard. Closing the sheet doesn't focus it again.
   - **Fix:** Add `$("gl").addEventListener("close", () => { const t = $("tans"); if (t && !t.disabled) t.focus(); });`.
8. **Two rare cases where cached files can be missing (`sw.js` and `build.py`).**
   - On a device's first visit, the page fetches its data before the service worker takes control. The data file only goes into the cache on the next online visit, so going offline right after the first visit fails.
   - `build.py` deletes the previous hashed files. A device that still has the old `index.html` in its HTTP cache (GitHub Pages caches pages for up to 10 minutes) but has lost the old data file from its service-worker cache will get a 404 and the retry screen.
   - Both are rare. If either matters, keep the previous version's hashed files for one deploy (delete files older than the last build rather than all of them).

---

## Data note (not a code finding)

With the current `/tmp/wp/pipe/passages_final.json`, `build.py` fails its own check: `g-L10-18: a target word has no card`. The passage lists `v-lambast`, but the card's id is `v-lambaste`. Fix the passage before building. One irregular form isn't bolded either: in *g-L-2-17*, "children" isn't marked for `v-child`. It is not a question target, so the guard is unaffected.
