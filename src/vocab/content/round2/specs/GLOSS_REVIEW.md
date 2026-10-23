# Your job: check tap-to-define dictionary entries (independent reviewer)

Someone else wrote these. The owner requires every entry to be correct. Read the writers' brief first: /tmp/wp/GLOSS.md.

Inputs: the writer's input batch (each item: `k` = "word|part of speech", `wordnet` reference senses, `context` sentence) and the writer's output (a JSON object: key → list of senses).

Check EVERY entry:
1. Each sense is a true, current meaning of that word in that part of speech (use `wordnet` as a reference; WebSearch any doubt). The most common sense comes first. If `context` is given, its sense is included and correct.
2. Plain words a learner understands; no harder words than the headword; does not contain the word itself; 3–14 words; verbs start "to …".
3. Not misleading by being too narrow or too broad.
4. An empty list is right only if the key is not a real word in that part of speech; if it IS real (e.g. a common word mis-split), write senses.

Output: a JSON object containing ONLY the keys you change, each mapped to its full corrected list of senses, written to your output path. Run `python3 /tmp/wp/gloss/check.py <input batch> <a merged copy of the writer's output with your changes applied>` and fix anything it reports.
Reply with: the output path, how many entries you changed, and the 3 most serious errors (one line each).
