# Your job: write tap-to-define dictionary entries for Word Power

Learners tap any word in the app's definitions, examples and reading passages and see a short dictionary entry. Learners range from English beginners to advanced adults, so entries must be **accurate and written in very plain words**.

Input: the JSON array in your input file. Each item has `k` ("base word|part of speech"), `wordnet` (Princeton WordNet senses for reference — often wordy or technical; never copy their wording) and `context` (a sentence from the app where the word appears; may be empty).

For each item write 1–3 senses:
- Most common everyday sense first. The sense used in `context` MUST be included.
- Each sense: 3–14 plain words. Never use the word itself or a form of it. Never define with a harder word.
- Verbs start with "to …". Adjectives describe ("very happy and excited"). Nouns name ("a large room where ...").
- Skip rare technical or archaic senses unless the context uses them.
- If `k` is wrong — not a real English word in that part of speech, a misspelling, a fragment, a name — output an empty list for it.
- Accuracy is the top priority: if you're unsure of a sense, leave it out.

Output: ONE JSON object mapping every input `k` to its list of senses, e.g. `{"bank|noun": ["a business that keeps and lends money", "the land along the side of a river"], "brusque|adjective": ["short and rude in the way you speak"]}`. Write it to your output path (in parts if long, then combine with python3). Check it loads, has every input key, and no sense contains its own word: run `python3 /tmp/wp/gloss/check.py <input> <output>` and fix what it reports.
Reply with ONE line: `<output path>: N entries, E empty, P problems left`.
