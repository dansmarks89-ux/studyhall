# Skill tagging spec

Context: /tmp/claude-0/-home-claude/9340766f-e6a4-5a54-ab18-50f2cf87ee8b/scratchpad/course/SPEC.md describes the course. Each level file `levels/<ID>.json` has an `items` list (types mc, fill, tiles, listen, dlg) and a `vocab` list. The app will track the learner's accuracy per SKILL and log the TYPE of each mistake, so it can show weak spots ("you keep using the imperfect where the preterite is needed"). Your job: tag every item. Do NOT edit the level files.

## Output
Write `levels/<ID>.tags.json`: one JSON object keyed by item id. Every item in the level must have an entry.

```json
{
  "C3-mc-01": {"sk": ["t:pret"], "vw": [4], "lem": "ir", "tn": "Preterite", "pn": 0, "oe": {}},
  "C3-mc-07": {"sk": ["g:serestar"], "vw": [], "oe": {"1": "serestar", "3": "word"}},
  "C3-fill-02": {"sk": ["t:pret", "g:irreg"], "vw": [], "lem": "tener", "tn": "Preterite", "pn": 2},
  "C3-tiles-01": {"sk": ["s:order", "t:pret"], "vw": [10]},
  "C3-listen-01": {"sk": ["s:listen", "t:pret"], "vw": [2]},
  "C3-dlg-01": {"sk": ["t:pret"], "turns": {"1": {"sk": ["t:pret"], "oe": {"1": "tense:Present", "2": "tense:Imperfect"}}, "3": {"sk": ["t:pret","g:irreg"], "oe": {"0": "tense:Future", "2": "word"}}}}
}
```

Fields:
- `sk` (required): 1–3 skill ids from the list below — what the item actually tests (the decision the learner must get right), most important first. Don't tag skills the item merely contains.
- `vw`: indices into this level's `vocab` list for vocab entries the item depends on (the learner must know the word to answer). `[]` if none. At most 3.
- `lem`, `tn`, `pn` — ONLY when the correct answer of an mc or fill item is a single conjugated verb form (or *no* + verb, or pronoun(s) + verb, e.g. "se mareó", "no se mueva", "ha tenido", "lo voy" does NOT count). `lem` = infinitive without "se" (e.g. "marear" for "se mareó", "acostar" for "acuéstese"). `tn` = one of: Present, Preterite, Imperfect, Future, Conditional, Present perfect, Pluperfect, Present subjunctive, Imperfect subjunctive, Command (+), Command (−). `pn` = person index: 0 yo, 1 tú, 2 usted/él/ella, 3 nosotros, 4 ustedes/ellos/ellas. Commands: tú = 1, usted = 2. Omit all three if the answer is not a single verb form (ir a + infinitive, infinitive, gerund, non-verb).
- `oe` (mc, and each dlg `you` turn): error code for each WRONG option index (string keys). The app auto-detects wrong options that are other forms of `lem`, but give a code for EVERY wrong option anyway. Codes:
  - `tense:<Tense>` — the option is the same verb in another tense/mood (use the tense names above, e.g. `tense:Imperfect`, `tense:Present subjunctive`). If it is also a different person, still use the tense code.
  - `person` — same verb, same tense, wrong person.
  - `serestar` — ser where estar is needed or vice versa.
  - `register` — tú form/pronoun where usted is needed or vice versa.
  - `pronoun` — wrong object/reflexive pronoun or wrong placement.
  - `agree` — wrong gender/number agreement.
  - `prep` — wrong preposition.
  - `word` — wrong word/meaning (vocabulary).
  - `question` — wrong question word.
  - `neg` — wrong negation word.
  - `infl` — infinitive or gerund where a conjugated form is needed (or vice versa).
  - `other` — anything else (e.g. the reply doesn't fit the conversation).
- dlg items: `sk` for the whole dialogue (union, ≤3), plus `turns`: keyed by the index of each `you` turn in `turns` (string), each with `sk` and `oe` (and `lem`/`tn`/`pn` only if the correct option is a single verb form — rare in dlg).

## Skill ids (use only these)
Tenses and moods:
- `t:pres` present indicative (incl. stem changes in the present when the point is the present)
- `t:pret` preterite
- `t:imp` imperfect
- `t:pvi` choosing preterite vs imperfect (tag together with t:pret or t:imp when the item contrasts them)
- `t:fut` simple future
- `t:ira` ir a + infinitive
- `t:cond` conditional
- `t:pperf` present perfect
- `t:plup` pluperfect
- `t:psub` present subjunctive (incl. choosing subjunctive vs indicative after a trigger)
- `t:isub` imperfect subjunctive
- `t:si` si clauses (real vs hypothetical)
- `t:cmd` commands (usted/tú, affirmative/negative, pronoun attachment)
- `t:prog` estar/seguir + gerund
Grammar:
- `g:serestar` ser vs estar
- `g:gustar` gustar/doler/encantar/importar/faltar pattern (indirect object verbs)
- `g:reflex` reflexive verbs (me levanto, se mareó)
- `g:objpron` object pronouns and their placement (lo, la, le, se lo, attached vs before)
- `g:agree` gender/number agreement (articles, adjectives, possessives)
- `g:questions` question words
- `g:neg` negation (no, nunca, nada, nadie, tampoco)
- `g:compare` comparisons
- `g:time` time expressions (hace…que, desde hace, llevar + time, acabar de, hace + time = ago)
- `g:connect` connectors (porque, pero, entonces, así que, cuando, mientras, aunque…)
- `g:register` tú vs usted register
- `g:irreg` irregular verb forms (when knowing the irregular form is the point)
- `g:person` verb endings / person agreement
- `g:prep` prepositions
Skills:
- `s:listen` listening comprehension (all listen items get this first)
- `s:order` building a sentence / word order (all tiles items get this first)
- `s:vocab` knowing what a word/phrase means (items that test meaning, not grammar)
- `s:phrase` choosing the natural/appropriate phrase for a situation (conversational or clinical pragmatics)

## Checks (run in Python before finishing)
- valid JSON; every item id of the level present; no extra ids
- every `sk` non-empty, ≤3, all ids from the list
- `tn` in the 11 tense names; `pn` in 0–4; `lem` lowercase infinitive ending in -ar/-er/-ir
- every mc item has an `oe` code for every wrong option index; every dlg `you` turn has `turns[<index>]` with `oe` for every wrong option
- `vw` indices within the level's vocab list
