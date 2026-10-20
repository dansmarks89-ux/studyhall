# Vocabulary examples — spec

Read /tmp/claude-0/-home-claude/9340766f-e6a4-5a54-ab18-50f2cf87ee8b/scratchpad/course/SPEC.md first (register, accuracy and grammar-scope rules all apply).

For each assigned level `<ID>`, read `levels/<ID>.json` and write `levels/<ID>.vx.json`: a JSON array with exactly one object per entry of that level's `vocab` list, in the same order.

```json
[
  {"i": 0, "w": "anoche", "ex": "Anoche me dolió mucho el pecho.", "en": "Last night my chest hurt a lot.", "hit": "Anoche", "note": "", "type": ["anoche"]}
]
```

- `i`: index in the level's `vocab` list. `w`: the vocab entry's Spanish text, copied exactly.
- `ex`: one natural example sentence (5–14 words) that uses this word or phrase in a typical, everyday way. Grammar must stay within this level or earlier levels of the same track (medical levels: up to their `bestAfter` conversation level). Medical levels: clinician ↔ patient context, clinician uses usted. Conversation levels: everyday situations, tú with friends/family, usted with strangers/elders. Latin American usage, no vosotros. Make the sentence show the meaning (context should help a learner guess the word).
- `en`: faithful, natural English translation.
- `hit`: the exact substring of `ex` that is the target word as it appears in the sentence (may be an inflected form, e.g. vocab "doler" → hit "dolió"; vocab "la presión arterial" → hit "presión arterial"). It must occur in `ex` exactly once. The app blanks it out for "fill the example" questions, so the rest of the sentence plus the English must make it the only sensible answer.
- `note`: optional, ≤ 18 words of English: gender if not obvious, false friends (embarazada ≠ embarrassed), regional variants, register. Empty string if nothing useful.
- `type`: every acceptable answer if the learner is shown the English meaning and must type the Spanish. Include the form with and without the article for nouns ("el pecho", "pecho"), common synonyms that the English also fits ONLY if they are genuinely equivalent, and accent-correct spellings only. Use `[]` (not typeable) when the entry is a pair or contrast ("alto / bajo"), a grammar label ("saber (preterite)"), or a phrase longer than 4 words.

Checks before you finish (run them in Python): valid JSON; length equals the level's vocab length; `w` matches `vocab[i][0]` exactly; `hit` occurs in `ex` exactly once; no empty `ex`/`en`. Then proofread every Spanish sentence for accents, ¿¡, agreement, tense, register and naturalness.
