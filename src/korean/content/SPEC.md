# Study Hall Korean — content spec (read fully before writing)

## Learners
Two American adults in Chicago, **complete beginners**, English speakers, learning to read Hangul. Goal: be slightly conversational and build everyday vocabulary. No medical content.
Learning style: hear a phrase, read it in Hangul, know what it means, and the reverse. Nothing asks them to type Korean. Every Korean string is shown in Hangul with a romanization and a "said like" line (generated automatically), and played as audio.

## Language rules (non-negotiable)
- Standard Seoul Korean, natural everyday speech.
- **Polite style (해요체, -요 endings) for everything the learner says and for most of what others say.** Fixed formal phrases stay formal because that is how everyone says them: 감사합니다, 죄송합니다, 잘 먹겠습니다, 잘 먹었습니다, 처음 뵙겠습니다, 어서 오세요. Staff may use -습니다/-세요 forms. No 반말 (casual speech) from the learner. Use 저/제 (not 나/내) for "I/my".
- Honorific -시- where Koreans naturally use it toward the listener or a respected person (가세요, 하세요, 이세요, 어떻게 오셨어요?). Don't overuse it about yourself.
- Hangul only, standard spelling and spacing (띄어쓰기): 할 수 있어요, 먹을 거예요, 한국 사람, 좋아해요. Numbers in Hangul words when they are spoken words (세 시, 오천 원); digits only where Koreans would write digits and you also give the Hangul nowhere else (prefer Hangul words).
- English: natural, faithful translations.
- **Every multiple-choice item has exactly ONE defensible right answer.** Korean allows variation (subject drop, 은/는 vs 이/가 in some contexts, word order of time/place words, 고마워요 vs 감사합니다). Make the context force one answer or rewrite. Distractors must be plausible to a beginner but clearly wrong to a speaker: wrong particle, wrong ending/tense, wrong number system (native vs Sino-Korean), wrong counter, wrong honorific level, wrong situation.
- **Grammar scope:** an item may only need grammar and vocabulary from its own level or earlier levels (see outline). Earlier vocabulary can be reused freely.

## Levels (themes, what each level teaches)
L1–L6 are built around an existing, already-checked phrase bank (`bank/L1.json` … `bank/L6.json`). For those levels the vocab list **must contain every bank entry exactly as given** (copy the whole object including "old", "topic", "note" and "pron" if present; don't change the Hangul or English). You may add up to 10 more entries per level. If you think a bank entry is wrong, don't edit it: report it in your reply.

- **L1 First words** (bank L1): greetings, 감사합니다 vs 고마워요, 죄송합니다 vs 미안해요, 네 / 아니요, 안녕히 가세요 vs 안녕히 계세요, asking to repeat / slow down, Sino-Korean numbers (일 이 삼 … 백 천 만) and native numbers 1–10 (하나 둘 셋 …), 주세요.
- **L2 People** (bank L2): 저 / 제, noun + 이에요/예요 and 아니에요, topic 은/는, 이름이 뭐예요?, 에서 왔어요, 사람, jobs, family words, 이 / 그 / 저.
- **L3 Food and drink** (bank L3): 주세요 / 좀, 있어요 / 없어요, object 을/를, counters with native numbers (한 개, 두 명, 세 잔, 네 병; 하나→한, 둘→두, 셋→세, 넷→네), 맛있어요 / 맛없어요, 안 + verb, 뭐, -ㄹ래요 for "would you like to / I'll have".
- **L4 Around town, shopping, time** (bank L4): 어디예요?, 에 (at/to), (으)로 (toward, by), 여기 / 거기 / 저기, 얼마예요?, 원 and money (Sino-Korean), time (native hours + Sino-Korean minutes: 세 시 삼십 분, 반), 오늘 / 내일 / 어제, days of the week (월요일 … 일요일), -고 싶어요, 비싸요 / 싸요.
- **L5 Small talk and likes** (bank L5): 좋아해요 vs 좋아요, subject 이/가 vs topic 은/는 (simple contrast), weather (더워요 / 추워요 and the ㅂ→워 change), -고 있어요 (doing now), -네요, 재미있어요 / 재미없어요, 시간 있어요?, 도 "also".
- **L6 Past and future** (bank L6): past -았/었/했어요, future -(으)ㄹ 거예요, -아서/어서 "so / because", -(으)면 "if", -아/어 본 적 있어요, -(으)ㄹ까요? "shall we", 못 "can't", -러 가요 "go to (do)".
- **L7 Making plans** (new): dates (몇 월 며칠, 월 names, 이번 주 / 다음 주 / 주말), -(으)ㄹ 수 있어요 / 없어요, -(으)ㄹ게요 "I'll (promise)", 같이, 약속, inviting and declining politely (미안해요, 다음에 같이 가요), phone and messages (전화하다, 문자 / 카톡 보내다, 답장), 언제, 몇 시에, -기로 했어요 "decided to".
- **L8 Daily life** (new): routine verbs (일어나다, 씻다, 출근하다, 퇴근하다, 아침/점심/저녁을 먹다, 요리하다, 자다), frequency (매일, 자주, 가끔, 보통, 별로 안), -고 "and then", -기 전에 "before", -(으)ㄴ 후에 "after", 에 vs 에서 (place of an action), 부터 / 까지, 쯤, transport (버스 / 지하철 / 택시를 타다, 운전하다, 걸어가다).
- **L9 Describing and comparing** (new): adjectives and the noun-modifier form (큰 집, 맛있는 음식, 좋은 사람), colours, clothes (입다 / 신다 / 쓰다), A보다 B가 더 …, 제일, 같아요 / 달라요, 처럼, describing people (키가 커요, 머리가 길어요) and places, 많이 / 조금.
- **L10 Real conversations** (new): problems and asking for help (잃어버렸어요, 고장 났어요, 길을 잃었어요, 몸이 안 좋아요, 도와주세요), -아야/어야 돼요 "have to", -지만 "but", -는데 (background, softening), 그래서 / 그런데 / 그러면, opinions -(으)ㄴ/는 것 같아요 and 생각해요, reactions (맞아요, 그렇죠, 진짜요?, 아, 그래요?), phone (여보세요), visiting a home (어서 오세요, 들어오세요, 편하게 앉으세요), farewells (조심히 가세요, 다음에 또 봐요).

New levels (L7–L10): 45–55 vocab entries each, mostly whole useful phrases plus key words.

## Output: one JSON file per level
Write `levels/L<n>.json` (UTF-8). A Korean text is a plain Hangul string — called **T** below.

```json
{
  "id": "L3", "n": 3,
  "title": "Food and drink", "goal": "Order food and drinks and count things.",
  "notes": [ {"h": "Counting with native numbers", "p": "Plain English. Mention Korean only inside tags like {{두 명}}.", "ex": [["커피 두 잔 주세요", "Two coffees, please."]]} ],
  "vocab": [ {"t": "물", "en": "water", "topic": "Food", "note": "", "avoid": []} ],
  "items": [ ... ],
  "roleplay": [ ... ],
  "pron": { }
}
```
- `notes`: 3–5 short lesson blocks explaining this level's grammar AND sound points (a sound change, a spelling-vs-speech trap). 2–4 examples each. Inside `p`, `why`, `q` (pick items) and new vocab `note`s, Korean **must** be inside `{{…}}`; no bare Hangul in prose.
- `vocab` entries: `t`, `en` (every English gloss in a level must be distinct), `topic`, optional `note`, optional `avoid` = indices of other entries in this level that could also fit this entry's English (e.g. 고마워요 / 감사합니다), so the app never offers them together as options.
- `pron`: corrections to the automatic "said like" line, as `{"exact Korean text": "how it is pronounced, in Hangul"}`. See the quality bar.

### Exercise pool (`items`) — exact counts per level: 16 gap, 8 pick, 12 tiles, 10 listen, 5 dlg
Ids `"L3-gap-01"` … numbered per type. Every item has `"sk"`: 1–3 skill ids, the decision the learner must get right, most important first:
`g:particles` 은/는 이/가 을/를 에 에서 도 (으)로 · `g:endings` polite verb endings and their forms (-아요/어요, irregulars) · `g:tense` past / future / -고 있어요 · `g:neg` 안 / 못 / 아니에요 / 없어요 · `g:numbers` native vs Sino-Korean, money, time, dates · `g:counters` 개 명 잔 병 살 번 · `g:question` question words · `g:order` word order · `g:connect` -고 -아서 -지만 -는데 -(으)면 그래서 그런데 · `g:honor` -시-, 저/제, polite vs formal phrases · `g:want` -고 싶어요 -(으)ㄹ래요 -(으)ㄹ까요 -(으)ㄹ게요 -(으)ㄹ 수 있어요 -아야 돼요 · `g:place` 여기/거기/저기, directions · `g:compare` 보다 / 제일 / 같아요 · `s:listen` listening · `s:vocab` knowing the word · `s:phrase` choosing the socially right phrase · `s:read` reading Hangul.

About one third easy, one third medium, one third hard; hard = the level's core skill.

`gap` — choose what fills the blank (4 Korean options):
```json
{"id":"L3-gap-01","t":"gap","q":"커피 ___ 잔 주세요.","en":"Two coffees, please.","opts":["두","이","둘","두 개"],"a":0,"why":"Counters take native numbers, and {{둘}} shortens to {{두}}.","sk":["g:numbers","g:counters"]}
```
`___` appears once (it may stand for a particle attached to a word: `"물___ 주세요"` with options `"좀"`… only if the filled sentence is spelled correctly; for particles prefer `"저___ 미국 사람이에요"` with options `"는","를","에","도"`). The filled sentence must be correct with exactly one option.

`pick` — situation in English; choose what you'd say (4 Korean options):
```json
{"id":"L1-pick-01","t":"pick","q":"You're leaving a shop and the owner stays. You say:","opts":["안녕히 계세요","안녕히 가세요","안녕하세요","잘 먹겠습니다"],"a":0,"why":"{{안녕히 계세요}} is said by the person leaving to the person staying.","sk":["s:phrase"]}
```

`tiles` — the English is shown; the learner taps word tiles to build the Korean:
```json
{"id":"L4-tiles-01","t":"tiles","en":"I want to go to Korea.","full":"한국에 가고 싶어요.","a":["한국에","가고","싶어요"],"alt":[],"extra":["한국을","갔어요"],"sk":["g:want","g:particles"]}
```
`a` = 2–7 tiles = the space-separated words of `full`, in order (particles stay attached, as written). Joined they must spell `full` exactly (ignoring spaces and punctuation). `alt` = other fully correct orders with the same tiles (Korean lets time and place words move: 내일 저는 가요 / 저는 내일 가요 — list them, or choose a sentence with one natural order). `extra` = 2–3 distractor tiles (wrong particle, wrong ending) that fit nowhere.

`listen` — the app plays `say`; the learner picks the meaning from 6 English options:
```json
{"id":"L6-listen-01","t":"listen","say":"어제 친구를 만났어요.","opts":["I met a friend yesterday.","I'll meet a friend tomorrow.","I'm meeting a friend now.","My friend met me yesterday.","I didn't meet my friend yesterday.","I met a friend today."],"a":0,"sk":["s:listen","g:tense"]}
```
`say` 2–10 words. Distractors test **listening**: tense endings, negation, particles (who did what), numbers, similar-sounding words (싸요 / 사요, 불 / 풀 / 뿔). Exactly one matches.

`dlg` — short scripted conversation; the learner chooses replies (3 options each):
```json
{"id":"L3-dlg-01","t":"dlg","title":"At a café","turns":[
 {"who":"Barista","s":"어서 오세요. 뭐 드릴까요?","en":"Welcome. What can I get you?"},
 {"you":true,"opts":["아이스 아메리카노 한 잔 주세요.","아이스 아메리카노 일 잔 주세요.","아이스 아메리카노 한 잔 있어요."],"a":0,"why":"Counters take native numbers: {{한 잔}}.","sk":["g:counters"]},
 {"who":"Barista","s":"여기서 드세요?","en":"For here?"},
 {"you":true,"opts":["아니요, 가져갈게요.","아니요, 가져갔어요.","네, 가져갈게요."],"a":0,"why":"…","sk":["g:want","s:phrase"]}
]}
```
4–7 turns, first turn by the other person, 2–3 `you` turns. Names: Korean names in English letters (Minji, Junho, Ms Kim, Mr Park) or a role (Barista, Driver, Shop owner).

### Roleplay — 2 per level (practice with an AI playing a Korean person; not graded)
```json
{"title":"At a café","setup":"English, 1–2 sentences.","persona":"English instructions for the AI: who it plays, facts it knows, to speak simple polite Korean using mostly words from levels 1–3.",
 "opening":"어서 오세요. 뭐 드릴까요?","opening_en":"Welcome. What can I get you?","goals":["Order a drink","Say how many","Ask how much it is"]}
```

## Quality bar — before you finish
1. Run `python3 /home/claude/studyhall/src/lang/tools/check_level.py ko <your file> --pron` and fix every ERROR.
2. The `--pron` output lists every Korean string with its automatic "said like" form and romanization (lines marked `~` differ from the spelling). Read every line. It shows natural connected speech: linking (먹어요 → 머거요), nasal changes (합니다 → 함니다, 밥 먹어요 → 밤 머거요), tensing (학교 → 학꾜, 올 거예요 → 올 꺼예요, 한국 사람 → 한국 싸람). Known gaps in the tool: it misses tensing after the endings -(으)ㄹ게요 / -(으)ㄹ걸 / -(으)ㄹ수록 (할게요 is said 할께요), and ㄴ-insertion (십육 → 심뉵, 무슨 일 → 무슨 닐, 한국 요리 → 한궁 뇨리). It sometimes moves ㅎ-aspiration across a word gap (아직 한국어 → 아지 칸구거); keep word boundaries in that case (아직 한구거). Add a `pron` entry for every line that is wrong.
3. Re-read every item as a Korean speaker would: natural, correct particles and endings, correct spacing, the right politeness, exactly one correct option, faithful English.
