# Study Hall Cantonese — content spec (read fully before writing)

## Learners
Two American adults in Chicago, **complete beginners**, English speakers. Goal: be slightly conversational with **Hong Kong** Cantonese speakers and build everyday vocabulary. No medical content.
Learning style chosen by the learner: **sound and meaning first**. They learn by hearing a phrase, seeing it, and knowing what it means (and the reverse). Characters are shown for reference and will be read slowly over time, but nothing asks them to write or type characters. Every Cantonese string in the course is shown with Jyutping and played as audio.

## Language rules (non-negotiable)
- **Colloquial spoken Hong Kong Cantonese**, written in **Traditional characters** the way Hong Kongers write speech: 係 唔 冇 佢 嘅 咗 喺 嚟 啲 咁 嗰 呢 乜嘢 咩 點 邊度 睇 俾 食 飲 瞓 攰 靚 嘢. Never standard written Chinese or Mandarin forms (是, 不, 沒有, 他/她, 的, 了, 在, 這, 那, 什麼, 給, 看) unless that is genuinely what is said aloud (e.g. 謝謝 is NOT HK speech; use 多謝/唔該).
- Natural everyday register: polite with strangers and staff, relaxed with friends. Include the sentence-final particles real speakers use (呀 啦 喇 㗎 囉 吖 喎 嘛 啩) where natural, but never stack them artificially.
- **Jyutping** (LSHK) for every Cantonese string: lowercase, tone number 1–6 on every syllable, syllables separated by spaces, punctuation optional. Write the tone people **actually say**, including common changed tones (話 in 廣東話 = waa2, 錢 in 幾多錢 = cin2, 位 counting people = wai2, 名 in 咩名 = meng2, 嗰 = go2, 呢 = ni1). Particles: 呀 aa3, 啦 laa1, 喇 laa3, 㗎 gaa3, 囉 lo1, 吖 aa1, 喎 wo3, 嘛 maa3, 啩 gwaa3, 咩 me1 (question "what?") / me1 (surprise question particle), 呢 ne1 (question particle "and…?").
- One character = one syllable. Numbers in characters (三十五), never digits. English names (Dan) may stay in Latin letters in both the characters and the Jyutping.
- English: natural, faithful translations.
- **Every multiple-choice item has exactly ONE defensible right answer.** Cantonese often allows synonyms (多謝 vs 唔該 depends on situation; 呀 is often optional; 你 vs 你哋). Either make the context force one answer or rewrite. Distractors must be plausible to a beginner but clearly wrong to a speaker: wrong particle/aspect marker, wrong measure word, wrong question word, wrong tone-similar word (買 maai5 buy / 賣 maai6 sell; 食 sik6 eat / 識 sik1 know), wrong situation.
- **Grammar scope:** an item may only need grammar and vocabulary from its own level or earlier levels (see outline). Vocabulary from earlier levels can be reused freely; a few new words in an item are fine if they are in this level's vocab list.

## Levels (themes, what each level teaches)
L1–L6 are built around an existing, already-verified phrase bank (`bank/L1.json` … `bank/L6.json`). For those levels the vocab list **must contain every bank entry exactly as given** (copy the whole object, including "old", "topic" and "note"; do not change characters, Jyutping or English). You may add up to 10 more entries per level. If you believe a bank entry is wrong, don't edit it: report it in your reply.

- **L1 First words** (bank L1: basics, numbers): greetings, 唔該 vs 多謝, sorry/excuse me, yes/no (係/唔係, answering by repeating the verb), asking someone to repeat / slow down, numbers 0–1000 (二 vs 兩), 唔 for "not".
- **L2 People** (bank L2): pronouns and 哋 plural, 係 "to be", 叫 "be called", 喺 "at/in" vs 係, 嘅 possessive and dropping it with family (我老婆), 呢個係…, question words 咩 / 邊度 / 點 / 邊個, softening 呀, family words.
- **L3 Food and drink** (bank L3): measure words (個 杯 碗 碟 位 份 枝 樽), 要 / 想 + noun/verb, 有冇…？, 好 + adjective ("very"), 唔該 + request, 啦 for suggestions, 呢個 / 嗰個, ordering at a cha chaan teng or dim sum.
- **L4 Around town, shopping, time** (bank L4): 喺邊度, 點去, directions, 幾多錢, money (蚊), A-唔-A questions (遠唔遠, 有冇), 太…喇, 啲 for "a bit more" (平啲), telling the time (三點半, 個字 optional), 今日 / 聽日 / 尋日, days of the week (星期一…星期日).
- **L5 Small talk and likes** (bank L5): 鍾意, 緊 (ongoing action), feelings, weather, 係咪, 得唔得閒, 幾 + adjective ("pretty"), 都 "also", sentence-final particles 呀 啦 喇 㗎 (what each adds).
- **L6 Past, experience, plans** (bank L6): 咗 (done), 過 (ever done), 未 (not yet / …yet?), 會 (will), 想 / 打算, 因為…所以…, 如果…就…, 不如…啦, 覺得, 得 after a verb (講得好好), 同 "with".
- **L7 Making plans** (new): dates and days (幾號, 星期幾, 月 names, 下個禮拜 / 下星期), abilities and permission 識 / 會 / 可以 / 得, 要 "need to", 一齊, 約 (arrange to meet), phone and messaging (打電話, send WhatsApp, 覆), accepting and politely declining invitations, 遲啲 / 之前 / 之後, 先 "first".
- **L8 Daily life** (new): routine (起身, 沖涼, 返工, 放工, 食早餐 / 晏晝 / 晚飯, 煮飯, 瞓覺), frequency (每日, 成日, 有時, 好少, 間中), sequence 先…然後…, 之後, 一…就…, places at home and around (屋企, 公司, 超級市場, 街市), transport (搭巴士 / 地鐵 / 的士, 揸車, 行路).
- **L9 Describing and comparing** (new): common adjectives (高 矮 大 細 新 舊 長 短 好睇 方便 好玩 悶), colours, clothes (着 / 戴), A 比 B + adjective, 最, 一樣, 冇咁…, 好似, describing people and places, 啲 / 好多 / 少少.
- **L10 Real conversations** (new): problems and asking for help (唔見咗, 壞咗, 蕩失路, 唔舒服, 可唔可以幫…), opinions and reactions (我覺得, 係囉, 真係？, 唔係嘛, 都係), connectors 雖然…但係…, 不過, 咁, 即係, 仲, 已經, visiting and hosting (歡迎, 入嚟坐, 隨便, 唔使客氣), farewells and well-wishes (保重, 慢慢行, 下次再傾).

New levels (L7–L10): 45–55 vocab entries each, mostly whole useful phrases plus key words.

## Output: one JSON file per level
Write `levels/L<n>.json` (UTF-8). A Cantonese text is always a two-element array **`["中文", "jyut ping"]`** — called **T** below.

```json
{
  "id": "L3", "n": 3,
  "title": "Food and drink",                       // short English title
  "goal": "Order food and drinks and say what you'd like.",   // one sentence
  "notes": [                                        // 3–5 short lesson blocks
    {"h": "Measure words", "p": "Plain English. Mention Cantonese only inside tags like {{一杯茶|jat1 bui1 caa4}}.",
     "ex": [[["兩杯奶茶","loeng5 bui1 naai5 caa4"], "two milk teas"]]}
  ],
  "vocab": [ {"t": ["唔該","m4 goi1"], "en": "Thank you (for a service) / please", "topic": "Basics", "note": "", "avoid": [3]} ],
  "items": [ ... ],
  "roleplay": [ ... ]
}
```
- `notes`: explain grammar AND sound points for this level (a tone trap, a changed tone, a particle). Short and concrete; 2–4 examples each. Inside `p`, `why`, `q` (pick items) and new vocab `note`s, any Cantonese **must** be written as `{{中文|jyut ping}}`; no bare Chinese characters in prose.
- `vocab` entries: `t`, `en` (every English gloss in a level must be distinct), `topic` (short English group name), optional `note`, optional `avoid` = indices of other entries in this level that could also fit this entry's English (near-synonyms like 好 / 得 "OK"), so the app never offers them as wrong options together.

### Exercise pool (`items`) — exact counts per level: 16 gap, 8 pick, 12 tiles, 10 listen, 5 dlg
Ids: `"L3-gap-01"` … numbered per type. Every item has `"sk"`: 1–3 skill ids, the decision the learner must get right, most important first:
`g:particles` sentence-final particles · `g:aspect` 咗/緊/過/未 · `g:measure` measure words · `g:neg` 唔/冇/未 · `g:question` question words and A-唔-A · `g:order` word order · `g:numbers` numbers, money, dates · `g:time` time words · `g:modal` 想/要/識/會/可以/得 · `g:compare` 比/最/一樣 · `g:connect` connectors (因為, 所以, 如果, 但係, 先…然後) · `g:pron` pronouns, 嘅, 哋 · `g:place` 喺/去/嚟/directions · `s:tones` tells similar-sounding words apart · `s:listen` listening · `s:vocab` knowing the word · `s:phrase` choosing the socially right phrase.

Also: about one third easy, one third medium, one third hard; hard = the level's core skill, not obscure words.

`gap` — choose the word that fills the blank (4 Cantonese options):
```json
{"id":"L6-gap-01","t":"gap","q":["我食___飯喇","ngo5 sik6 ___ faan6 laa3"],"en":"I've eaten already.","opts":[["咗","zo2"],["緊","gan2"],["過","gwo3"],["未","mei6"]],"a":0,"why":"{{咗|zo2}} marks a finished action.","sk":["g:aspect"]}
```
`___` appears once in both halves of `q`; the filled sentence must be correct with exactly one option.

`pick` — a situation in English; choose what you'd say (4 Cantonese options):
```json
{"id":"L3-pick-01","t":"pick","q":"The waiter brings your tea. You say:","opts":[["唔該","m4 goi1"],["多謝晒你嘅禮物","do1 ze6 saai3 nei5 ge3 lai5 mat6"],["對唔住","deoi3 m4 zyu6"],["拜拜","baai1 baai3"]],"a":0,"why":"For a small service, {{唔該|m4 goi1}}.","sk":["s:phrase"]}
```

`tiles` — the English is shown; the learner taps word tiles to build the Cantonese:
```json
{"id":"L6-tiles-01","t":"tiles","en":"I've been to Hong Kong.","full":["我去過香港。","ngo5 heoi3 gwo3 hoeng1 gong2"],
 "a":[["我","ngo5"],["去過","heoi3 gwo3"],["香港","hoeng1 gong2"]],"alt":[],"extra":[["咗","zo2"],["緊","gan2"]],"sk":["g:aspect","g:order"]}
```
`a` = 3–8 tiles, each a word or short chunk (1–3 characters; particles are their own tile; no punctuation). Joined, they must spell `full` exactly (ignoring punctuation). `alt` = other fully correct orders using exactly the same tiles (Cantonese often allows moving time words: 聽日我去 / 我聽日去 — list them, or pick a sentence with one natural order). `extra` = 2–3 distractor tiles that fit nowhere in a correct sentence.

`listen` — the app plays `say`; the learner picks the meaning from 6 English options:
```json
{"id":"L4-listen-01","t":"listen","say":["我想買呢個","ngo5 soeng2 maai5 ni1 go3"],"opts":["I want to buy this one.","I want to sell this one.","I want that one.","I bought this one.","Do you want this one?","I don't want this one."],"a":0,"why":"{{買|maai5}} buy rises; {{賣|maai6}} sell is low and flat.","sk":["s:tones","s:listen"]}
```
`say` = a phrase or sentence of 3–12 syllables. Distractors test **listening**: tone-similar words, 咗/緊/過 aspect, negation, person, numbers. Exactly one matches.

`dlg` — a short scripted conversation; the learner chooses their replies (3 options each):
```json
{"id":"L3-dlg-01","t":"dlg","title":"At a cha chaan teng","turns":[
 {"who":"Waiter","s":["幾多位呀？","gei2 do1 wai2 aa3"],"en":"How many people?"},
 {"you":true,"opts":[["兩位，唔該","loeng5 wai2, m4 goi1"],["二位，唔該","ji6 wai2, m4 goi1"],["兩個杯","loeng5 go3 bui1"]],"a":0,"why":"Use {{兩|loeng5}} before a measure word.","sk":["g:numbers","g:measure"]},
 {"who":"Waiter","s":["飲咩呀？","jam2 me1 aa3"],"en":"What would you like to drink?"},
 {"you":true,"opts":[["唔該，一杯奶茶","m4 goi1, jat1 bui1 naai5 caa4"],["多謝，一碗奶茶","do1 ze6, jat1 wun2 naai5 caa4"],["我飲咗奶茶","ngo5 jam2 zo2 naai5 caa4"]],"a":0,"why":"…","sk":["g:measure","s:phrase"]}
]}
```
4–7 turns, first turn by the other person, 2–3 `you` turns. Names: use HK names written in English letters (Ka-yan, Wing, Mr Chan, Miss Lee, Auntie) or a role (Waiter, Driver, Shop assistant).

### Roleplay — 2 per level (practice with an AI playing a Hong Kong person; not graded)
```json
{"title":"Ordering at a cha chaan teng","setup":"English, 1–2 sentences: where you are and what you want to do.",
 "persona":"English instructions for the AI: who it plays, facts it knows, to speak simple colloquial HK Cantonese using mostly words from levels 1–3, short sentences.",
 "opening":["歡迎光臨！幾多位呀？","fun1 jing4 gwong1 lam4! gei2 do1 wai2 aa3"],"opening_en":"Welcome! How many people?",
 "goals":["Say how many people","Order a drink","Ask for the bill"]}
```

## Quality bar — before you finish
1. Run `python3 /home/claude/studyhall/src/lang/tools/check_level.py yue <your file>` and fix every ERROR. It checks the structure, counts, that every character has a Jyutping syllable, and every syllable against two Cantonese dictionaries.
2. Read every WARN. A WARN means both dictionaries would read that character differently in that spot. Fix it unless you are sure the spoken form you wrote is right (changed tones like 錢 cin2 in 幾多錢 are expected warnings).
3. Re-read every item as a Hong Kong speaker would: natural colloquial Cantonese, the right particle, the right measure word, exactly one correct option, English faithful.
