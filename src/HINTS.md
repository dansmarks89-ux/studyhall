# Conversation hints: writing spec

The AI conversations (Talk) in Spanish, Cantonese and Korean show the learner a role-play: a title, a setup, a list of
goals, and the other person's opening line. When the learner is stuck, **Help** gives a hint for one goal in three steps:

1. **The idea** (`en`): what he could say, in natural English. "Ask her where she lives."
2. **A start** (`start`): the model sentence's first words, shown with "…". `¿Dónde…`
3. **The model sentence** (`es`, or `t` for Cantonese and Korean), with audio. `¿Dónde vives?`

The learner then says or types the sentence himself. The model sentence is shown as correct Spanish, Cantonese or
Korean to copy, so it must be **100% correct and natural**: a native speaker of the course's variety would say exactly
this, to this person, in this situation.

The learner is an American cardiologist in Chicago (beginner to intermediate). Hints are written per role-play goal.

## Files

`src/<lang>/content/hints/<level id>.json`, one per level (Spanish C1–C8, M1–M8; Cantonese and Korean L1–L10):

```json
{"roleplay": [
  {"title": "New coworker at lunch",
   "hints": [ {"en": "…", "es": "…", "start": "…"},  … one per goal, in the goals' order … ]},
  … one per role-play, in the level's order …
]}
```

- Spanish: `{"en": "Ask where she lives and how many kids she has.", "es": "¿Dónde vives? ¿Cuántos hijos tienes?", "start": "¿Dónde vives?"}`
- Cantonese: `{"en": "…", "t": ["你住喺邊度呀？", "nei5 zyu6 hai2 bin1 dou6 aa3?"], "start": "你住喺"}`. Characters and
  Jyutping; every character has one syllable with a tone number 1–6; numbers are written in characters; Latin names
  (Wing, Chicago) appear unchanged in both.
- Korean: `{"en": "…", "t": "어디에 사세요?", "start": "어디에"}`. The build adds the romanization.

Spanish also has `src/spanish/content/hints/quick.json` for the lessons' short chats, whose goal "Ask one question back"
has no role-play: `{"every": hint, "clinic": hint}` (Everyday: a friendly neighbour, tú; Clinic: a patient, usted).

`python3 src/hints_check.py <spanish|cantonese|korean>` checks the files. Every ERROR must be fixed; read every WARN.

## Rules

**The model sentence**
- It achieves the goal, as one turn the learner could say in that conversation. For a goal with two parts, give one or
  two short sentences that do both. Most models are 4–12 words; never more than 2 sentences.
- It fits the persona and setup: right register (Spanish: usted with patients, strangers and older people; tú with
  coworkers, friends and family, as the persona says; Korean: the polite -요 style unless the persona clearly calls for
  formal 합니다 style; Cantonese: colloquial Hong Kong Cantonese, not written Chinese), and nothing the learner couldn't
  know at that point. Where the goal asks the learner to tell something about himself, use plain, plausible facts for
  an American doctor in Chicago.
- It uses the level's own vocabulary and grammar, or earlier levels'. Read the level file (`grammar`/`notes`, `vocab`,
  `phrases`) and the persona's instructions, which say what the level allows (e.g. "present tense only"). Prefer the
  words and patterns the level teaches. If the goal names a structure (gustar, tener que, the preterite), use it.
- Spanish: Mexico and Central America; never vosotros or vos; correct accents and ¿ ¡. Cantonese: characters as Hong
  Kong writes them in this course (呀, 嘅, 喺, 唔, 咗, 嚟). Korean: correct spacing and particles.
- One model per goal. No alternatives, slashes, brackets or ellipses in the model.

**The start**
- The model's first words, exactly as they appear in it (a prefix), ending at a word boundary (Cantonese: a character
  boundary), without "…". Usually 1–4 words: enough to show the frame (the question word, the verb pattern), never the
  whole sentence. A one-word model (안녕하세요, ¡Gracias!, 唔該) has `"start": ""`: don't add a word just to have a start.

**The English (`en`)**
- The idea, as an instruction or suggestion in natural English ("Ask how long the pain lasts.", "Say you like running
  but not the cold."), specific enough that the model sentence is clearly one right way to say it. Not a word-for-word
  gloss, and not the goal copied unchanged when the goal is vague.

## Process

Author → a separate reviewer (who did not write it) → `hints_check.py` → a walkthrough in the app. The reviewer
returns corrections; the author's file is changed only by applying them.
