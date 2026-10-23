# Your job: write Word Power reading passages for ONE vocabulary level

Reading practice lets learners meet words they've studied in real context and answer questions about them. Accuracy is the top priority.

## Input
`/tmp/wp/levelwords/L<level>.json` — every vocabulary card at your level: id, term, pos, def (the meaning the app teaches), forms.

## What to write
30 passages. Each passage uses exactly 6 target words from your level's list, each in **the meaning given in its `def`** (inflected forms are fine: "corroborated"). Spread your choices: use as many different words across the 30 passages as possible; no word in more than 2 passages.

Length and style:
- Levels -2 and -1 (Starter, for English learners and children): 40–70 words, short simple sentences, everyday life.
- Levels 0–2: 80–130 words.
- Levels 3–10: 110–170 words, the style of a good magazine, news feature, letter, short story scene or explanation.
- All other words in the passage should be clearly easier than the target words (for Starter passages: only very basic words).
- Varied topics and settings: work, family, school, travel, food, science, nature, sports, history, money, health, community. Varied names from many backgrounds; no stereotypes. Fiction is fine. Any real-world fact you state must be true (or keep it fictional/everyday). No partisan politics, nothing sexual or gruesome, no real living private people.
- Each target word must appear once, spelled exactly as it would be in normal text.

## Questions (exactly 3 per passage)
- 2 questions of kind `"word"`: about two different target words. `q` = `In the passage, what does “<the form used in the text>” mean?` Six `options`: the correct plain meaning **as used in this passage**, plus 5 wrong but plausible meanings (another sense of the same word, a near-miss, the opposite, a meaning that fits a careless reading). Exactly one option correct.
- 1 question of kind `"idea"`: main idea, inference, or detail that needs the passage to be understood (not a word definition). Six options, exactly one defensibly correct; the others plausible to a careless reader.
- `answer` = index 0–5 of the correct option; vary its position. `why` = 1–2 sentences explaining the right answer (and the most tempting wrong one).
- Options in plain words a learner at that level understands.

## Format: one JSON array, written to your output path
```
{"id":"g-L<level>-<nn>","track":"reading","level":<level>,"title":"<2-6 words>","text":"<passage>","words":["v-...", 6 ids],
 "qs":[{"kind":"word","word":"v-...","q":"...","options":[6 strings],"answer":2,"why":"..."},
       {"kind":"word","word":"v-...","q":"...","options":[...],"answer":0,"why":"..."},
       {"kind":"idea","q":"...","options":[...],"answer":4,"why":"..."}]}
```
`nn` = 01..30. Run `python3 /tmp/wp/validate_passages.py <output path>` and fix every PROBLEM; re-run until clean. Then SOLVE each question yourself from the passage alone, as a check.
Reply with ONE line: `<output path>: N passages, P problems left`.
