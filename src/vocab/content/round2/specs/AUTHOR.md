# Your job: write Word Power vocabulary cards

1. Read the full spec: /tmp/wp/SPEC.md (main spec + ADDENDUM — the addendum wins where they differ). Accuracy is the top priority: the owner requires every definition, example and fact to be correct.
2. Look at the first 3 items in /tmp/wp/raw_old/vocab-L5_a.json to see the exact JSON format.
3. Your candidate list is the file named in your task (one word per line: word, dictionary parts of speech n/v/a/r, frequency). Choose words ONLY from it. The `level` field of every card = your level number. `pos` must be one of the listed parts of speech for that word.
4. Write the cards as one JSON array to the output path in your task (write in two or three parts if long, then combine into that single file with python3; the final file must be a single valid JSON array).
5. Run `python3 /tmp/wp/validate.py <output path>` and fix every PROBLEM; fix plain-word warnings unless a plainer accurate wording truly does not exist. Re-run until clean.
6. Reply with ONE line only: `<output path>: N cards, P problems, W warnings left`. Do not include card contents in your reply.
