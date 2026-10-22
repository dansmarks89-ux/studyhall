# Word Power — content spec (Study Hall vocabulary & knowledge app)

The learners are adults who speak English (American English). The app is **primarily a vocabulary builder**. Secondary tracks build idioms, cultural references, general knowledge, word roots and reasoning. Every card is studied, then **tested** later with multiple choice (6 options), fill-in-the-blank sentences, and typed answers. Accuracy matters more than anything: the owner requires every fact to be correct. If you are not certain something is true, leave it out.

Output: a JSON **array** of items, written with the Write tool to the exact path you are given. Valid JSON only (double quotes, no comments, no trailing commas). Use straight ASCII quotes `"` for JSON and typographic apostrophes are fine inside strings. Write in chunks if needed (e.g. `..._a.json`, `..._b.json`) — each file a complete array.

## Fields used by every item

| field | rule |
|---|---|
| `id` | unique, lowercase, `<prefix>-<slug>`: vocab `v-`, roots `r-`, idioms `i-`, refs `f-`, knowledge `k-`, reasoning concepts `c-`, reasoning problems `p-`. Slug = term in lowercase, spaces→`-`, drop punctuation. |
| `track` | `vocab` · `roots` · `idioms` · `refs` · `knowledge` · `reasoning` |
| `level` | integer (ranges per track below) |
| `term` | the word/phrase exactly as it is normally written |
| `def` | learner-friendly definition, **6–22 words**, plain English, the most common sense. It must **not** contain the term or an obvious form of it (no "candidly" in the definition of "candid"), so multiple choice is not a giveaway. Do not start with "To" for verbs — write "to ..." lowercase is fine. Never vague ("a kind of thing"). It must distinguish this term from close neighbors. |
| `ex` | exactly **2** example sentences, 8–25 words each, natural modern usage, each containing the term (an inflected form is fine for vocab). Varied settings: work, home, news, school, sports, health, travel, money, relationships. |
| `cloze` | `{"s": "...___...", "a": "..."}` — a **third, different** sentence with `___` where the answer goes, and `a` = the exact text that fills the blank (may be inflected: "corroborated"). The sentence's context must make the meaning clear enough that a reader who knows the word could pick it from 6 same-type options, and **only this term** fits sensibly. Exactly one `___`. |
| `syn` | 0–4 true synonyms in this sense (array of strings). Only genuine synonyms. |
| `ant` | 0–3 antonyms (array, may be empty) |
| `note` | optional, ≤ 30 words: connotation (positive/negative/formal), a common mistake, or a commonly confused word ("Not the same as *flout*, which means ..."). Omit if nothing useful. |

## Track: vocab (field `pos` required; `forms` optional)
- `pos`: `noun` · `verb` · `adjective` · `adverb`. The sense you define must match `pos`.
- `forms`: optional, up to 3 common related forms, e.g. `["obsequiously (adverb)", "obsequiousness (noun)"]`. Only forms that genuinely exist and are in use.
- **Choose words only from the band file you are given** (one word per line: word, WordNet parts of speech, frequency). Pick words genuinely worth knowing for reading news, books, work and conversation. Exclude: proper nouns and names, specialist jargon (medical, chemical, legal-technical, computing), slang, offensive or slur words, British-only spellings, plain inflections ("walked") when the base form is the useful entry, archaic words, and words nearly every adult already knows from childhood ("table"). Prefer words where learning them adds expressive or comprehension power. Mix parts of speech (roughly half adjectives+verbs, a third nouns, some adverbs).
- If a word has several common senses, teach the most common one, and you may add `"also": "short note of a second common sense"`.

## Track: roots (levels 1–3)
Items are prefixes, roots and suffixes from Latin/Greek/Old English that unlock many English words.
- `term`: e.g. `"bene-"`, `"chron"`, `"-phobia"` (use hyphens to show attachment).
- `type`: `prefix` · `root` · `suffix`; `origin`: `Latin` · `Greek` · `Old English` · `French`.
- `def`: its meaning (e.g. "good, well").
- `words`: exactly 4 objects `{"w": "benefit", "m": "an advantage or something good that you get"}` — common English words that **really** contain this element **with this meaning** (no false friends: "pediatric" is Greek *paid-* child, not Latin *ped-* foot). 
- No `ex`/`cloze` needed for roots. Level 1 = most productive/common (pre-, re-, un-, -able), 3 = advanced (-cracy, philo, -phile).

## Track: idioms (levels 1–5)
Idioms, set phrases, phrasal expressions and foreign phrases used in English.
- `kind`: `idiom` · `phrase` · `foreign`; for foreign also `lang` ("Latin", "French", ...).
- `register`: `informal` · `neutral` · `formal`.
- `origin`: optional, ≤ 30 words, ONLY if the origin is well documented; if commonly told stories are disputed or false, either omit or say "Origin uncertain." Never repeat a folk etymology.
- `cloze.a` is the full idiom text that fills the blank (other idioms will be the wrong options).
- Level 1 = everyday, heard weekly by most adults ("break the ice"); 3 = common in news/business writing ("moot point", "status quo"); 5 = educated/literary ("hoist with one's own petard", "pyrrhic" belongs to refs instead).

## Track: refs (levels 1–5)
Allusions and cultural references that English speakers use as shorthand: "Achilles' heel", "Pandora's box", "Catch-22", "Orwellian", "crossing the Rubicon", "Kafkaesque", "the emperor's new clothes".
- `source`: one of `Greek & Roman myth` · `Norse & other myth` · `Bible & religious texts` · `Shakespeare` · `Literature` · `Folk tales & fables` · `History` · `Science & medicine` · `Film, TV & media` · `People (eponyms)`.
- `story`: 1–3 sentences: the original story/event/person and how it gave the phrase its meaning. Must be factually correct.
- `def`: what people mean when they use it today.
- Be inclusive: draw from many cultures' stories **that actually appear in English-language usage** (e.g. "nirvana", "karma", "yin and yang", "Mecca of ...", "Rashomon effect", "Shangri-La", "Aesop", "Arabian Nights / open sesame"), alongside the Greco-Roman, Biblical, Shakespearean and literary canon.
- Level 1 = widely understood ("Achilles' heel"), 5 = rarer ("Procrustean", "Cassandra" is ~3).

## Track: knowledge (levels 1–5)
Core concepts an informed adult is expected to know — framed as **terms** so the app stays vocabulary-centred.
- `domain`: one of `Science` · `Health & body` · `Math & numbers` · `Technology` · `History` · `Government & law` · `Economics & money` · `Geography & earth` · `Arts & culture` · `Philosophy & ideas`.
- `def`: what it is; `why`: one sentence on why it matters or where you meet it.
- Only stable facts: no current office-holders, no figures that change yearly, no contested political claims. Neutral, non-partisan wording.
- Level 1 = basic adult literacy ("inflation", "photosynthesis", "Constitution"), 5 = well-read ("opportunity cost" ~2, "habeas corpus" ~3, "Pareto principle" ~4, "epistemology" ~5).

## Track: reasoning — concepts (levels 1–3, id prefix `c-`)
Fallacies, cognitive biases, logic and evidence ideas: straw man, ad hominem, false dilemma, slippery slope, confirmation bias, sunk cost fallacy, correlation vs. causation, base rate neglect, survivorship bias, sample size, anchoring, availability heuristic, Occam's razor, burden of proof, necessary vs. sufficient, etc.
- `kind`: `fallacy` · `bias` · `logic` · `evidence`.
- `def`; `scenario`: a 1–3 sentence everyday example that illustrates it; `fix`: one sentence on how to spot or counter it.
- `tests`: exactly 2 NEW short scenarios (1–3 sentences each, different from `scenario`) that each clearly show this concept and **no other concept more strongly**: `[{"s": "..."}, {"s": "..."}]`. The app asks "Which reasoning problem does this show?" with other concepts as wrong options, so the scenario must be unambiguous.
- No `ex`/`cloze` needed.

## Track: reasoning — problems (levels 1–3, id prefix `p-`)
Self-contained practice questions that train understanding language and solving problems.
- `kind`: `analogy` (word relationships, A:B :: C:?) · `context` (work out an unfamiliar real word's meaning from a sentence) · `inference` (what must be true / best supported by a short passage) · `logic` (if–then, all/some, necessary vs. sufficient) · `relationship` (which word is the opposite / most similar / odd one out).
- `q`: the question (passage included); `options`: exactly 6 strings; `answer`: index 0–5 of the single correct option (vary the position!); `why`: 1–2 sentence explanation of why it is right and why the most tempting wrong option is wrong.
- Exactly one option must be defensibly correct. Wrong options should be plausible to a careless reader.
- `term`: a short label for the problem (e.g. "Analogy: surgeon : scalpel").

## Style and inclusion
- American English spelling and usage.
- People in examples: varied names from many backgrounds (e.g. Maria, Kwame, Priya, Wei, Aisha, Diego, Hannah, Tomás, Yuki, Malik, Fatima, Liam, Olga, Jamal, Sofia), mixed genders, varied ages, roles and settings. No stereotypes (don't pair groups with jobs or traits that reinforce clichés).
- No partisan politics, no real living private individuals, nothing sexual or gratuitously violent. Mention real public figures only in established references (Machiavelli, Orwell).
- Each example sentence should show the meaning, not just contain the word ("She was candid about her mistakes, admitting them all in the meeting" — good; "Candid is a word" — bad).
- Every claim must be true. When unsure, cut it.
